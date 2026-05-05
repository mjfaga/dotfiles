# Pi customizations

This directory contains public, non-secret pi customizations managed by dotbot.

## Claude CLI provider

`pi/agent/extensions/claude-cli-provider` registers an experimental `claude-cli` provider for pi.
It shells out to the local Claude Code CLI using the user's existing Claude Code login and explicitly removes `ANTHROPIC_API_KEY` from the child process environment.

Install/symlink with:

```bash
./install
```

Then use:

```bash
pi --provider claude-cli --model sonnet
pi --provider claude-cli --model haiku -p "Say hello"
```

Notes:

- This is for local developer use only.
- The provider disables Claude CLI tools and MCP servers so file edits continue to go through pi when using pi's normal providers.
- Because the CLI invocation is text-only and tools are disabled, this provider is best for chat/summarization experiments, not full coding-agent workflows.
