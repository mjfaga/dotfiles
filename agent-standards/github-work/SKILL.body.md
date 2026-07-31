---
name: github-work
description:
  Use when creating, classifying, relating, assigning, linking, finalizing, or restoring GitHub work
  items and pull requests.
---

<!-- BEGIN github-work-standard -->

# GitHub work lifecycle

Requires GitHub CLI 2.96.0 or newer. Run the repository-local `scripts/github_work.py` with the
private operator-supplied configuration paths; never commit those private files to a consumer:

```bash
python3 scripts/github_work.py \
  --config "$GITHUB_WORK_PRIVATE_CONFIG" \
  --ownership-config "$GITHUB_WORK_OWNERSHIP_CONFIG" \
  preflight --repos OWNER/REPO
```

The target file is JSON-compatible YAML with `targets` and optional `auxiliary_repositories` arrays.
Each target declares `repo`, `adapter`, and `classification`; the ownership file has a `mappings`
array of `repo`, `area`, and `logins`. The private operator supplies their location. Keep receipts
under `.github-work/receipts/`; consumer repositories must ignore `.github-work/`,
`github-work-targets.y*ml`, `github-work-ownership.y*ml`, and `*.github-work-receipt.json`.

Assign before creating a branch. Use `issue-create` with Feature, Bug, or Task and native
parent/blocking relationships. Use `pr-link --mode refs` by default. Run read-only `finality` before
promotion to `--mode closes`. Assignment preserves existing assignees and uses `needs-owner` when an
ownership lookup has zero or multiple candidates. Save receipts for mutations and use `restore` for
compensating rollback; a second restore is a no-op. Multiline PR bodies are edited through a body
file. Never let this generic lifecycle replace local land/deploy checks.

The generated helper is tested at its immutable public source tag before distribution.

<!-- END github-work-standard -->
