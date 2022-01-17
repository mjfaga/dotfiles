#!/usr/bin/env bash

source ~/.shell/functions
source ~/.shell/path
source ~/.zsh/prompt
source ~/.shell/settings
source ~/.zsh/settings
source ~/.zsh/autocompletion
source ~/.shell/aliases
source ~/.shell/plugins
source ~/.zsh/plugins

# For stuff that you don't want commited
if [ -f ~/.zsh/extra ]; then
  source ~/.zsh/extra
fi
