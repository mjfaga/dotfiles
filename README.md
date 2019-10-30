# Mark's Dotfiles

## Installation

### Clone repositories

Yep, that's right. My scripts assume you have a general dotfiles repository, and also a dotfiles-local repository where you store stuff specific to your workstation. If you don't have a "local" repository, that's cool too. Just skip that step.

You can clone the repositories wherever you want (I like to keep them in `~/projects/`).

```bash
# from ~/projects
git clone git@github.com:mjfaga/dotfiles-local.git ./dotfiles-local # Regardles of the local dotfiles name, always putit in a dotfiles-local directory
git clone git@github.com:mjfaga/dotfiles.git
cd dotfiles
```

### Install Homebrew formulae

When setting up a new Mac, you may want to install some common [Homebrew](http://brew.sh/) formulae (Homebrew installed automatically by script):
```bash
./brew.sh
```

### Bootstrap script

The bootstrapper script will pull in the latest version of your dotfiels and simlink/copy the files to your home folder.

```bash
# from ~/Projects
git clone git@github.com:mjfaga/dotfiles.git && cd dotfiles && source bootstrap.sh
```

To run the bootstrap:
```bash
cd dotfiles
source bootstrap.sh
```

Alternatively, to update while avoiding the confirmation prompt:
```bash
cd dotfiles
set -- -f; source bootstrap.sh
```

To update later on, just run that command again.

Other things I like to install:
* [Disk Inventory X](http://www.derlien.com/index.html)
* Microsoft Office 365 for Mac

### Sensible macOS defaults

When setting up a new Mac, you may want to set some sensible macOS defaults:

```bash
./.macos
```

## Feedback

Suggestions/improvements [welcome](https://github.com/mjfaga/dotfiles/issues)!
