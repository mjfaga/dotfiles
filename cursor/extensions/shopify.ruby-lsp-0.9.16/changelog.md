# vscode-ruby-lsp-v0.9.16
## ✨ Enhancements

- Fix RBS highlighting in Ruby regexes (https://github.com/Shopify/ruby-lsp/pull/3390) by @Morriar
- Highlight multiline RBS signature syntax (https://github.com/Shopify/ruby-lsp/pull/3391) by @Morriar

## 🐛 Bug Fixes

- Fix RBS highlighting in Ruby regexes (https://github.com/Shopify/ruby-lsp/pull/3390) by @Morriar



# vscode-ruby-lsp-v0.9.15
## 🐛 Bug Fixes

- Fix heredoc syntax highlighting (https://github.com/Shopify/ruby-lsp/pull/3389) by @Morriar



# vscode-ruby-lsp-v0.9.14
## ✨ Enhancements

- Add test run durations to status updates (https://github.com/Shopify/ruby-lsp/pull/3368) by @vinistock

## 📦 Other Changes

- Allow test run cancellation in Test Results panel (https://github.com/Shopify/ruby-lsp/pull/3343) by @alexcrocha



# vscode-ruby-lsp-v0.9.13
## ✨ Enhancements

- Introduce test file watcher (https://github.com/Shopify/ruby-lsp/pull/3326) by @alexcrocha
- Implement debug handler based on command resolution (https://github.com/Shopify/ruby-lsp/pull/3354) by @vinistock
- Auto resolve first test file of each top level directory (https://github.com/Shopify/ruby-lsp/pull/3349) by @vinistock
- Implement test coverage profile for the explorer (https://github.com/Shopify/ruby-lsp/pull/3361) by @vinistock

## 🐛 Bug Fixes

- Remove workspace from map when not eagerly activating (https://github.com/Shopify/ruby-lsp/pull/3352) by @vinistock
- Apply debug env customizations on top of Ruby environment (https://github.com/Shopify/ruby-lsp/pull/3353) by @vinistock

## 📦 Other Changes

- Add telemetry for the new test explorer usage (https://github.com/Shopify/ruby-lsp/pull/3362) by @vinistock



# vscode-ruby-lsp-v0.9.12
## 🐛 Bug Fixes

- Avoiding rejecting promise if test command failed (https://github.com/Shopify/ruby-lsp/pull/3334) by @vinistock
- Automatically discover children for test files that weren't expanded (https://github.com/Shopify/ruby-lsp/pull/3336) by @vinistock

## 📦 Other Changes

- Allow cancelling test runs (https://github.com/Shopify/ruby-lsp/pull/3338) by @vinistock
- Use abort controller as signal to cancel test execution (https://github.com/Shopify/ruby-lsp/pull/3341) by @vinistock



# vscode-ruby-lsp-v0.9.11
## ✨ Enhancements

- Add support for appendOutput to streaming explorer updates (https://github.com/Shopify/ruby-lsp/pull/3323) by @vinistock

## 🐛 Bug Fixes

- Use map compact instead of filter_map in activation script (https://github.com/Shopify/ruby-lsp/pull/3321) by @vinistock
- Do not include workspace name as part of relative path (https://github.com/Shopify/ruby-lsp/pull/3329) by @vinistock
- Accumulate streaming promises and await all before exiting (https://github.com/Shopify/ruby-lsp/pull/3330) by @vinistock



# vscode-ruby-lsp-v0.9.9
## ✨ Enhancements

- Add new run handler for test controller (https://github.com/Shopify/ruby-lsp/pull/3251) by @vinistock

## 🐛 Bug Fixes

- Add icon for GoToRelevantFile in vscode (https://github.com/Shopify/ruby-lsp/pull/3320) by @jenny-codes



# vscode-ruby-lsp-v0.9.10
## ✨ Enhancements

- Add support for appendOutput to streaming explorer updates (https://github.com/Shopify/ruby-lsp/pull/3323) by @vinistock

## 🐛 Bug Fixes

- Use map compact instead of filter_map in activation script (https://github.com/Shopify/ruby-lsp/pull/3321) by @vinistock



# vscode-ruby-lsp-v0.9.8
## ✨ Enhancements

- Add GoToRelevantFile functionality (https://github.com/Shopify/ruby-lsp/pull/2985) by @jenny-codes

## 🐛 Bug Fixes

- Append test output when a test fails (https://github.com/Shopify/ruby-lsp/pull/3146) by @klaaspieter
- Assorted RBS grammar fixes (https://github.com/Shopify/ruby-lsp/pull/3275) by @Morriar

## 📦 Other Changes

- Avoid mutating test items when filtering them (https://github.com/Shopify/ruby-lsp/pull/3245) by @vinistock
- Allowing finding test items based on ID and URI (https://github.com/Shopify/ruby-lsp/pull/3272) by @vinistock



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


