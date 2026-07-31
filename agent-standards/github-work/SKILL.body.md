---
name: github-work
description:
  Create, classify, relate, assign, link, finalize, and restore GitHub work items and pull requests.
  Use BEFORE opening an issue or PR, or WHEN rolling back a work-item mutation.
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
`*github-work-targets*`, `*github-work-ownership*`, and `*.github-work-receipt.json*`.

Assign before creating a branch. Every mutating command requires `--receipt PATH`; keep that path
private and reuse it for compensating `restore`. Use `issue-create` with Feature, Bug, or Task and
native parent/blocking relationships. Use `pr-link --mode refs` by default. `pr-link --mode closes`
enforces the read-only finality check before it edits a PR body; run `finality` separately to inspect
eligibility first. Assignment preserves existing assignees and uses `needs-owner` when an ownership
lookup has zero or multiple candidates.

A second restore and a receipt from a successful no-op mutation are no-ops. A missing receipt path is
exit `2`. `restore` exits `3` when labels remain in use; resolve those references and retry. Restore
output distinguishes `empty`, `already_restored`, `restored`, and `labels_in_use`, and reports both
restored and mutated operation counts. Receipts remain compatible across helper releases with the
same receipt schema; each new operation records the active helper source and private-config digests
as audit metadata. On interruption or partial failure, recover created work from the receipt and any
`partial: true` output rather than relying on normal success output.

Exit `0` means success or eligibility. Exit `1` means a read-only eligibility, preflight, or finality
check failed. Exit `2` means an operational or configuration error; mutating commands report
classification ineligibility as exit `2`. Read-only commands emit JSON on exits `0` and `1`; exit `2`
reports the operational error on stderr. Finality consumers must check `reason` (`ready`,
`not_ready`, or `classification`) before reading relationship counts. Multiline PR bodies are edited
through a body file. Never let this generic lifecycle replace local land or deployment checks.

The generated helper is tested at its immutable public source tag before distribution.

<!-- END github-work-standard -->
