#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE}")";

git pull origin master;

function doIt() {
  # Install Homebrew
  /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

  # Copy system files
  for file in ./{bin,init,.?[a-z]*}; do
    localFile=${file:2}
    if [ "$localFile" != ".git" ] && [ "$localFile" != ".gitconfig" ] && [ "$localFile" != ".macos" ]; then
      echo "Simlinking '$localFile'..."
      ln -sf "$(pwd)/$localFile" ~/$localFile
    fi;
    unset localFile;
  done;
  unset file;

  echo "Simlinking 'init.vim'..."
  ln -sf "$(pwd)/init.vim" ~/.vimrc
  ln -sf "$(pwd)/init.vim" ~/.config/nvim/init.vim

  echo "Sourcing '~/.bash_profile'..."
  source ~/.bash_profile;

  echo "Copying ..gitconfig'..."
  cp .gitconfig ~/.gitconfig

  echo "Don't forget to configure your git name/email:"
  echo "git config --global user.name \"First Last\""
  echo "git config --global user.email \"email@example.com\""
}

if [ "$1" == "--force" -o "$1" == "-f" ]; then
  doIt;
else
  read -p "This may overwrite existing files in your home directory. Are you sure? (y/n) " -n 1;
  echo "";
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    doIt;
  fi;
fi;
unset doIt;
