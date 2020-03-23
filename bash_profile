#!/usr/bin/env bash

source ~/.bash/functions
source ~/.bash/path
source ~/.bash/prompt
source ~/.bash/settings
source ~/.bash/autocompletion
source ~/.bash/aliases
source ~/.bash/plugins

# For stuff that you don't want commited
if [ -f ~/.bash/extra ]; then
  source ~/.bash/extra
fi
