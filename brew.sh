#!/usr/bin/env bash

# Install command-line tools using Homebrew.

# Ask for the administrator password upfront.
sudo -v

# Keep-alive: update existing `sudo` time stamp until the script has finished.
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

# Make sure we’re using the latest Homebrew.
brew update

# Upgrade any already-installed formulae.
brew upgrade --all

# Install GNU core utilities (those that come with OS X are outdated).
# Don’t forget to add `$(brew --prefix coreutils)/libexec/gnubin` to `$PATH`.
brew install coreutils
sudo ln -s /usr/local/bin/gsha256sum /usr/local/bin/sha256sum

# Install some other useful utilities like `sponge`.
brew install moreutils
# Install GNU `find`, `locate`, `updatedb`, and `xargs`, `g`-prefixed.
brew install findutils
# Install GNU `sed`, overwriting the built-in `sed`.
brew install gnu-sed --with-default-names
# Install Bash 4.
# Note: don’t forget to add `/usr/local/bin/bash` to `/etc/shells` before
# running `chsh`.
brew install bash
brew install bash-completion2

# Install `wget` with IRI support.
brew install wget --with-iri

# Install more recent versions of some OS X tools.
brew install vim --override-system-vi

# Install Java
brew cask install Java

# Install font tools.
brew tap bramstein/webfonttools
brew install sfnt2woff
brew install sfnt2woff-zopfli
brew install woff2 # requires Java

# Install some CTF tools; see https://github.com/ctfs/write-ups.
brew install bfg
brew install aircrack-ng
brew install binutils
brew install binwalk
brew install cifer
brew install fcrackzip
brew install foremost
brew install httpie
brew install netpbm
brew install nmap
brew install pngcheck
brew install sqlmap
brew install tcpflow
brew install tcpreplay
brew install tcptrace
brew install ucspi-tcp # `tcpserver` etc.
brew install xpdf
brew install xz

# Install other useful binaries.
brew install ack
brew install git
brew install git-lfs
brew install shellcheck
brew install imagemagick --with-webp
brew install neovim
brew install p7zip
brew install pigz
brew install pv
brew install reattach-to-user-namespace
brew install rename
brew install speedtest_cli
brew install ssh-copy-id
brew install tmux
brew install tree
brew install webkit2png
brew install zopfli
brew install tig
brew install pgcli
brew install fzf
brew install ripgrep
brew install nvm
mkdir ~/.nvm
brew install yarn --without-node

# Applications
brew cask install google-chrome
brew cask install firefox
brew cask install slack
brew cask install 1password
brew cask install divvy
brew cask install gimp
brew cask install dash
brew cask install alfred
brew install Caskroom/cask/iterm2
brew install Caskroom/cask/dropbox
brew install Caskroom/cask/bettertouchtool
brew install Caskroom/cask/evernote
brew install graphviz

#dev tools
brew install memcached
brew install redis
brew install direnv

# https://github.com/thoughtbot/parity
brew tap thoughtbot/formulae
brew install parity

# Matrix console screen saver
brew install cmatrix

# Remove outdated versions from the cellar.
brew cleanup
