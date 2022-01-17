#!/usr/bin/env bash

source ~/.shell/functions
source ~/.shell/path
source ~/.bash/prompt
source ~/.shell/settings
source ~/.bash/settings
source ~/.bash/autocompletion
source ~/.shell/aliases
source ~/.shell/plugins
source ~/.bash/plugins

# For stuff that you don't want commited
if [ -f ~/.bash/extra ]; then
  source ~/.bash/extra
fi
