# GitHub Work Standard

Public, repository-neutral sources for using GitHub as an agent work ledger. Runtime target and ownership inventories are external and must be supplied with `--config` and `--ownership-config`.

## Commands

`github_work.py` provides `preflight`, `labels ensure`, `issue-create`, `work-graph create`, `pr-link`, `finality`, `assign`, `restore`, and `standard-check`. `--dry-run` is a global option and must precede the command. Mutations use strict mode-`0600` JSON receipts bound to the helper source SHA and private-config digest. Multiline GitHub content is always passed through temporary body files.

`sync_github_work_standard.py --config TARGETS --source-tag TAG --source-sha SHA [--checkout-override OWNER/REPO=/FEATURE/WORKTREE] [--check|--dry-run]` verifies the immutable tag/SHA and clean source tree before rendering bounded blocks, templates, skills, and a marked helper. Runtime checkout overrides direct output into feature worktrees without changing the configured target digest. Config files ending in `.yml` are JSON-compatible YAML parsed with the Python standard-library `json` module.

`public_content_check.py --targets TARGETS --ownership OWNERSHIP` rejects runtime-private names, paths, ownership values, rollout receipt artifacts, and generic secret patterns in this public tree.

## Private target schema

```json
{
  "targets": [
    {
      "repo": "sample-space/sample-app",
      "checkout": "/runtime/path",
      "adapter": "generated-modern",
      "classification": "native-type",
      "agents_source_path": "AGENTS.src.md",
      "skill_source_path": ".claude/skills/github-work/SKILL.src.md",
      "issue_forms_path": ".github/ISSUE_TEMPLATE",
      "pr_template_path": ".github/pull_request_template.md",
      "helper_path": "scripts/github_work.py",
      "checks": ["project-specific check"]
    }
  ],
  "auxiliary_repositories": [
    {"repo": "sample-space/shared-config", "classification": "native-type"}
  ]
}
```

Adapters are explicit. Unknown layouts, absolute output paths, and `..` escapes fail before rendering. Existing template content outside bounded classification blocks is byte-preserved; existing unrelated labels are retained inside the adopted block. Generated files are never edited directly—configure source paths instead.

Ownership is supplied separately as `{"mappings":[{"repo":"sample-space/sample-app","area":"sample-area","logins":["sample-user"]}]}`. Zero or multiple matches apply/retain `needs-owner`; automation never guesses.
