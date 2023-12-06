# Mark's dotfiles

## Installation

I use [dotbot](https://github.com/anishathalye/dotbot) for managing my dot files now.

Check out the [install.conf.yaml](./install.conf.yaml) for my current configuration.

## Manual setup steps

- [ ] `mkdir ~/projects`
- [ ] `cd ~/projects`
- [ ] [Create GitHub SSH key](https://help.github.com/en/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)
- [ ] `git clone git@github.com:mjfaga/dotfiles.git`
- [ ] Run [dotfiles](https://www.github.com/mjfaga/dotfiles) configuration
- [ ] `git clone git@github.com:mjfaga/dotfiles-local.git`
- [ ] Run [dotfiles-local](https://www.github.com/mjfaga/dotfiles-local) configuration
- [ ] Reload terminal
- [ ] `sh apps.sh`
- [ ] `sh macos.sh`
- [ ] Install VIM pluggins via `:PlugInstall`
- [ ] Install `asdf` plugins

  ```sh
  asdf plugin-add nodejs git@github.com:asdf-vm/asdf-nodejs.git
  asdf plugin add ruby https://github.com/asdf-vm/asdf-ruby.git
  asdf plugin-add java https://github.com/halcyon/asdf-java.git
  asdf plugin-add python https://github.com/asdf-community/asdf-python.git
  ```

- [ ] Run fzf key bindings install: `$(brew --prefix)/opt/fzf/install` (Note: Don't update shell
      configurations)
- [ ] Configure CocConfig
  - [ ] `:CocInstall coc-html`
  - [ ] `:CocInstall coc-tsserver`
  - [ ] `:CocInstall coc-json`
  - [ ] `:CocInstall coc-markdownlint`
  - [ ] `:CocInstall coc-prettier`
  - [ ] `:CocInstall coc-eslint`
  - [ ] `gem install solargraph`, then `:CocInstall coc-solargraph`
- [ ] Install
      [Github Copilot](https://docs.github.com/en/copilot/getting-started-with-github-copilot?tool=vimneovim)

  - [ ] `git clone https://github.com/github/copilot.vim ~/.config/nvim/pack/github/start/copilot.vim`
  - [ ] `:Copilot setup`
  - [ ] `:Copilot enable`

- [ ] Download [Raycast](https://api.raycast.app/v2/download)
  - [ ] System Preferences -> Keyboard -> Shortcuts -> Spotlight and disable the keyboard shortcut.
  - [ ] Configure Cmd + Space as Raycast trigger
  - [ ] Mark all setup tasks completed
  - [ ] Configure hotkeys
    - [ ] Left Half: Ctrl + Shift + Cmd + Left Arrow
    - [ ] Right Half: Ctrl + Shift + Cmd + Right Arrow
    - [ ] Maximize: Ctrl + Option + Cmd + Up Arrow
    - [ ] Lock Screen: Cmd + L
    - [ ] Clipboard History: Shift + Cmd + V
    - [ ] AI chat shortcut: Option + Cmd + A
- [ ] Sign into google accounts to enable contact sync
- [ ] Open Photos to sync to iCloud
- [ ] MacOS App Store
  - [ ] Xcode
  - [ ] OneDrive
- [ ] Run `xcode-select --install`
- [ ] Sign into 1Password

  - [ ] [Turn on the SSH agent](https://blog.1password.com/git-commit-signing/?utm_source=google&utm_medium=cpc&utm_campaign=18388341772&utm_content=&utm_term=&gclid=Cj0KCQiAx6ugBhCcARIsAGNmMbhUaZJ4RXEhaEf1q5nWzB5lxcL_rA1uzkVCgIw_KkTXmTqXwabTlIUaAs4xEALw_wcB&gclsrc=aw.ds)
        for github key signing
  - [ ] Put signing key into `.gitconfig.secret`:

  ```sh
  [user]
    signingkey = <value here>
  ```

- [ ] Create a `gem/credential` file in this repo:

  ```sh
  ---
  :rubygems_api_key: <get from 1Password>
  ```

- [ ] Create a `bundle/config` file in this repo:

  ```sh
  ---
  BUNDLE_GEMS__GRAPHQL__PRO: "<get from 1Password">
  ```

- [ ] Open chrome and sign-in/configure
- [ ] Download Arc Beta (personal url in 1Password)
- [ ] Dropbox
  - [ ] Disable Preferences -> Import -> Enable camera uploads
- [ ] Iterm
  - [ ] General ->
    - [ ] Window ->
      - [ ] Uncheck "Adjust window when changing font size"
  - [ ] Preferences ->
    - [ ] Appearance ->
      - [ ] General ->
        - [ ] Theme = Minimal
      - [ ] Tabs ->
        - [ ] Check "Preserve window size when tab bar shows or hides"
    - [ ] Profiles ->
      - [ ] Keys -> Left Option Key = Esc+
      - [ ] Terminal -> Check "Unlimited scrollback"
      - [ ] General -> Working Directory -> Select "Reuse previous session's directory"
      - [ ] Text -> Non-ASCII Font -> 3270 Nerd Font, "Regular", size 13
- [ ] Dash
  - [ ] Load license
  - [ ] Set up sync folder to Dropbox
  - [ ] Preferences -> General ->
    - [ ] check "Launch Dash at login”
    - [ ] Global Search Shortcut = Shift + Cmd + D
- [ ] Display - turn on schedule for nightshift -> sunset to sunrise
- [ ] System Preferences -> Displays -> set up arrangement and menu bar
- [ ] Install Office 365
- [ ] Install [Disk Inventory X](http://www.derlien.com/index.html)
- [ ] Install [Postgres App](https://postgresapp.com/downloads.html)
- [ ] Install [Postico App](https://eggerapps.at/postico2/)
- [ ] Run `kubectl completion bash > /usr/local/etc/bash_completion.d/kubectl` if kubernetes is
      installed
- [ ] Create finder "open in" shortcuts:

  - Open the Automator built-in macOS app. Pick "Application".
  - Search for “Run Shell Script” in the list of actions, and paste these 2 lines:

    ```sh
    finderPath=`osascript -e 'tell application "Finder" to get the POSIX path of (target of front window as alias)'`
    open -n -b "com.microsoft.VSCode" --args "$finderPath"
    ```

  - Save that to the Applications folder, for example as "VS Code icon in Finder"
  - Open Get Info for both VS Code and this new app, drag the VS Code icon
  - Keep the cmd pressed and drag to the Finder toolbar. Done.
  - Repeat for vim script, but with "Run Apple Script":

    ```
    tell application "Finder"
        if exists Finder window 1 then
            set currentDir to target of Finder window 1 as alias
        else
            set currentDir to desktop as alias
        end if

        set filePath to the POSIX path of currentDir
    end tell

    tell application "iTerm"
        set newWindow to (create window with default profile)

        tell current session of newWindow
            write text "cd " & filePath
            write text "vim ."
        end tell
    end tell
    ```

  - Open Get Info for this new app and drag the vim-icon.svg from this repo.
  - Keep the cmd pressed and drag to the Finder toolbar. Done.
  - For any `rails` + `heroku` repos, install [parity](https://github.com/thoughtbot/parity)
  - Install [Remarkable desktop app](https://my.remarkable.com/device/desktop)

## Feedback

Suggestions/improvements [welcome](https://github.com/mjfaga/dotfiles/issues)!
