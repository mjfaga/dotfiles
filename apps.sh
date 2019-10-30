#!/usr/bin/env bash

# Check for Homebrew Installation
if ! which brew > /dev/null; then
  echo "Installing Homebrew"
  /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
fi;

echo "Updating and installing apps via Homebrew..."
# Make sure we’re using the latest Homebrew.
brew update

# Upgrade any already-installed formulae.
brew upgrade

# Install everything inside Brewfile
brew bundle

if ! fgrep -q '/usr/local/bin/bash' /etc/shells; then
  echo "Switch to using brew-installed bash as default shell..."
  echo '/usr/local/bin/bash' | sudo tee -a /etc/shells;
  chsh -s /usr/local/bin/bash;
fi;

# Remove outdated versions from the cellar.
brew cleanup
