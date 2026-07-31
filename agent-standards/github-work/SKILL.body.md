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
array of `repo`, optional `area`, and `logins`. With `--area`, ownership resolution prefers exact,
then `*`, then no match; a bare default never satisfies an explicit area, so use `*` in mappings for
cross-area ownership. A literal `--area "*"` queries only that wildcard mapping tier. Without
`--area`, resolution prefers the omitted-area default, then `*`, then a union of specific areas.
Every assignment result, including partials, emits `ownership_source` as `exact`, `wildcard`,
`default`, `default-ineligible`, `area-unmapped`, `repo-unmapped`, `specific-union`, or `explicit`;
these values distinguish an ineligible bare default, a missing area in a configured repository, and
a repository absent from the ownership map. A supplied non-empty ownership config is validated
before non-restore commands but used only by `assign --from-ownership-map`; restore ignores it so
the shared invocation remains safe. The private operator supplies the files' locations. Consumer
repositories must ignore `.github-work/`, `*github-work-targets*`, `*github-work-ownership*`,
`*.github-work-receipt.json*`, and `*github-work-recovery*.json*`.

Assign before creating a branch. Every mutating command requires `--receipt PATH`; keep the path in
a private location excluded from source control, such as `.github-work/receipts/`, and reuse it for
compensating `restore`. Use `issue-create` with Feature, Bug, or Task and native parent/blocking
relationships. Use `pr-link --mode refs` by default. `pr-link --mode closes` enforces the read-only
finality check before it edits a PR body; run `finality` separately to inspect eligibility first.
Assignment preserves existing assignees, adds a uniquely resolved owner when needed, and uses
`needs-owner` only when an unassigned issue's lookup has zero or multiple human candidates. When an
issue becomes human-owned, assignment removes a stale `needs-owner` label with a reversible receipt
operation. Map ambiguity on an owned issue reports `existing-owner`; `already-assigned` results use
stable `assignee`, `assignees`, and `candidates` keys. Every assignment result, including partials,
includes `needs_owner_removed`; `true` means removal occurred or would occur under `--dry-run`,
`false` means no removal, and `null` means removal is in flight or unknown. A bot-only matched tier
remains fail-closed and reports its source. An empty `--receipt`, `--title`, `--assignee`, `--area`,
`--parent`, `--blocking`, or `--body-file`, or `--area` without `--from-ownership-map`, exits `2`.
Empty target or ownership config exits `2` on commands that consume configuration; `standard-check`
ignores both, while `restore` audits target config availability and ignores ownership config. Other
commands fail fast on a supplied empty or malformed ownership config even when only a later
assignment step uses it.

A second restore and a receipt from a successful no-op mutation are no-ops. Restore reports
`retained_labels` with `retained_label_definitions` when a receipt-created label definition must
remain to preserve a reversed removal. A missing receipt path is exit `2`. Restore does not require
the private target config and tolerates a supplied config path that is missing, empty, unreadable,
or invalid during rollback. Its output and schema-v3 per-operation audit metadata distinguish an
unavailable requested config from a deliberately config-free restore. `config_status` is `ok`,
`absent`, `empty`, `unreadable`, or `invalid`; older receipts without these audit fields mean
unknown. It exits `3` when labels remain in use; resolve those references and retry. Restore output
distinguishes `empty`, `already_restored`, `restored`, and `labels_in_use`, and reports both
restored and mutated operation counts. Receipts remain compatible across helper releases with a
supported receipt schema even if the repository is later removed from active target configuration.
Drain outstanding newer-schema receipts before pinning an older standard version. Schema-v3
operations require creation and restore attribution. Each new operation records the active helper
source and private-config digests as audit metadata.

On interruption or partial failure, recover created work from the receipt and any `partial: true`
output. Partial payloads accompany a non-zero exit and require reconciliation. Stage `audit` means
the GitHub mutation succeeded but receipt persistence failed; `mutation-result-unknown` means verify
live GitHub state. PR-body recovery data is written beside the receipt at the private mode-0600
`recovery_path`, not stdout. A primary-write failure records errno/detail and tries a mode-0600
system-temp path. `recovery_fallback_used` is true only when that write succeeds. Recovery payloads
always include stable primary/fallback attempted-path, errno, and detail keys with nulls where they
do not apply. `recovery_error` is one of null, `receipt-path-unavailable`, `primary-write-failed`,
or `primary-and-fallback-write-failed`. If both writes fail, `recovery_path` is null. Delete a
recovery file after reconciliation.

For `labels ensure`, `created` contains receipt-backed labels; in dry-run output it contains planned
labels. `failed_label` requires the action indicated by `stage`. Issue-create partials include the
`title`, `requested_relationships`, `relationship`, `relationship_added`, `completed_relationships`,
and `stage`; the title is deliberately emitted when it may be the only recovery handle. Work-graph
failures are partial only when a child or prior mutation needs reconciliation; they include
receipt-backed `issues`, `failed_repo`, and the child's `failed_partial`. Dry-run issue objects are
plans without URLs. A `needs-owner` failure reports `label_created` when it made the shared label
during that invocation.

Exit `0` means success or eligibility. Exit `1` means the read-only `preflight` or `finality`
command found ineligibility. The mutating `pr-link --mode closes` finality gate also returns exit
`1` with a `finality` object and makes no PR edit. Exit `2` means an operational or configuration
error; other mutating-command classification failures use exit `2`. Eligibility responses emit JSON
on exits `0` and `1`; exit `2` reports the operational error on stderr. Finality consumers must
check `reason` (`ready`, `not_ready`, or `classification`) before reading relationship counts.
Multiline PR bodies are edited through a body file. Never let this generic lifecycle replace local
land or deployment checks.

The generated helper is tested at its immutable public source tag before distribution.

<!-- END github-work-standard -->
