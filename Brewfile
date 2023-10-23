#!/usr/bin/env bash

tap "bramstein/webfonttools"
tap "heroku/brew"
tap "thoughtbot/formulae"
tap "inigolabs/homebrew-tap"
tap "eth-p/software"

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
cask "font-hack-nerd-font"
brew "inigo_cli"
brew "cmake"
brew "pkg-config"
brew "openssl"
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
brew "tree"
brew "webkit2png"
brew "zopfli"
brew "tig"
brew "pgcli"
brew "jq"
brew "fzf"
brew "ripgrep"
brew "asdf"
brew "maven"
brew "yarn", args: ["ignore-dependencies"]
brew "bat"
brew "eth-p/software/bat-extras"
brew "netpbm"
brew "xz"
brew "httpie"
brew "watchman" # Required for relay compiler
brew "tailspin"
brew "duckdb"

# Applications
cask "zed"
brew "television"
cask "cleanshot"
cask "raycast"
cask "arc"
cask "google-chrome"
cask "brave-browser"
cask "firefox"
cask "slack"
cask "1password"
cask "1password-cli"
cask "divvy"
cask "gimp"
cask "licecap"
cask "iterm2"
cask "dropbox"
cask "visual-studio-code"
cask "graphiql"
brew "graphviz"
cask "notion"
brew "pandoc"
cask "spotify"
cask "postman"
cask "remarkable"
cask "postico"
cask "tuple"

#dev tools
brew "gh"
cask "ngrok"
brew "kubectl"
cask "lens"
brew "memcached"
brew "redis"
brew "direnv"
brew "heroku/brew/heroku"
cask "docker"

# https://github.com/thoughtbot/parity
brew "thoughtbot/formulae/parity"

# Matrix console screen saver
brew "cmatrix"
