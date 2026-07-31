<!-- BEGIN github-work-standard -->

## GitHub work ledger

- Create typed Feature, Bug, or Task issues with outcome, evidence, acceptance, constraints,
  dependencies, and verification.
- Use native sub-issue and blocking relationships; do not substitute prose TODOs when relationships
  are available.
- Assign the active worker before implementation. Assignment is additive; ambiguous planned
  ownership gets `needs-owner`.
- Every PR references its issue. Partial or automated PRs use `Refs`; only a verified final PR may
  use `Closes`, `Fixes`, or `Resolves`.
- Finality requires no open blockers, all required sub-issues complete, acceptance evidence
  recorded, and removed scope documented.
- Before closing an unmerged or superseded PR, record the reason and successor link. Convert
  follow-ups to typed related issues.
- Preserve repository-specific validation, merge, deployment, and cleanup guidance.

<!-- END github-work-standard -->
