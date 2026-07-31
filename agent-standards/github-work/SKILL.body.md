<!-- BEGIN github-work-standard -->

# GitHub work lifecycle

Run the repository-local `scripts/github_work.py` with explicit configuration paths. Start with
`preflight`; assign before creating a branch. Use `issue-create` with Feature, Bug, or Task and
native parent/blocking relationships. Use `pr-link --mode refs` by default. Run read-only `finality`
before promotion to `--mode closes`. Assignment preserves existing assignees and uses `needs-owner`
when an ownership lookup has zero or multiple candidates. Save receipts for mutations and use
`restore` for exact rollback; a second restore is a no-op. Multiline PR bodies are edited through a
body file. Never let this generic lifecycle replace local land/deploy checks.

<!-- END github-work-standard -->
