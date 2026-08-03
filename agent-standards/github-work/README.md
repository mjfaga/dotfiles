# GitHub Work Standard

Public, repository-neutral sources for using GitHub as an agent work ledger. Runtime target and ownership inventories are external and must be supplied with `--config` and `--ownership-config`.

For immutable versioning, validation, tagging, consumer rollout, and completion criteria, see [RELEASING.md](RELEASING.md). Private target sequencing, fixtures, rollback, and cleanup belong in the private operator runbook.

## Commands

`github_work.py` provides `preflight`, `labels ensure`, `issue-create`, `work-graph create`, `pr-link`, `finality`, `assign`, `restore`, and `standard-check`. `--dry-run` is a global option and must precede the command. Mutations use strict mode-`0600` JSON receipts bound to the helper source SHA and private-config digest. Multiline GitHub content is always passed through temporary body files.

`sync_github_work_standard.py --config TARGETS --source-tag TAG --source-sha SHA [--checkout-override OWNER/REPO=/FEATURE/WORKTREE] [--check|--dry-run]` verifies the immutable tag/SHA and clean source tree before rendering bounded blocks, templates, skills, a marked helper, a pull-request-capable provenance workflow, and bounded formatter/private-state ignore blocks. Runtime checkout overrides direct output into feature worktrees without changing the configured target digest. Config files ending in `.yml` are JSON-compatible YAML parsed with the Python standard-library `json` module.

`public_content_check.py --targets TARGETS --ownership OWNERSHIP` rejects runtime-private names, paths, ownership values, rollout receipt artifacts, and generic secret patterns in this public tree.

## Personal-product isolation

Personal products use the same immutable public sources but a distinct private isolation policy.
They use managed `type:*` labels instead of organization-native issue types, vendor the rendered
artifacts into each repository, and have no runtime dependency on the source repository. Private
configuration can forbid target namespaces, reusable workflow owners, and secret prefixes. The
renderer preflights every selected checkout and fails before writing if any personal checkout crosses that boundary.

The public repository contains only generic mechanisms. Repository inventories, machine paths,
ownership, receipts, and isolation values remain in the private operator configuration.

## Private target schema

```json
{
  "isolation_policies": {
    "personal-products": {
      "required_classification": "managed-label",
      "forbidden_target_values": ["private-organization/", "/private/product/path/"],
      "forbidden_workflow_uses": ["private-organization/"],
      "forbidden_secret_prefixes": ["PRIVATE_ORG_"]
    }
  },
  "isolation_assignments": {
    "repository_prefixes": {
      "personal-owner/": "personal-products"
    }
  },
  "targets": [
    {
      "repo": "sample-space/sample-app",
      "checkout": "/runtime/path",
      "adapter": "generated-modern",
      "classification": "managed-label",
      "isolation_policy": "personal-products",
      "agents_source_path": "AGENTS.src.md",
      "skill_source_path": ".claude/skills/github-work/SKILL.src.md",
      "issue_forms_path": ".github/ISSUE_TEMPLATE",
      "pr_template_path": ".github/pull_request_template.md",
      "helper_path": "scripts/github_work.py",
      "standard_workflow_path": ".github/workflows/github-work-standard.yml",
      "gitignore_path": ".gitignore",
      "prettierignore_path": ".prettierignore",
      "checks": ["project-specific check"]
    }
  ],
  "auxiliary_repositories": [
    {"repo": "sample-space/shared-config", "classification": "native-type"}
  ]
}
```

Adapters are explicit. Unknown layouts, isolation policies, absolute output paths, and `..` escapes fail before rendering. Existing template content outside bounded classification blocks is byte-preserved; existing unrelated labels are retained inside the adopted block. Generated files are never edited directly—configure source paths instead.

Ownership is supplied separately as `{"mappings":[{"repo":"sample-space/sample-app","area":"sample-area","logins":["sample-user"]}]}`. Zero or multiple matches apply/retain `needs-owner`; automation never guesses.
