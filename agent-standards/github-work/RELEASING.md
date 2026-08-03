# Releasing the GitHub Work Standard

This runbook publishes a new immutable, repository-neutral GitHub Work Standard release.
Target inventories, ownership, checkout paths, receipts, and isolation values belong in private
operator configuration and must never be committed here.

## Release invariants

- Never move or reuse an existing `agent-standards-github-work-v*` tag.
- Consumers pin both the release tag and its full 40-character source commit SHA.
- Edit canonical sources here, not rendered files in consumer repositories.
- Preserve existing consumer behavior outside managed blocks.
- Keep public sources machine-neutral and free of target inventories, ownership, receipts, paths, and secrets.
- A release is not complete until selected consumers are merged and remote-main provenance is verified.

## 1. Prepare the public source

Changes confined to operator documentation such as this runbook do not require a standard release;
validate, commit, and push them without retagging or rolling consumers. Continue through the release
steps when changing rendered content, the helper, schemas, policy behavior, or consumer validation.

1. Confirm there is no overlapping release work.
2. Modify the canonical files under `agent-standards/github-work/`.
3. Update `standard.yml` to a new version. Use a new version for every released content or behavior change.
4. Update tests with the implementation.

Set local paths without committing them:

```bash
PUBLIC_REPO=/path/to/public-dotfiles
SOURCE_ROOT="$PUBLIC_REPO/agent-standards/github-work"
PRIVATE_TARGETS=/path/to/private/targets.yml
PRIVATE_OWNERSHIP=/path/to/private/ownership.yml
```

## 2. Validate before publishing

```bash
cd "$PUBLIC_REPO"
python3 -m unittest discover -s agent-standards/github-work/tests -p 'test_*.py'
python3 -m py_compile \
  agent-standards/github-work/github_work.py \
  agent-standards/github-work/scripts/public_content_check.py \
  agent-standards/github-work/scripts/sync_github_work_standard.py
ruff check agent-standards/github-work
python3 agent-standards/github-work/scripts/public_content_check.py \
  --root agent-standards/github-work \
  --targets "$PRIVATE_TARGETS" \
  --ownership "$PRIVATE_OWNERSHIP"
```

The public-content check must report zero violations. Review `git diff` for stale version strings,
generated residue, private values, and unrelated changes.

## 3. Commit, push, and tag

Follow the public dotfiles repository's exact-path staging rules. After the signed commit is pushed to `main`:

```bash
VERSION=$(python3 -c 'import json; print(json.load(open("agent-standards/github-work/standard.yml"))["version"])')
TAG="agent-standards-github-work-v$VERSION"
SOURCE_SHA=$(git rev-parse HEAD)

git tag "$TAG" "$SOURCE_SHA"
git push origin "$TAG"

test "$(git rev-parse "$TAG^{commit}")" = "$SOURCE_SHA"
git ls-remote --exit-code --tags origin "refs/tags/$TAG"
```

If commit signing fails, restore the signing agent and retry once; do not bypass signing. Never
replace a published tag—fix forward with another version.

## 4. Hand off to the private rollout

Update the private operator configuration's standard version, tag, and source SHA. The renderer
requires a clean source checkout whose `HEAD` equals `SOURCE_SHA`; use a detached checkout at the
immutable tag rather than a public `main` checkout that may advance. The operator then renders
selected targets with:

```bash
python3 "$SOURCE_ROOT/scripts/sync_github_work_standard.py" \
  --config "$PRIVATE_TARGETS" \
  --source-root "$SOURCE_ROOT" \
  --source-tag "$TAG" \
  --source-sha "$SOURCE_SHA" \
  --repos OWNER/REPO \
  --checkout-override OWNER/REPO=/absolute/feature/worktree \
  --check
```

Remove `--check` only when rendering into the intended feature worktree. Roll out through ordinary
consumer PRs; do not push consumer changes directly to their default branches.

## 5. Completion criteria

A release is complete when:

- public tests, compilation, lint, and public/private isolation checks pass;
- the immutable tag resolves to the expected source SHA;
- every selected consumer's repository-specific checks and review pass;
- every selected consumer is merged and its remote-main provenance workflow passes;
- a final renderer `--check` reports zero drift against fresh remote-main checkouts;
- each consumer's checked-in `standard-check` command reports `current: true` and `pinned: true`;
- any lifecycle mutations have mode-`0600`, source/config-attributed receipts with no outstanding operations.

Use the private operator runbook for target sequencing, lifecycle fixtures, rollback, and cleanup.
