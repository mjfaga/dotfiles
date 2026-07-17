# Dotfiles — Agent Instructions

Public dotfiles repo (`mjfaga/dotfiles`). Shared configuration safe for public visibility.

## What This Repo Manages

Symlinked configuration for: vim/neovim, zsh, git, tmux, shell utilities, and editor settings.
All files are source-of-truth; symlinks into `~` and `~/.config` are created by dotbot.

## Key Conventions

### Installation
- **dotbot** manages symlinks via `install.conf.yaml`
- Run `./install` to apply — it reads `install.conf.yaml` and creates/updates symlinks
- `install.conf.yaml` format: `- link:` section maps `~/.target: source/path`
- `create: true` and `relink: true` are defaults — parent dirs auto-created, existing symlinks replaced

### Public Content Only
This repo is **public**. Never commit:
- API keys, tokens, or secrets
- Machine-specific paths or hostnames
- Private configuration (use `dotfiles-local` instead)

### Companion Repo
Private config lives in `~/projects/dotfiles-local` (`mjfaga/dotfiles-local`).
When editing a symlinked file, check `ls -la` to determine which repo owns it before committing.

### `bin/` is a shared drop zone — it is gitignored by default

`install.conf.yaml` maps `~/bin: bin`, so **`~/bin` IS this repo's `bin/` directory**. Anything
`dotfiles-local` (or `internal-slackbot`) links into `~/bin` physically lands here as an untracked
symlink pointing into a **private** repo. Committing one leaks the script's existence and the
private path, permanently, into a public repo.

Because of that, `.gitignore` ignores `bin/*` and allow-lists only this repo's own scripts:

```gitignore
bin/*
!bin/bash
!bin/subl
```

- **Adding a script that belongs to THIS repo?** Add a `!bin/<name>` exception (or `git add -f`).
- **Adding a script to `dotfiles-local/bin/`?** Do nothing here — it's ignored automatically.
- **Never** relax `bin/*` to make a stray file commit. If something in `bin/` is untracked and you
  didn't put it there, it's almost certainly a private symlink — run
  `readlink bin/<name>` and check whether it points at `dotfiles-local`.

The failure mode is intentionally lopsided: forgetting a `!` line means a public script silently
fails to commit (loud, harmless). The old per-script ignore list meant forgetting a line leaked a
private script (silent, permanent).

### Commit Discipline
After modifying, creating, or deleting any file — commit and push directly to `main` immediately, without asking. Do not batch changes or wait for explicit commit instructions.

This repo is exempt from the usual global rules that require a PR and a `/review` pass. It is also exempt from the worktree workflow and from the `block-primary-worktree` hook — **edit in place; do not create a worktree here.**

**Stage only the files you changed, by exact path.** Never `git add -A`, `git add .`, `git add -u`, or `git commit -a`. Multiple agent sessions write to this repo concurrently, so a blanket add sweeps another session's unrelated, in-progress work into your commit. Run `git status` before committing and confirm the staged set contains only your intended files. If unrelated changes are present, leave them unstaged.

### Directory Structure
- `shell/` — shared shell config (aliases, functions, settings, path, plugins)
- `vim/` — neovim/vim config (autoload, plugged, colors, etc.)
- `zsh/` — zsh configuration modules
- `bin/` — utility scripts added to PATH
- `init/` — initialization/setup scripts
- `nvim/` — neovim-specific config (filetype.lua, etc.)
- `zed/` — Zed editor settings, keymap, and tasks
- `bash/` — bash-specific config
- `goose/` — Goose AI agent config and recipes
- `ssh/` — SSH client configuration
- `television/` — television fuzzy finder config

### Pre-commit Checks
No automated pre-commit hooks. Verify manually:
1. `./install` completes without errors
2. Symlinks resolve correctly (`ls -la ~/.target`)
3. No secrets or private paths in committed files

### Editing Conventions
- Shell files use POSIX-compatible syntax where possible (zsh-specific goes in `zsh/`)
- Vim config uses Vimscript (not Lua) in `vim/`, Lua configs go in `nvim/`
- Aliases and functions are organized by topic in `shell/` subdirectories
