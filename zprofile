#!/usr/bin/env bash

source ~/.zsh/functions
source ~/.zsh/path
source ~/.zsh/prompt
source ~/.zsh/settings
source ~/.zsh/autocompletion
source ~/.zsh/aliases
source ~/.zsh/plugins

# For stuff that you don't want commited
if [ -f ~/.zsh/extra ]; then
  source ~/.zsh/extra
fi
