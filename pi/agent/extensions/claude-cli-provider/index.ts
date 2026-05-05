import { spawn } from "node:child_process";
import { createInterface } from "node:readline";
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import {
  type Api,
  type AssistantMessage,
  type AssistantMessageEventStream,
  type Context,
  createAssistantMessageEventStream,
  type Message,
  type Model,
  type SimpleStreamOptions,
  type StopReason,
} from "@mariozechner/pi-ai";

type ClaudeCliApi = Api;

type ClaudeStreamJson =
  | { type: "stream_event"; event: AnthropicLikeStreamEvent }
  | { type: "result"; is_error?: boolean; result?: string; stop_reason?: string; usage?: ClaudeCliUsage }
  | { type: string; [key: string]: unknown };

type AnthropicLikeStreamEvent =
  | { type: "message_start"; message: { usage?: AnthropicLikeUsage } }
  | { type: "content_block_start"; index: number; content_block: { type: string } }
  | { type: "content_block_delta"; index: number; delta: { type: string; text?: string; thinking?: string; signature?: string } }
  | { type: "content_block_stop"; index: number }
  | { type: "message_delta"; delta?: { stop_reason?: string | null }; usage?: AnthropicLikeUsage }
  | { type: "message_stop" }
  | { type: string; [key: string]: unknown };

type AnthropicLikeUsage = {
  input_tokens?: number;
  output_tokens?: number;
  cache_read_input_tokens?: number;
  cache_creation_input_tokens?: number;
};

type ClaudeCliUsage = {
  input_tokens?: number;
  output_tokens?: number;
  cache_read_input_tokens?: number;
  cache_creation_input_tokens?: number;
};

type StreamBlock =
  | { type: "text"; text: string; cliIndex: number }
  | { type: "thinking"; thinking: string; thinkingSignature?: string; cliIndex: number };

const PROVIDER_NAME = "claude-cli";

export default function (pi: ExtensionAPI) {
  pi.registerProvider(PROVIDER_NAME, {
    name: "Claude CLI",
    baseUrl: "cli://claude",
    api: "claude-cli" as Api,
    apiKey: "claude-cli-local-auth",
    models: [
      model("haiku", "Claude CLI Haiku"),
      model("sonnet", "Claude CLI Sonnet"),
      model("opus", "Claude CLI Opus"),
    ],
    streamSimple: streamClaudeCli,
  });
}

function model(id: string, name: string) {
  return {
    id,
    name,
    reasoning: true,
    input: ["text" as const],
    cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
    contextWindow: 200000,
    maxTokens: 32000,
  };
}

function streamClaudeCli(
  model: Model<ClaudeCliApi>,
  context: Context,
  options?: SimpleStreamOptions,
): AssistantMessageEventStream {
  const stream = createAssistantMessageEventStream();

  void (async () => {
    const output: AssistantMessage = {
      role: "assistant",
      content: [],
      api: model.api,
      provider: model.provider,
      model: model.id,
      usage: {
        input: 0,
        output: 0,
        cacheRead: 0,
        cacheWrite: 0,
        totalTokens: 0,
        cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0 },
      },
      stopReason: "stop",
      timestamp: Date.now(),
    };

    try {
      stream.push({ type: "start", partial: output });
      await runClaudeCli(model.id, renderPrompt(context), output, stream, options);
      stream.push({ type: "done", reason: output.stopReason as "stop" | "length" | "toolUse", message: output });
      stream.end();
    } catch (error) {
      output.stopReason = options?.signal?.aborted ? "aborted" : "error";
      output.errorMessage = error instanceof Error ? error.message : String(error);
      stream.push({ type: "error", reason: output.stopReason, error: output });
      stream.end();
    }
  })();

  return stream;
}

async function runClaudeCli(
  modelId: string,
  prompt: string,
  output: AssistantMessage,
  stream: AssistantMessageEventStream,
  options?: SimpleStreamOptions,
): Promise<void> {
  const { ANTHROPIC_API_KEY: _anthropicApiKey, ...env } = process.env;
  const child = spawn(
    "claude",
    [
      "-p",
      "--model",
      modelId,
      "--output-format",
      "stream-json",
      "--verbose",
      "--include-partial-messages",
      "--tools",
      "",
      "--strict-mcp-config",
      "--mcp-config",
      '{"mcpServers":{}}',
      "--no-session-persistence",
    ],
    { env, stdio: ["pipe", "pipe", "pipe"], signal: options?.signal },
  );

  child.stdin.end(prompt);

  let stderr = "";
  child.stderr.setEncoding("utf8");
  child.stderr.on("data", (chunk: string) => {
    stderr += chunk;
  });

  const blocks = output.content as StreamBlock[];
  const lineReader = createInterface({ input: child.stdout });

  for await (const line of lineReader) {
    if (!line.trim()) continue;
    handleClaudeCliLine(JSON.parse(line) as ClaudeStreamJson, output, blocks, stream);
  }

  await new Promise<void>((resolve, reject) => {
    child.on("error", reject);
    child.on("close", (code, signal) => {
      if (code === 0) resolve();
      else reject(new Error(`Claude CLI exited ${code ?? signal}: ${stderr.slice(0, 4000)}`));
    });
  });
}

function handleClaudeCliLine(
  line: ClaudeStreamJson,
  output: AssistantMessage,
  blocks: StreamBlock[],
  stream: AssistantMessageEventStream,
): void {
  if (line.type === "result") {
    if (line.is_error) throw new Error(`Claude CLI returned an error result: ${JSON.stringify(line)}`);
    if (line.stop_reason) output.stopReason = mapStopReason(line.stop_reason);
    if (line.usage) updateUsage(output, line.usage);
    return;
  }

  if (line.type !== "stream_event") return;
  const event = line.event;

  if (event.type === "message_start") {
    if (event.message.usage) updateUsage(output, event.message.usage);
    return;
  }

  if (event.type === "content_block_start") {
    if (event.content_block.type === "text") {
      blocks.push({ type: "text", text: "", cliIndex: event.index });
      stream.push({ type: "text_start", contentIndex: blocks.length - 1, partial: output });
    } else if (event.content_block.type === "thinking") {
      blocks.push({ type: "thinking", thinking: "", thinkingSignature: "", cliIndex: event.index });
      stream.push({ type: "thinking_start", contentIndex: blocks.length - 1, partial: output });
    }
    return;
  }

  if (event.type === "content_block_delta") {
    const contentIndex = blocks.findIndex((block) => block.cliIndex === event.index);
    const block = blocks[contentIndex];
    if (!block) return;

    if (event.delta.type === "text_delta" && block.type === "text") {
      const delta = event.delta.text ?? "";
      block.text += delta;
      stream.push({ type: "text_delta", contentIndex, delta, partial: output });
    } else if (event.delta.type === "thinking_delta" && block.type === "thinking") {
      const delta = event.delta.thinking ?? "";
      block.thinking += delta;
      stream.push({ type: "thinking_delta", contentIndex, delta, partial: output });
    } else if (event.delta.type === "signature_delta" && block.type === "thinking") {
      block.thinkingSignature = `${block.thinkingSignature ?? ""}${event.delta.signature ?? ""}`;
    }
    return;
  }

  if (event.type === "content_block_stop") {
    const contentIndex = blocks.findIndex((block) => block.cliIndex === event.index);
    const block = blocks[contentIndex];
    if (!block) return;
    delete (block as { cliIndex?: number }).cliIndex;

    if (block.type === "text") {
      stream.push({ type: "text_end", contentIndex, content: block.text, partial: output });
    } else {
      stream.push({ type: "thinking_end", contentIndex, content: block.thinking, partial: output });
    }
    return;
  }

  if (event.type === "message_delta") {
    if (event.delta?.stop_reason) output.stopReason = mapStopReason(event.delta.stop_reason);
    if (event.usage) updateUsage(output, event.usage);
  }
}

function renderPrompt(context: Context): string {
  const sections: string[] = [];

  if (context.systemPrompt) {
    sections.push(`<system>\n${context.systemPrompt}\n</system>`);
  }

  sections.push(
    "You are running as pi's experimental Claude CLI provider. Respond as the assistant for the transcript below. Do not claim to have used pi tools, and do not attempt to call tools.",
  );
  sections.push(renderMessages(context.messages));

  return sections.filter(Boolean).join("\n\n");
}

function renderMessages(messages: Message[]): string {
  return messages.map(renderMessage).join("\n\n");
}

function renderMessage(message: Message): string {
  if (message.role === "user") return `<user>\n${renderContent(message.content)}\n</user>`;
  if (message.role === "assistant") return `<assistant>\n${renderAssistantContent(message.content)}\n</assistant>`;
  if (message.role === "toolResult") return `<tool_result name=\"${message.toolName}\">\n${renderContent(message.content)}\n</tool_result>`;
  return `<message>\n${JSON.stringify(message)}\n</message>`;
}

function renderContent(content: Message["content"]): string {
  if (typeof content === "string") return content;
  return content
    .map((item) => {
      if (item.type === "text") return item.text;
      if (item.type === "image") return `[image omitted: ${item.mimeType}]`;
      return JSON.stringify(item);
    })
    .join("\n");
}

function renderAssistantContent(content: AssistantMessage["content"]): string {
  return content
    .map((item) => {
      if (item.type === "text") return item.text;
      if (item.type === "thinking") return `<thinking>\n${item.thinking}\n</thinking>`;
      if (item.type === "toolCall") return `<tool_call name=\"${item.name}\">\n${JSON.stringify(item.arguments)}\n</tool_call>`;
      return JSON.stringify(item);
    })
    .join("\n");
}

function updateUsage(output: AssistantMessage, usage: AnthropicLikeUsage | ClaudeCliUsage): void {
  output.usage.input = usage.input_tokens ?? output.usage.input;
  output.usage.output = usage.output_tokens ?? output.usage.output;
  output.usage.cacheRead = usage.cache_read_input_tokens ?? output.usage.cacheRead;
  output.usage.cacheWrite = usage.cache_creation_input_tokens ?? output.usage.cacheWrite;
  output.usage.totalTokens = output.usage.input + output.usage.output + output.usage.cacheRead + output.usage.cacheWrite;
}

function mapStopReason(reason: string): StopReason {
  if (reason === "max_tokens") return "length";
  if (reason === "tool_use") return "toolUse";
  if (reason === "cancelled") return "aborted";
  return "stop";
}
