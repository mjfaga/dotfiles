#!/usr/bin/env bash

tap "bramstein/webfonttools"
tap "caskroom/cask"
tap "heroku/brew"
tap "homebrew/bundle"
tap "homebrew/cask"
tap "homebrew/core"
tap "thoughtbot/formulae"

# Install GNU core utilities (those that come with OS X are outdated).
# Don’t forget to add `$(brew --prefix coreutils)/libexec/gnubin` to `$PATH`.
brew "coreutils"

# Install some other useful utilities like `sponge`.
brew "moreutils"
# Install GNU `find`, `locate`, `updatedb`, and `xargs`, `g`-prefixed.
brew "findutils"
# Install GNU `sed`, overwriting the built-in `sed`.
# Don’t forget to add `$(brew --prefix gnu-sed)/libexec/gnubin` to `$PATH`.
brew "gnu-sed"
# Install Bash 4.
# Note: don’t forget to add `/usr/local/bin/bash` to `/etc/shells` before
# running `chsh`.
brew "bash"
brew "bash-completion@2"

# Install `wget`
brew "wget"

# Install more recent versions of some OS X tools.
brew "vim" #, args: ["override-system-vi"]

# Install Java
cask "Java"

# Install font tools.
brew "bramstein/webfonttools/sfnt2woff"
brew "bramstein/webfonttools/sfnt2woff-zopfli"
brew "woff2" # requires Java

# Install some CTF tools; see https://github.com/ctfs/write-ups.
brew "bfg"
brew "aircrack-ng"
brew "binutils"
brew "binwalk"
brew "cifer"
brew "fcrackzip"
brew "foremost"
brew "httpie"
brew "netpbm"
brew "nmap"
brew "pngcheck"
brew "sqlmap"
brew "tcpflow"
brew "tcpreplay"
brew "tcptrace"
brew "ucspi-tcp" # `tcpserver` etc.
brew "xpdf"
brew "xz"

# Install other useful binaries.
brew "ack"
brew "git"
brew "git-lfs"
brew "shellcheck"
brew "imagemagick" #, args:['with-webp']
brew "neovim"
brew "p7zip"
brew "pigz"
brew "pv"
brew "reattach-to-user-namespace"
brew "rename"
brew "speedtest_cli"
brew "ssh-copy-id"
brew "tmux"
brew "tree"
brew "webkit2png"
brew "zopfli"
brew "tig"
brew "pgcli"
brew "jq"
brew "fzf"
brew "ripgrep"
brew "nvm"
brew "yarn", args: ["ignore-dependencies"]

# Applications
cask "google-chrome"
cask "brave-browser"
cask "firefox"
cask "slack"
cask "1password"
cask "divvy"
cask "gimp"
cask "dash"
cask "alfred"
cask "licecap"
cask "iterm2"
cask "dropbox"
cask "bettertouchtool"
cask "evernote"
cask "visual-studio-code"
brew "graphviz"

#dev tools
cask "postgres"
brew "memcached"
brew "redis"
brew "direnv"
brew "heroku/brew/heroku"

# https://github.com/thoughtbot/parity
brew "thoughtbot/formulae/parity"

# Matrix console screen saver
brew "cmatrix"
