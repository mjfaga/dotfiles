# Pi customizations

This directory contains public, non-secret pi customizations managed by dotbot.

## Primary model integration

Pi already supports Anthropic Claude Pro/Max subscription auth directly via `/login`. That built-in Anthropic provider is the fully functional primary integration: it supports pi's normal tool-calling loop, sessions, compaction, thinking levels, images, and model switching.

This repo sets the global pi defaults in `pi/agent/settings.json`:

```json
{
  "defaultProvider": "openai-codex",
  "defaultModel": "gpt-5.5",
  "defaultThinkingLevel": "medium",
  "doubleEscapeAction": "tree",
  "enabledModels": [
    "openai-codex/gpt-5.5",
    "openai-codex/gpt-5.4-mini",
    "anthropic/claude-sonnet-4-6",
    "anthropic/claude-opus-4-5"
  ]
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

## Shell initialization

Pi runs tool commands through non-interactive bash. Global settings point `shellCommandPrefix` at `~/.pi/agent/shell-init.bash`, which is managed by private dotfiles-local and enables shared shell aliases/functions for Pi bash tool calls.

## Keyboard shortcuts

This repo also links `pi/agent/keybindings.json` to `~/.pi/agent/keybindings.json`.

Custom bindings:

- `Alt+N` — new session (`/new`)
- `Alt+R` — resume picker (`/resume`)
- `Alt+T` — session tree (`/tree`)

Useful built-in bindings left at pi defaults:

- `Ctrl+L` — model selector
- `Ctrl+P` / `Shift+Ctrl+P` — cycle scoped models from `enabledModels`
- `Shift+Tab` — cycle thinking level
- `Ctrl+O` — collapse/expand tool output
- `Ctrl+T` — collapse/expand thinking blocks
- double `Esc` — session tree

## Claude CLI provider experiment

`pi/agent/extensions/claude-cli-provider` is intentionally **not** installed as an auto-discovered extension. It shells out to the Claude Code CLI and is useful only as an experiment for text-only local calls.

It is not suitable as the primary coding provider because Claude CLI does not expose pi's arbitrary tool schemas as model tool calls. A production-quality pi provider needs to stream pi `toolCall` events so pi can execute and record `read`, `edit`, `write`, `bash`, etc. The built-in Anthropic subscription provider already does that.

Manual experiment only:

```bash
pi --extension ./pi/agent/extensions/claude-cli-provider/index.ts --provider claude-cli --model haiku -p "Say hello"
```
