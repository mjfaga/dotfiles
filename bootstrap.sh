#!/usr/bin/env bash

# Script is dependent on being run from the root repo directory
cd "$(dirname "${BASH_SOURCE[0]}")" || exit;

git pull origin master;

dotfilesLocal="../dotfiles-local";

function doIt() {
  files=();
  for file in ./{bin,init,.?[a-z]*}; do
    localFile=${file:2}
    if [ "$localFile" != ".git" ] &&
      [ "$localFile" != ".gitignore" ]; then
      fallbackOnSymlink=true

      if [ -d "$dotfilesLocal" ]; then
        if [ -f "$dotfilesLocal/$localFile" ]; then
          files+=("$localFile")
          if [ -h ~/$localFile ]; then
            echo "unlinking $localFile"
            unlink ~/$localFile
          fi

          echo "Copying '$localFile'..."
          cp "$(pwd)/$localFile" ~/$localFile
          echo "Appending '$dotfilesLocal/$localFile'..."
          cat $dotfilesLocal/$localFile >> ~/$localFile
          fallbackOnSymlink=false
        fi
      fi

      if $fallbackOnSymlink; then
        echo "Simlinking '$localFile'..."
        ln -sfn "$(pwd)/$localFile" ~/$localFile
      fi;

      unset fallbackOnSymlink;
    fi;
    unset localFile;
  done;
  if [ -d "$dotfilesLocal" ]; then
    for file in $dotfilesLocal/.?[a-z]*; do
      localFile=${file:2}
      localFile=$(basename -- "$localFile")
      if [ "$localFile" != ".git" ] &&
        [ "$localFile" != ".gitignore" ]; then
        if [[ ! " ${files[*]} " =~ $localFile ]]; then
          echo "Simlinking '$localFile'..."
          ln -sfn "$(pwd)/$dotfilesLocal/$localFile" ~/$localFile
        fi;
      fi;
      unset localFile;
    done;
  fi;
  unset file;

  echo "Simlinking 'init.vim'..."
  mkdir -p ~/.config/nvim
  ln -sf "$(pwd)/.vimrc" ~/.config/nvim/init.vim

  echo "Sourcing '~/.bash_profile'..."
  source ~/.bash_profile;
}

if [ "$1" == "--force" ] || [ "$1" == "-f" ]; then
  doIt;
else
  read -p "This may overwrite existing files in your home directory. Are you sure? (y/n) " -n 1;
  echo "";
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    doIt;
  fi;
fi;
unset doIt;
