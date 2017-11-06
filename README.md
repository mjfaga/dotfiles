# Mark's Dotfiles

## Installation

### Using Git and the bootstrap script

You can clone the repository wherever you want (I like to keep it in `~/Projects/dotfiles`). The bootstrapper script will pull in the latest version and copy the files to your home folder.

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

Once you are bootstrapped, add the following to the bottom of the global .gitconfig:
```bash
[user]

  name = First Last
  email = example@email.com
```

Other things I like to install:
* [Disk Inventory X](http://www.derlien.com/index.html)
* Microsoft Office 365 for Mac

### Sensible macOS defaults

When setting up a new Mac, you may want to set some sensible macOS defaults:

```bash
./.macos
```

### Install Homebrew formulae

When setting up a new Mac, you may want to install some common [Homebrew](http://brew.sh/) formulae (after installing Homebrew, of course):
```bash
./brew.sh
```

## Feedback

Suggestions/improvements [welcome](https://github.com/mjfaga/dotfiles/issues)!

## Author

Original Author:

| [![twitter/mathias](http://gravatar.com/avatar/24e08a9ea84deb17ae121074d0f17125?s=70)](http://twitter.com/mathias "Follow @mathias on Twitter") |
|---|
| [Mathias Bynens](https://mathiasbynens.be/) |

Updates By:
Mark Faga
