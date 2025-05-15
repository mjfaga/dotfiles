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
  asdf plugin add nodejs https://github.com/asdf-vm/asdf-nodejs.git
  asdf plugin add ruby https://github.com/asdf-vm/asdf-ruby.git
  asdf plugin add java https://github.com/halcyon/asdf-java.git
  asdf plugin add python https://github.com/asdf-community/asdf-python.git
  ```

- [ ] Run fzf key bindings install: `$(brew --prefix)/opt/fzf/install` (Note: Don't update shell
      configurations)
- [ ] Configure Clean Shot
  - [ ] Navigate to **System Settings** -> **Keyboard** -> **Keyboard shortcuts** and uncheck all
        options
  - [ ] Open Preferences
    - [ ] Check **Start at Login**
- [ ] Configure CocConfig
  - [ ] `:CocInstall coc-html`
  - [ ] `:CocInstall coc-tsserver`
  - [ ] `:CocInstall coc-json`
  - [ ] `:CocInstall coc-markdownlint`
  - [ ] `:CocInstall coc-prettier`
  - [ ] `:CocInstall coc-eslint`
  - [ ] `gem install solargraph`, then `:CocInstall coc-solargraph`
- [ ] Run `xcode-select --install`
- [ ] Install
      [Github Copilot](https://docs.github.com/en/copilot/getting-started-with-github-copilot?tool=vimneovim)

  - [ ] `git clone https://github.com/github/copilot.vim ~/.config/nvim/pack/github/start/copilot.vim`
  - [ ] `:Copilot setup`
  - [ ] `:Copilot enable`

- [ ] Install
      [Github CLI w/copilot](https://docs.github.com/en/copilot/managing-copilot/configure-personal-settings/installing-github-copilot-in-the-cli)
  - [ ] `gh auth login`
  - [ ] `gh extension install github/gh-copilot`
  - [ ] `gh extension upgrade gh-copilot`
- [ ] Raycast
  - [ ] System Preferences -> Keyboard -> Shortcuts -> Spotlight and disable the keyboard shortcut.
  - [ ] Configure Cmd + Space as Raycast trigger
  - [ ] Mark all setup tasks completed
  - [ ] Enable Cloud Sync
- [ ] Arc Browser
  - [ ] Sign into account + enable sidebar sync
  - [ ] General
    - [ ] Check "Automatically update my Arc"
  - [ ] Profiles
    - [ ] Passwords
      - [ ] Settings
        - [ ] Disable "Offer to save passwords and passkeys"
  - [ ] Max
    - [ ] Enable All
  - [ ] Advanced
    - [ ] Enable "Restore windows from previous session"
    - [ ] Enable "Show full URL when Toolbar is enabled"
  - [ ] Chrome Extensions
    - [ ] [1Password](https://chromewebstore.google.com/detail/1password-%E2%80%93-password-mana/aeblfdkhhhdcdjpifhhbdiojplfjncoa?hl=en)
    - [ ] [React Dev Tools](https://chromewebstore.google.com/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi?hl=en)
    - [ ] [Relay Dev Tools](https://chromewebstore.google.com/detail/relay-developer-tools/ncedobpgnmkhcmnnkcimnobpfepidadl?hl=en)
    - [ ] [Refined Github](https://chromewebstore.google.com/detail/refined-github/hlepfoohegkhhmjieoechaddaejaokhf?pli=1)
      - [ ] Options -> Features -> Disable "update-pr-from-base-branch"
    - [ ] [Vimium](https://chromewebstore.google.com/detail/vimium/dbepggeogbaibhgnhhndojpepiihcmeb?hl=en)
- [ ] Sign into google accounts to enable contact sync
- [ ] Open Photos to sync to iCloud
- [ ] MacOS App Store
  - [ ] Xcode
  - [ ] OneDrive
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
    :github: Bearer <get from 1Password>
    ```

  - [ ] Create a `bundle/config` file in this repo:

    ```sh
    ---
    BUNDLE_HTTPS://RUBYGEMS__PKG__GITHUB__COM/HUNTCLUB/: "mjfaga:<get from 1Password>"
    BUNDLE_GEMS__GRAPHQL__PRO: "<get from 1Password">
    ```

- [ ] Install [1Password CLI](https://support.1password.com/command-line-getting-started/)
- [ ] Zed
  - [ ] Configure Github Language service access token in projects
- [ ] Dropbox
  - [ ] Disable Preferences -> Import -> Enable camera uploads
- [ ] Iterm
  - [ ] General ->
    - [ ] Window ->
      - [ ] Uncheck "Adjust window when changing font size"
  - [ ] Appearance ->
    - [ ] General ->
      - [ ] Theme = Minimal
    - [ ] Tabs ->
      - [ ] Check "Preserve window size when tab bar shows or hides"
  - [ ] Profiles ->
    - [ ] Keys -> Left Option Key = Esc+
    - [ ] Terminal -> Check "Unlimited scrollback"
    - [ ] General -> Working Directory -> Select "Reuse previous session's directory"
    - [ ] Text -> Non-ASCII Font -> Hack Nerd Font Mono, "Regular", size 13
- [ ] Display - turn on schedule for nightshift -> sunset to sunrise
- [ ] System Preferences -> Displays -> set up arrangement and menu bar
- [ ] Install Office 365
- [ ] Install [Disk Inventory X](http://www.derlien.com/index.html)
- [ ] Install [Postgres App](https://postgresapp.com/downloads.html)
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

- [ ] For any `rails` + `heroku` repos, configure [parity](https://github.com/thoughtbot/parity)

## Feedback

Suggestions/improvements [welcome](https://github.com/mjfaga/dotfiles/issues)!
