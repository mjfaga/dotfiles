# vscode-ruby-lsp-v0.9.7
## ✨ Enhancements

- Consider server test item tags for test explorer (https://github.com/Shopify/ruby-lsp/pull/3235) by @vinistock
- Add test item filtering for resolve command (https://github.com/Shopify/ruby-lsp/pull/3240) by @vinistock

## 🐛 Bug Fixes

- Fix incorrect RBS highlighting in Ruby code (https://github.com/Shopify/ruby-lsp/pull/3221) by @st0012
- Ensure workspace is fully initialized before discovering tests (https://github.com/Shopify/ruby-lsp/pull/3203) by @vinistock
- Fix range and workspace processing for test discovery updates (https://github.com/Shopify/ruby-lsp/pull/3236) by @vinistock
- Fix Encoding::UndefinedConversionError in activation.rb (https://github.com/Shopify/ruby-lsp/pull/3214) by @mckeed
- Fix regexp patterns for block parameters (https://github.com/Shopify/ruby-lsp/pull/3212) by @taichi-ishitani

## 📦 Other Changes

- Make RBS signature opacity optional (https://github.com/Shopify/ruby-lsp/pull/3242) by @vinistock
- Make RBS inline signature tokens more specific (https://github.com/Shopify/ruby-lsp/pull/3243) by @vinistock



# vscode-ruby-lsp-v0.9.6
## ✨ Enhancements

- Support highlighting inline RBS signatures starting with `#:` (https://github.com/Shopify/ruby-lsp/pull/3215) by @st0012



# vscode-ruby-lsp-v0.9.5
## ✨ Enhancements

- Resolve test items with server request (https://github.com/Shopify/ruby-lsp/pull/3186) by @vinistock
- Add command to show LSP's internal state for diagnosing issues (https://github.com/Shopify/ruby-lsp/pull/3195) by @vinistock

## 🐛 Bug Fixes

- Reject binary encoded environment variables in activation script (https://github.com/Shopify/ruby-lsp/pull/3161) by @vinistock
- Never include workspace name as part of relative test URI (https://github.com/Shopify/ruby-lsp/pull/3181) by @vinistock
- Add support for ASDF v0.16 (https://github.com/Shopify/ruby-lsp/pull/3185) by @vinistock

## 📦 Other Changes

- Avoid focusing on test items on document switch (https://github.com/Shopify/ruby-lsp/pull/3197) by @vinistock



# vscode-ruby-lsp-v0.9.3
## ✨ Enhancements

- Start discovering all available tests lazily (https://github.com/Shopify/ruby-lsp/pull/3120) by @vinistock

## 📦 Other Changes

- Pass machine ID to server for telemetry (https://github.com/Shopify/ruby-lsp/pull/3157) by @vinistock



# vscode-ruby-lsp-v0.9.2
## 🐛 Bug Fixes

- Use bundled environment activation script file (https://github.com/Shopify/ruby-lsp/pull/3083) by @vinistock
- fix duplicate ending tag  on erb.html files(#3117) (https://github.com/Shopify/ruby-lsp/pull/3121) by @jules-w2
- Ensure disposables are being tracked by the entities that own them (https://github.com/Shopify/ruby-lsp/pull/3142) by @vinistock

## 📦 Other Changes

- Ignore untrusted workspace error for telemetry (https://github.com/Shopify/ruby-lsp/pull/3139) by @vinistock
- Allow server to produce data telemetry (https://github.com/Shopify/ruby-lsp/pull/3150) by @vinistock



# vscode-ruby-lsp-v0.8.20
## ✨ Enhancements

- Allow for under development feature flags (https://github.com/Shopify/ruby-lsp/pull/3119) by @vinistock

## 🐛 Bug Fixes

- Fix local variable assignment highlighting with no spaces (https://github.com/Shopify/ruby-lsp/pull/3131) by @vinistock

## 📦 Other Changes

- Bump Tapioca and Launcher rollout (https://github.com/Shopify/ruby-lsp/pull/3122) by @vinistock
- Roll out Tapioca add-on to 100% of users (https://github.com/Shopify/ruby-lsp/pull/3134) by @vinistock



# vscode-ruby-lsp-v0.8.19
## ✨ Enhancements

- Check if bundle is valid before restarting (https://github.com/Shopify/ruby-lsp/pull/3066) by @vinistock

## 📦 Other Changes

- Bump rollout of Tapioca add-on to 30% (https://github.com/Shopify/ruby-lsp/pull/3097) by @vinistock



# vscode-ruby-lsp-v0.8.18
## 🐛 Bug Fixes

- Prevent double activation when multiple documents are opened (https://github.com/Shopify/ruby-lsp/pull/3070) by @vinistock



# vscode-ruby-lsp-v0.8.17
## ✨ Enhancements

- Provide additional debugging help when the debugger exits with an error (https://github.com/Shopify/ruby-lsp/pull/2961) by @st0012
- VSCode extension checks multiple install locations for `mise` binary (https://github.com/Shopify/ruby-lsp/pull/2943) by @adam12
- Add a new command to help users migrate launch.json configurations (https://github.com/Shopify/ruby-lsp/pull/2450) by @st0012
- Add Show Output Channel command for VSCode extension (https://github.com/Shopify/ruby-lsp/pull/2986) by @timkooi-jobber

## 🐛 Bug Fixes

- Fix: Block parameters prefixed with underscore are incorrectly highlighted (https://github.com/Shopify/ruby-lsp/pull/2972) by @willyamacaroni
- Fix word boundary regexes in Ruby grammar (https://github.com/Shopify/ruby-lsp/pull/2984) by @vinistock



# vscode-ruby-lsp-v0.8.16
## ✨ Enhancements

- Print debugger output to the Ruby LSP output channel as well as the debug console (https://github.com/Shopify/ruby-lsp/pull/2957) by @st0012



# vscode-ruby-lsp-v0.8.15
## ✨ Enhancements

- Fallback to closest Ruby if we can't find an installation for the requested version (https://github.com/Shopify/ruby-lsp/pull/2912) by @vinistock

## 🐛 Bug Fixes

- Allow opting into specific feature flags (https://github.com/Shopify/ruby-lsp/pull/2931) by @vinistock

## 📦 Other Changes

- Extract Ruby fallback cancellable flow (https://github.com/Shopify/ruby-lsp/pull/2911) by @vinistock
- Rollout launcher mode to 5% of users (https://github.com/Shopify/ruby-lsp/pull/2914) by @vinistock



# vscode-ruby-lsp-v0.8.14
## ✨ Enhancements

- Allow configuring rbenv executable path (https://github.com/Shopify/ruby-lsp/pull/2875) by @aurelien-reeves-scalingo
- Display output channel when addons are clicked (https://github.com/Shopify/ruby-lsp/pull/2850) by @st0012

## 🐛 Bug Fixes

- Prevent Shadowenv from mutating BUNDLE_GEMFILE (https://github.com/Shopify/ruby-lsp/pull/2874) by @vinistock
- Eagerly compute SHA's for watched files (https://github.com/Shopify/ruby-lsp/pull/2861) by @vinistock
- Merge composed bundle environment into Ruby object (https://github.com/Shopify/ruby-lsp/pull/2881) by @vinistock
- Fix enabled feature flags object composition (https://github.com/Shopify/ruby-lsp/pull/2899) by @vinistock
- Limit supported client schemes to file and git (https://github.com/Shopify/ruby-lsp/pull/2889) by @vinistock
- Make `enabled_feature?` return true when all flags are enabled (https://github.com/Shopify/ruby-lsp/pull/2900) by @vinistock

## 📦 Other Changes

- Remove experimental features from extension and migrate old settings (https://github.com/Shopify/ruby-lsp/pull/2830) by @vinistock
- Show multi-root workspace warning as progress instead (https://github.com/Shopify/ruby-lsp/pull/2879) by @vinistock
- Only include workspace name as part of telemetry (https://github.com/Shopify/ruby-lsp/pull/2883) by @vinistock
- Allow individual version managers to trigger manual Ruby selection (https://github.com/Shopify/ruby-lsp/pull/2835) by @vinistock
- Fallback to latest known Ruby if no .ruby-version is found (https://github.com/Shopify/ruby-lsp/pull/2836) by @vinistock


