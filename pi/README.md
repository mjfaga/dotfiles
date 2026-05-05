# Pi customizations

This directory contains public, non-secret pi customizations managed by dotbot.

## Primary model integration

Pi already supports Anthropic Claude Pro/Max subscription auth directly via `/login`. That built-in Anthropic provider is the fully functional primary integration: it supports pi's normal tool-calling loop, sessions, compaction, thinking levels, images, and model switching.

This repo sets the global pi defaults in `pi/agent/settings.json`:

```json
{
  "defaultProvider": "anthropic",
  "defaultModel": "claude-sonnet-4-6",
  "defaultThinkingLevel": "medium"
}
```

Install/symlink with:

```bash
./install
```

Authenticate once in pi if needed:

```text
/login
```

Then use pi normally:

```bash
pi
pi -p "Say hello"
```

## Claude CLI provider experiment

`pi/agent/extensions/claude-cli-provider` is intentionally **not** installed as an auto-discovered extension. It shells out to the Claude Code CLI and is useful only as an experiment for text-only local calls.

It is not suitable as the primary coding provider because Claude CLI does not expose pi's arbitrary tool schemas as model tool calls. A production-quality pi provider needs to stream pi `toolCall` events so pi can execute and record `read`, `edit`, `write`, `bash`, etc. The built-in Anthropic subscription provider already does that.

Manual experiment only:

```bash
pi --extension ./pi/agent/extensions/claude-cli-provider/index.ts --provider claude-cli --model haiku -p "Say hello"
```
