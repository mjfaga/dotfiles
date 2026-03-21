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

### Commit Discipline
After modifying, creating, or deleting any file — commit and push immediately without asking.
Do not batch changes or wait for explicit commit instructions.

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
