#!/usr/bin/env python3
"""Repository-neutral GitHub work lifecycle helper.

Configuration files use JSON syntax (which is valid YAML) so the helper has no
third-party runtime dependencies.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
from contextlib import contextmanager
import os
import re
import stat
import subprocess
import sys
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

SCHEMA_VERSION = 1
MIN_GH_VERSION = (2, 96, 0)
MANAGED_LABELS = {
    "bug": ("type:bug", "B60205", "Unexpected problem or incorrect behavior"),
    "feature": ("type:feature", "1D76DB", "Requested capability or improvement"),
    "task": ("type:task", "8250DF", "Bounded implementation or follow-up work"),
}
CLOSING_WORDS = ("Closes", "Fixes", "Resolves")
NEEDS_OWNER_LABEL = ("needs-owner", "D876E3", "Ownership requires explicit triage")


class WorkError(RuntimeError):
    """A hard precondition or mutation failure."""


class EligibilityError(WorkError):
    """A reachable repository is missing required issue classification."""


@dataclass
class CommandResult:
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0


class GhRunner:
    def __init__(self, *, dry_run: bool = False) -> None:
        self.dry_run = dry_run

    def run(
        self,
        args: Sequence[str],
        *,
        mutate: bool = False,
        check: bool = True,
    ) -> CommandResult:
        if mutate and self.dry_run:
            return CommandResult()
        try:
            process = subprocess.run(
                ["gh", *args],
                check=False,
                text=True,
                capture_output=True,
            )
        except OSError as exc:
            raise WorkError(f"cannot execute GitHub CLI: {exc}") from exc
        result = CommandResult(process.stdout, process.stderr, process.returncode)
        if check and process.returncode != 0:
            detail = process.stderr.strip() or process.stdout.strip() or "unknown gh failure"
            raise WorkError(f"gh {' '.join(args)} failed: {detail}")
        return result

    def json(self, args: Sequence[str], *, check: bool = True) -> Any:
        result = self.run(args, check=check)
        if result.returncode != 0:
            return None
        try:
            return json.loads(result.stdout or "null")
        except json.JSONDecodeError as exc:
            raise WorkError(f"gh returned invalid JSON for {' '.join(args)}") from exc


OPERATION_FIELDS = {
    "label-created": {"repo", "name"},
    "issue-created": {"issue"},
    "relationship-added": {"relation", "source", "target"},
    "pr-body-changed": {"pr", "before", "after"},
    "issue-label-added": {"issue", "name"},
    "assignee-added": {"issue", "login"},
}


class Receipt:
    def __init__(
        self,
        path: str | None,
        *,
        source_sha: str,
        config_digest: str,
    ) -> None:
        self.path = Path(path) if path else None
        self.loaded = bool(self.path and self.path.exists())
        self.source_sha = source_sha
        self.config_digest = config_digest
        self.data: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "receipt_id": str(uuid.uuid4()),
            "source_sha": source_sha,
            "config_digest": config_digest,
            "operations": [],
        }
        if self.loaded:
            assert self.path is not None
            if stat.S_IMODE(self.path.stat().st_mode) != 0o600:
                raise WorkError("existing receipt permissions must be exactly 0600")
            self.data = load_json(self.path)
            self.validate()
            if self.data["source_sha"] != source_sha:
                raise WorkError("receipt source SHA does not match the active helper")
            if self.data["config_digest"] != config_digest:
                raise WorkError("receipt target-config digest does not match active config")

    def validate(self) -> None:
        required = {"schema_version", "receipt_id", "source_sha", "config_digest", "operations"}
        if required - self.data.keys():
            raise WorkError("receipt is missing required metadata")
        if self.data["schema_version"] != SCHEMA_VERSION:
            raise WorkError("unsupported receipt schema")
        if not isinstance(self.data["receipt_id"], str) or not self.data["receipt_id"]:
            raise WorkError("receipt_id must be a non-empty string")
        if not re.fullmatch(r"(?:[0-9a-f]{40}|development)", self.data["source_sha"]):
            raise WorkError("receipt source_sha is malformed")
        if not re.fullmatch(r"[0-9a-f]{64}", self.data["config_digest"]):
            raise WorkError("receipt config_digest is malformed")
        if not isinstance(self.data["operations"], list):
            raise WorkError("receipt operations must be an array")
        identifiers: set[str] = set()
        for operation in self.data["operations"]:
            if not isinstance(operation, dict):
                raise WorkError("receipt operations must be objects")
            kind = operation.get("kind")
            if kind not in OPERATION_FIELDS:
                raise WorkError(f"unsupported receipt operation: {kind}")
            required_fields = OPERATION_FIELDS[kind]
            if required_fields - operation.keys():
                raise WorkError(f"receipt operation {kind} is missing required fields")
            for field in required_fields:
                value = operation[field]
                if not isinstance(value, str):
                    raise WorkError(f"receipt operation {kind} fields must be strings")
                if not value and not (kind == "pr-body-changed" and field in {"before", "after"}):
                    raise WorkError(f"receipt operation {kind} fields must be non-empty strings")
            if kind == "relationship-added" and operation["relation"] not in {"sub-issue", "blocked-by"}:
                raise WorkError("receipt relationship type is invalid")
            operation_id = operation.get("operation_id")
            if not isinstance(operation_id, str) or not operation_id or operation_id in identifiers:
                raise WorkError("receipt operation IDs must be unique non-empty strings")
            identifiers.add(operation_id)
            if operation.get("status") not in {"active", "restored"}:
                raise WorkError("receipt operation status must be active or restored")

    def add(self, kind: str, **details: Any) -> None:
        if kind not in OPERATION_FIELDS or OPERATION_FIELDS[kind] - details.keys():
            raise WorkError(f"invalid receipt operation: {kind}")
        if "issue" in details and isinstance(details["issue"], str):
            details["issue"] = canonical_issue_reference(details["issue"])
        self.data["operations"].append({
            "operation_id": str(uuid.uuid4()),
            "status": "active",
            "kind": kind,
            **details,
        })
        self.save()

    def mark_restored(self, operation: dict[str, Any], *, mutated: bool) -> None:
        operation["status"] = "restored"
        operation["restore_mutated"] = mutated
        self.save()

    def save(self) -> None:
        if not self.path:
            return
        self.validate()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(self.data, indent=2, sort_keys=True) + "\n")
        temporary.replace(self.path)
        self.path.chmod(0o600)
        self.loaded = True


def load_json(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkError(f"cannot load JSON-compatible YAML: {path}") from exc
    if not isinstance(value, dict):
        raise WorkError(f"expected object in {path}")
    return value


def file_digest(path: str | Path) -> str:
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError as exc:
        raise WorkError(f"cannot digest configuration: {path}") from exc


def active_source_sha() -> str:
    source = Path(__file__).read_text(encoding="utf-8", errors="replace")[:1000]
    marker = re.search(r"github-work-standard: version=\S+ source=([0-9a-f]{40})\b", source)
    if marker:
        return marker.group(1)
    result = subprocess.run(
        ["git", "-C", str(Path(__file__).resolve().parent), "rev-parse", "HEAD"],
        check=False,
        text=True,
        capture_output=True,
    )
    candidate = result.stdout.strip()
    return candidate if result.returncode == 0 and re.fullmatch(r"[0-9a-f]{40}", candidate) else "development"


def load_targets(path: str | None) -> dict[str, Any]:
    if not path:
        raise WorkError("--config is required")
    config = load_json(path)
    targets = config.get("targets")
    if not isinstance(targets, list):
        raise WorkError("target config requires a targets array")
    seen: set[str] = set()
    for target in targets:
        if not isinstance(target, dict):
            raise WorkError("every target must be an object")
        required = {"repo", "adapter", "classification"}
        missing = sorted(required - target.keys())
        if missing:
            raise WorkError(f"target missing fields: {', '.join(missing)}")
        if target["repo"] in seen:
            raise WorkError(f"duplicate target: {target['repo']}")
        seen.add(target["repo"])
        if target["adapter"] not in {"generated-modern", "generated-legacy", "plain"}:
            raise WorkError(f"unknown adapter for {target['repo']}: {target['adapter']}")
        if target["classification"] not in {"native-type", "managed-label"}:
            raise WorkError(f"unknown classification for {target['repo']}")
    auxiliary = config.get("auxiliary_repositories", [])
    if not isinstance(auxiliary, list):
        raise WorkError("auxiliary_repositories must be an array")
    for item in auxiliary:
        if not isinstance(item, dict) or not isinstance(item.get("repo"), str):
            raise WorkError("auxiliary repository entries require repo")
        if item.get("classification") not in {"native-type", "managed-label"}:
            raise WorkError(f"unknown auxiliary classification for {item.get('repo')}")
        if item["repo"] in seen:
            raise WorkError(f"duplicate repository configuration: {item['repo']}")
        seen.add(item["repo"])
    return config


def target_for(config: dict[str, Any], repo: str) -> dict[str, Any]:
    for target in [*config["targets"], *config.get("auxiliary_repositories", [])]:
        if target["repo"] == repo:
            return target
    raise WorkError(f"repository is not configured: {repo}")


def parse_repositories(config: dict[str, Any], value: str) -> list[str]:
    if value == "all":
        return [target["repo"] for target in config["targets"]]
    repos = [repo.strip() for repo in value.split(",") if repo.strip()]
    if not repos:
        raise WorkError("--repos must not be empty")
    for repo in repos:
        target_for(config, repo)
    return repos


def parse_issue_url(value: str) -> tuple[str, int]:
    match = re.search(r"github\.com/([^/]+/[^/]+)/issues/(\d+)(?:$|[?#])", value)
    if match:
        return match.group(1), int(match.group(2))
    match = re.fullmatch(r"([^/]+/[^#]+)#(\d+)", value)
    if match:
        return match.group(1), int(match.group(2))
    raise WorkError(f"expected issue URL or OWNER/REPO#N: {value}")


def issue_url(repo: str, number: int) -> str:
    return f"https://github.com/{repo}/issues/{number}"


def canonical_issue_reference(value: str) -> str:
    return issue_url(*parse_issue_url(value))


def parse_pr_url(value: str) -> tuple[str, int]:
    match = re.search(r"github\.com/([^/]+/[^/]+)/pull/(\d+)(?:$|[?#])", value)
    if not match:
        raise WorkError(f"expected pull request URL: {value}")
    return match.group(1), int(match.group(2))


def json_print(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


@contextmanager
def temporary_body(content: str) -> Iterator[str]:
    handle = tempfile.NamedTemporaryFile("w", delete=False, suffix=".md", encoding="utf-8")
    try:
        handle.write(content)
        handle.close()
        yield handle.name
    finally:
        Path(handle.name).unlink(missing_ok=True)


def gh_version(runner: GhRunner) -> tuple[int, int, int]:
    text = runner.run(["version"]).stdout
    match = re.search(r"gh version (\d+)\.(\d+)\.(\d+)", text)
    if not match:
        raise WorkError("cannot parse gh version")
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def issue_state(runner: GhRunner, value: str) -> dict[str, Any]:
    return runner.json([
        "issue", "view", value,
        "--json", "url,state,labels,assignees,subIssuesSummary,blockedBy,title,body",
    ])


def issue_labels(state: dict[str, Any]) -> set[str]:
    return {item["name"] for item in state.get("labels", [])}


def issue_assignees(state: dict[str, Any]) -> set[str]:
    return {item["login"] for item in state.get("assignees", [])}


def basic_preflight(runner: GhRunner) -> tuple[int, int, int]:
    version = gh_version(runner)
    if version < MIN_GH_VERSION:
        raise WorkError(f"gh {version} is older than required {MIN_GH_VERSION}")
    auth = runner.run(["auth", "status"], check=False)
    if auth.returncode != 0:
        raise WorkError("GitHub CLI authentication is unavailable")
    return version


def repository_preflight(runner: GhRunner, repo: str) -> None:
    available = runner.run(["repo", "view", repo, "--json", "nameWithOwner"], check=False)
    if available.returncode != 0:
        raise WorkError(f"repository unavailable: {repo}")


def target_preflight(runner: GhRunner, target: dict[str, Any]) -> None:
    repo = target["repo"]
    repository_preflight(runner, repo)
    if target["classification"] == "native-type":
        owner = repo.split("/", 1)[0]
        issue_types = runner.json(["api", f"orgs/{owner}/issue-types"], check=False)
        if not isinstance(issue_types, list):
            raise WorkError(f"cannot read native issue types for {owner}")
        names = {item.get("name") for item in issue_types if isinstance(item, dict)}
        missing = {"Bug", "Feature", "Task"} - names
        if missing:
            raise EligibilityError(f"{owner} missing issue types: {sorted(missing)}")
    else:
        current = runner.json([
            "label", "list", "--repo", repo, "--limit", "200",
            "--json", "name,color,description",
        ], check=False)
        if not isinstance(current, list):
            raise WorkError(f"cannot read labels for {repo}")
        names = {item.get("name") for item in current if isinstance(item, dict)}
        missing = {definition[0] for definition in MANAGED_LABELS.values()} - names
        if missing:
            raise EligibilityError(f"{repo} missing labels: {sorted(missing)}")


def mutation_preflight(runner: GhRunner, config: dict[str, Any], repos: Iterable[str]) -> None:
    basic_preflight(runner)
    for repo in sorted(set(repos)):
        target_preflight(runner, target_for(config, repo))


def command_preflight(args: argparse.Namespace, runner: GhRunner, config: dict[str, Any]) -> int:
    failures: list[str] = []
    version = basic_preflight(runner)
    repos = parse_repositories(config, args.repos)
    native = sum(target_for(config, repo)["classification"] == "native-type" for repo in repos)
    labels = len(repos) - native
    ready = 0
    for repo in repos:
        try:
            target_preflight(runner, target_for(config, repo))
            ready += 1
        except EligibilityError as exc:
            failures.append(str(exc))
    json_print({
        "gh_version": ".".join(map(str, version)),
        "native_type_targets": native,
        "label_type_targets": labels,
        "classification_ready_targets": ready,
        "missing_classifications": len(failures),
        "failures": failures,
    })
    return 1 if failures else 0


def command_labels_ensure(
    args: argparse.Namespace, runner: GhRunner, config: dict[str, Any], receipt: Receipt
) -> int:
    created: list[dict[str, str]] = []
    unchanged = 0
    repos = parse_repositories(config, args.repos)
    basic_preflight(runner)
    for repo in repos:
        target = target_for(config, repo)
        available = runner.run(["repo", "view", repo, "--json", "nameWithOwner"], check=False)
        if available.returncode != 0:
            raise WorkError(f"repository unavailable: {repo}")
        if target["classification"] != "managed-label":
            raise WorkError(f"labels ensure is invalid for native-type target: {repo}")
        current = runner.json([
            "label", "list", "--repo", repo, "--limit", "200",
            "--json", "name,color,description",
        ]) or []
        by_name = {item["name"]: item for item in current}
        for name, color, description in MANAGED_LABELS.values():
            if name in by_name:
                unchanged += 1
                continue
            runner.run([
                "label", "create", name, "--repo", repo,
                "--color", color, "--description", description,
            ], mutate=True)
            if not runner.dry_run:
                receipt.add("label-created", repo=repo, name=name)
            created.append({"repo": repo, "name": name})
    json_print({"created": created, "created_count": len(created), "unchanged": unchanged, "dry_run": runner.dry_run})
    return 0


def default_issue_body(kind: str, title: str) -> str:
    return (
        f"## Outcome\n\n{title}\n\n"
        "## Context and evidence\n\n"
        "## Acceptance criteria\n\n- [ ] Verified outcome\n\n"
        "## Constraints and non-goals\n\n"
        "## Dependencies and relationships\n\n"
        "## Verification\n\n"
        f"Created as a {kind} work item.\n"
    )


def command_issue_create(
    args: argparse.Namespace, runner: GhRunner, config: dict[str, Any], receipt: Receipt
) -> int:
    target = target_for(config, args.repo)
    related_repos = [args.repo]
    if args.parent:
        related_repos.append(parse_issue_url(args.parent)[0])
    if args.blocking:
        related_repos.append(parse_issue_url(args.blocking)[0])
    mutation_preflight(runner, config, related_repos)
    kind = args.type.lower()
    if kind not in MANAGED_LABELS:
        raise WorkError("--type must be Bug, Feature, or Task")
    if args.assignee:
        validation = runner.run(["api", f"repos/{args.repo}/assignees/{args.assignee}"], check=False)
        if validation.returncode != 0:
            raise WorkError(f"not assignable in {args.repo}: {args.assignee}")
    body = Path(args.body_file).read_text(encoding="utf-8") if args.body_file else default_issue_body(args.type, args.title)
    command = ["issue", "create", "--repo", args.repo, "--title", args.title]
    if target["classification"] == "native-type":
        command.extend(["--type", args.type.title()])
    else:
        command.extend(["--label", MANAGED_LABELS[kind][0]])
    if args.assignee:
        command.extend(["--assignee", args.assignee])
    with temporary_body(body) as path:
        command.extend(["--body-file", path])
        result = runner.run(command, mutate=True)
    if runner.dry_run:
        json_print({"dry_run": True, "repo": args.repo, "type": args.type})
        return 0
    output_lines = result.stdout.strip().splitlines()
    if not output_lines:
        raise WorkError("gh issue create returned no issue URL")
    created_url = output_lines[-1]
    parse_issue_url(created_url)
    receipt.add("issue-created", issue=created_url)
    if target["classification"] == "managed-label":
        receipt.add("issue-label-added", issue=created_url, name=f"type:{args.type.lower()}")
    if args.parent:
        runner.run(["issue", "edit", args.parent, "--add-sub-issue", created_url], mutate=True)
        receipt.add("relationship-added", relation="sub-issue", source=args.parent, target=created_url)
    if args.blocking:
        runner.run(["issue", "edit", args.blocking, "--add-blocked-by", created_url], mutate=True)
        receipt.add("relationship-added", relation="blocked-by", source=args.blocking, target=created_url)
    json_print({"url": created_url, "repo": args.repo, "type": args.type})
    return 0


def issue_reference(value: str) -> str:
    repo, number = parse_issue_url(value)
    return f"{repo}#{number}"


def target_reference_pattern(issue: str, pr_repo: str) -> re.Pattern[str]:
    repo, number = parse_issue_url(issue)
    forms = [
        re.escape(f"https://github.com/{repo}/issues/{number}"),
        re.escape(f"{repo}#{number}"),
    ]
    if repo == pr_repo:
        forms.append(re.escape(f"#{number}"))
    return re.compile(rf"(?:{'|'.join(forms)})(?!\d)", re.IGNORECASE)


def linked_body(body: str, issue: str, mode: str, pr_repo: str) -> str:
    reference = issue_reference(issue)
    keyword = "Refs" if mode == "refs" else "Closes"
    body = re.sub(r"\bRefs\s+#ISSUE\b", f"{keyword} {reference}", body, flags=re.IGNORECASE)
    target = target_reference_pattern(issue, pr_repo)
    closing = re.compile(
        rf"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+(?P<reference>{target.pattern})",
        re.IGNORECASE,
    )
    demoted = closing.sub(lambda match: f"Refs {match.group('reference')}", body)
    refs = re.compile(rf"\bRefs\s+(?P<reference>{target.pattern})", re.IGNORECASE)
    if mode == "refs":
        if refs.search(demoted):
            return demoted.rstrip() + "\n"
        desired = f"Refs {reference}"
        return demoted.rstrip() + ("\n\n" if demoted.strip() else "") + desired + "\n"
    desired = f"Closes {reference}"
    if refs.search(demoted):
        return refs.sub(desired, demoted, count=1).rstrip() + "\n"
    return demoted.rstrip() + ("\n\n" if demoted.strip() else "") + desired + "\n"


def command_pr_link(
    args: argparse.Namespace,
    runner: GhRunner,
    config: dict[str, Any],
    receipt: Receipt,
) -> int:
    issue_repo, _ = parse_issue_url(args.issue)
    pr_repo, _ = parse_pr_url(args.pr)
    mutation_preflight(runner, config, [issue_repo, pr_repo])
    if args.mode == "closes":
        finality = finality_result(issue_state(runner, args.issue))
        if not finality["eligible"]:
            json_print({"changed": False, "finality": finality, "mode": args.mode, "pr": args.pr})
            return 1
    current = runner.json(["pr", "view", args.pr, "--json", "body,url"])
    if not isinstance(current, dict):
        raise WorkError(f"cannot read pull request: {args.pr}")
    before = current.get("body") or ""
    after = linked_body(before, args.issue, args.mode, pr_repo)
    if before == after:
        json_print({"changed": False, "pr": args.pr, "mode": args.mode})
        return 0
    with temporary_body(after) as path:
        runner.run(["pr", "edit", args.pr, "--body-file", path], mutate=True)
    if not runner.dry_run:
        receipt.add("pr-body-changed", pr=args.pr, before=before, after=after)
    json_print({"changed": True, "dry_run": runner.dry_run, "pr": args.pr, "mode": args.mode})
    return 0


def finality_result(state: dict[str, Any]) -> dict[str, Any]:
    if "blockedBy" not in state or not isinstance(state["blockedBy"], list):
        raise WorkError("finality response lacks a valid blockedBy array")
    if "subIssuesSummary" not in state or not isinstance(state["subIssuesSummary"], dict):
        raise WorkError("finality response lacks a valid subIssuesSummary object")
    blockers = state["blockedBy"]
    for blocker in blockers:
        if not isinstance(blocker, dict) or str(blocker.get("state", "")).upper() not in {"OPEN", "CLOSED"}:
            raise WorkError("finality response contains a malformed blocker")
    summary = state["subIssuesSummary"]
    total = summary.get("total")
    completed = summary.get("completed")
    if not isinstance(total, int) or isinstance(total, bool) or not isinstance(completed, int) or isinstance(completed, bool):
        raise WorkError("finality summary counts must be integers")
    if total < 0 or completed < 0 or completed > total:
        raise WorkError("finality summary counts are inconsistent")
    open_blockers = sum(1 for blocker in blockers if blocker["state"].upper() != "CLOSED")
    incomplete = total - completed
    eligible = open_blockers == 0 and incomplete == 0
    return {
        "eligible": eligible,
        "failure": None,
        "incomplete_sub_issues": incomplete,
        "open_blockers": open_blockers,
        "reason": "ready" if eligible else "blockers",
    }


def command_finality(args: argparse.Namespace, runner: GhRunner, config: dict[str, Any]) -> int:
    repo, _ = parse_issue_url(args.issue)
    basic_preflight(runner)
    try:
        target_preflight(runner, target_for(config, repo))
    except EligibilityError as exc:
        json_print({
            "eligible": False,
            "failure": str(exc),
            "incomplete_sub_issues": None,
            "open_blockers": None,
            "reason": "classification",
        })
        return 1
    result = finality_result(issue_state(runner, args.issue))
    json_print(result)
    return 0 if result["eligible"] else 1


def ownership_candidates(config: dict[str, Any], repo: str, area: str | None) -> list[str]:
    candidates: list[str] = []
    for mapping in config.get("mappings", []):
        if mapping.get("repo") != repo:
            continue
        if area and mapping.get("area") not in {area, "*"}:
            continue
        candidates.extend(login for login in mapping.get("logins", []) if isinstance(login, str))
    return sorted(set(candidates))


def add_needs_owner(runner: GhRunner, issue: str, receipt: Receipt) -> None:
    state = issue_state(runner, issue)
    if NEEDS_OWNER_LABEL[0] in issue_labels(state):
        return
    repo, _ = parse_issue_url(issue)
    labels = runner.json([
        "label", "list", "--repo", repo, "--limit", "200", "--json", "name",
    ])
    if not isinstance(labels, list):
        raise WorkError(f"cannot verify ownership labels in {repo}")
    if NEEDS_OWNER_LABEL[0] not in {item.get("name") for item in labels if isinstance(item, dict)}:
        runner.run([
            "label", "create", NEEDS_OWNER_LABEL[0], "--repo", repo,
            "--color", NEEDS_OWNER_LABEL[1], "--description", NEEDS_OWNER_LABEL[2],
        ], mutate=True)
        if not runner.dry_run:
            receipt.add("label-created", repo=repo, name=NEEDS_OWNER_LABEL[0])
    runner.run(["issue", "edit", issue, "--add-label", NEEDS_OWNER_LABEL[0]], mutate=True)
    if not runner.dry_run:
        receipt.add("issue-label-added", issue=issue, name=NEEDS_OWNER_LABEL[0])


def command_assign(
    args: argparse.Namespace,
    runner: GhRunner,
    config: dict[str, Any],
    ownership: dict[str, Any] | None,
    receipt: Receipt,
) -> int:
    repo, _ = parse_issue_url(args.issue)
    mutation_preflight(runner, config, [repo])
    assignee = args.assignee
    if args.from_ownership_map:
        if ownership is None:
            raise WorkError("--ownership-config is required with --from-ownership-map")
        candidates = ownership_candidates(ownership, repo, args.area)
        candidates = [candidate for candidate in candidates if not candidate.endswith("[bot]")]
        if len(candidates) != 1:
            add_needs_owner(runner, args.issue, receipt)
            json_print({"assigned": False, "reason": "zero-matches" if not candidates else "multiple-matches", "candidates": candidates})
            return 0
        assignee = candidates[0]
    if not assignee:
        raise WorkError("provide --assignee or --from-ownership-map")
    if assignee.endswith("[bot]"):
        raise WorkError("bot identities cannot be planned issue owners")
    state = issue_state(runner, args.issue)
    if assignee in issue_assignees(state):
        json_print({"assigned": False, "reason": "already-assigned", "assignee": assignee})
        return 0
    validation = runner.run(["api", f"repos/{repo}/assignees/{assignee}"], check=False)
    if validation.returncode != 0:
        raise WorkError(f"not assignable in {repo}: {assignee}")
    runner.run(["issue", "edit", args.issue, "--add-assignee", assignee], mutate=True)
    if not runner.dry_run:
        receipt.add("assignee-added", issue=args.issue, login=assignee)
    json_print({"assigned": True, "dry_run": runner.dry_run, "assignee": assignee})
    return 0


def restore_pr_body(runner: GhRunner, operation: dict[str, Any]) -> bool:
    current = runner.json(["pr", "view", operation["pr"], "--json", "body"])
    if not isinstance(current, dict):
        raise WorkError(f"cannot read pull request: {operation['pr']}")
    body = current.get("body") or ""
    if body == operation["before"]:
        return False
    if body != operation["after"]:
        raise WorkError(f"refusing to overwrite independently changed PR body: {operation['pr']}")
    with temporary_body(operation["before"]) as path:
        runner.run(["pr", "edit", operation["pr"], "--body-file", path], mutate=True)
    return True


def receipt_repositories(receipt: Receipt) -> set[str]:
    repos: set[str] = set()
    for operation in receipt.data["operations"]:
        for key in ("issue", "source", "target"):
            if key in operation:
                repos.add(parse_issue_url(operation[key])[0])
        if "pr" in operation:
            repos.add(parse_pr_url(operation["pr"])[0])
        if "repo" in operation:
            repos.add(operation["repo"])
    return repos


def command_restore(
    args: argparse.Namespace,
    runner: GhRunner,
    config: dict[str, Any],
    receipt: Receipt,
) -> int:
    if not receipt.data["operations"]:
        if not receipt.loaded:
            raise WorkError(f"receipt not found: {receipt.path}")
        json_print({
            "already_restored_operations": 0,
            "dry_run": runner.dry_run,
            "restored_operations": 0,
            "skipped_labels_in_use": 0,
        })
        return 0
    if all(operation["status"] == "restored" for operation in receipt.data["operations"]):
        json_print({
            "already_restored_operations": len(receipt.data["operations"]),
            "dry_run": runner.dry_run,
            "restored_operations": 0,
            "skipped_labels_in_use": 0,
        })
        return 0
    basic_preflight(runner)
    for repo in sorted(receipt_repositories(receipt)):
        target_for(config, repo)  # Validate that every receipt repository is in the active config.
        repository_preflight(runner, repo)
    restored = 0
    already_restored = 0
    skipped_in_use = 0
    pending_issue_label_removals = {
        (canonical_issue_reference(operation["issue"]), operation["name"])
        for operation in receipt.data["operations"]
        if operation["status"] == "active" and operation["kind"] == "issue-label-added"
    }
    for operation in reversed(receipt.data["operations"]):
        if operation["status"] == "restored":
            already_restored += 1
            continue
        kind = operation["kind"]
        mutated = False
        if kind == "pr-body-changed":
            mutated = restore_pr_body(runner, operation)
        elif kind == "assignee-added":
            state = issue_state(runner, operation["issue"])
            if operation["login"] in issue_assignees(state):
                runner.run(["issue", "edit", operation["issue"], "--remove-assignee", operation["login"]], mutate=True)
                mutated = True
        elif kind == "issue-label-added":
            state = issue_state(runner, operation["issue"])
            if operation["name"] in issue_labels(state):
                runner.run(["issue", "edit", operation["issue"], "--remove-label", operation["name"]], mutate=True)
                mutated = True
        elif kind == "relationship-added":
            flag = "--remove-sub-issue" if operation["relation"] == "sub-issue" else "--remove-blocked-by"
            result = runner.run(["issue", "edit", operation["source"], flag, operation["target"]], mutate=True, check=False)
            if result.returncode == 0:
                mutated = True
            else:
                detail = f"{result.stderr}\n{result.stdout}".lower()
                if not any(marker in detail for marker in ("not found", "does not exist", "no relationship", "not related")):
                    raise WorkError(f"relationship restore failed: {result.stderr.strip() or result.stdout.strip()}")
        elif kind == "issue-created":
            state = issue_state(runner, operation["issue"])
            if str(state.get("state")).upper() == "OPEN":
                runner.run(["issue", "close", operation["issue"], "--reason", "not planned"], mutate=True)
                mutated = True
        elif kind == "label-created":
            current = runner.json([
                "label", "list", "--repo", operation["repo"], "--limit", "200", "--json", "name",
            ])
            if not isinstance(current, list):
                raise WorkError(f"cannot verify labels in {operation['repo']}")
            if operation["name"] in {item.get("name") for item in current if isinstance(item, dict)}:
                issue_uses = runner.json([
                    "issue", "list", "--repo", operation["repo"], "--state", "all",
                    "--label", operation["name"], "--limit", "100", "--json", "url",
                ])
                pr_uses = runner.json([
                    "pr", "list", "--repo", operation["repo"], "--state", "all",
                    "--label", operation["name"], "--limit", "1", "--json", "url",
                ])
                if not isinstance(issue_uses, list) or not isinstance(pr_uses, list):
                    raise WorkError(f"cannot verify label usage in {operation['repo']}")
                if runner.dry_run:
                    issue_uses = [
                        use for use in issue_uses
                        if (canonical_issue_reference(use.get("url", "")), operation["name"])
                        not in pending_issue_label_removals
                    ]
                if issue_uses or pr_uses:
                    skipped_in_use += 1
                    continue
                runner.run(["label", "delete", operation["name"], "--repo", operation["repo"], "--yes"], mutate=True)
                mutated = True
        if not runner.dry_run:
            receipt.mark_restored(operation, mutated=mutated)
        restored += int(mutated)
    json_print({
        "restored_operations": restored,
        "already_restored_operations": already_restored,
        "skipped_labels_in_use": skipped_in_use,
        "dry_run": runner.dry_run,
    })
    return 3 if skipped_in_use else 0


def command_work_graph_create(
    args: argparse.Namespace,
    runner: GhRunner,
    config: dict[str, Any],
    receipt: Receipt,
) -> int:
    repos = parse_repositories(config, args.repos)
    umbrella_repo, _ = parse_issue_url(args.umbrella)
    mutation_preflight(runner, config, [umbrella_repo, *repos])
    created: list[dict[str, Any]] = []
    for repo in repos:
        target = target_for(config, repo)
        title = target.get("work_title") or f"Adopt the GitHub work standard in {repo}"
        child_args = argparse.Namespace(
            repo=repo,
            type="Task",
            title=title,
            body_file=None,
            parent=args.umbrella,
            blocking=None,
            assignee=args.assignee,
        )
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            command_issue_create(child_args, runner, config, receipt)
        created.append(json.loads(captured.getvalue()))
    json_print({"created_tasks": len(created), "issues": created, "umbrella": args.umbrella, "dry_run": runner.dry_run})
    return 0


def provenance_from_text(text: str) -> dict[str, str]:
    matches = list(re.finditer(
        r"github-work-standard: version=(\S+) source=([0-9a-f]{40}) "
        r"target=([0-9a-f]{64}) content=([0-9a-f]{64})",
        text,
    ))
    if len(matches) != 1:
        raise WorkError("github-work-standard requires exactly one valid provenance marker")
    match = matches[0]
    return {
        "version": match.group(1),
        "source": match.group(2),
        "target": match.group(3),
        "content": match.group(4),
    }


def content_without_provenance(text: str, *, managed_region: bool) -> str:
    candidate = text
    if managed_region:
        if candidate.count("BEGIN github-work-standard") != 1 or candidate.count("END github-work-standard") != 1:
            raise WorkError("github-work-standard requires exactly one managed region")
        begin = candidate.find("BEGIN github-work-standard")
        end = candidate.find("END github-work-standard", begin + 1)
        marker = candidate.find("github-work-standard: version=")
        if begin < 0 or end < 0 or not begin < marker < end:
            raise WorkError("github-work-standard provenance must be inside its managed region")
        start = candidate.rfind("\n", 0, begin) + 1
        finish = candidate.find("\n", end)
        candidate = candidate[start : len(candidate) if finish < 0 else finish]
    marker_line = re.compile(
        r"(?:# github-work-standard: version=\S+ source=[0-9a-f]{40} target=[0-9a-f]{64} "
        r"content=[0-9a-f]{64}|<!-- github-work-standard: version=\S+ source=[0-9a-f]{40} "
        r"target=[0-9a-f]{64} content=[0-9a-f]{64} -->)(?:\r?\n)?"
    )
    lines: list[str] = []
    removed = 0
    for line in candidate.splitlines(keepends=True):
        if marker_line.fullmatch(line.strip(" \t")):
            removed += 1
        else:
            lines.append(line)
    if removed != 1:
        raise WorkError("github-work-standard provenance marker must occupy exactly one complete line")
    return "".join(lines)


def verify_content(text: str, marker: dict[str, str], *, managed_region: bool) -> None:
    content = content_without_provenance(text, managed_region=managed_region)
    actual = hashlib.sha256(content.encode("utf-8")).hexdigest()
    if actual != marker["content"]:
        raise WorkError("github-work-standard managed content digest does not match provenance")


def command_standard_check(args: argparse.Namespace) -> int:
    helper_text = Path(__file__).read_text(encoding="utf-8")
    helper = provenance_from_text(helper_text)
    verify_content(helper_text, helper, managed_region=False)
    identity = {key: helper[key] for key in ("version", "source", "target")}
    checked: dict[str, str] = {"helper": str(Path(__file__))}
    paths = [
        ("agents", args.agents_path),
        ("skill", args.skill_path),
        ("pull-request-template", args.pr_template_path),
        *((f"issue-form-{index + 1}", path) for index, path in enumerate(
            args.issue_form_path or [
                ".github/ISSUE_TEMPLATE/bug.yml",
                ".github/ISSUE_TEMPLATE/feature.yml",
                ".github/ISSUE_TEMPLATE/task.yml",
            ]
        )),
    ]
    for label, raw_path in paths:
        path = Path(raw_path)
        if not path.is_file():
            raise WorkError(f"standard-check path is missing: {path}")
        text = path.read_text(encoding="utf-8")
        marker = provenance_from_text(text)
        verify_content(text, marker, managed_region=True)
        if {key: marker[key] for key in identity} != identity:
            raise WorkError(f"{label} provenance does not match helper provenance")
        checked[label] = str(path)
    if args.expected_version and helper["version"] != args.expected_version:
        raise WorkError("standard version does not match --expected-version")
    if args.expected_source_sha and helper["source"] != args.expected_source_sha:
        raise WorkError("standard source does not match --expected-source-sha")
    if args.expected_target_digest and helper["target"] != args.expected_target_digest:
        raise WorkError("standard target digest does not match --expected-target-digest")
    json_print({"current": True, "provenance": helper, "checked": checked})
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", help="JSON-compatible private target configuration")
    parser.add_argument("--ownership-config", help="JSON-compatible private ownership configuration")
    parser.add_argument("--dry-run", action="store_true", help="read and validate but skip mutations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight = subparsers.add_parser("preflight")
    preflight.add_argument("--repos", default="all")
    preflight.add_argument("--json", action="store_true")

    labels = subparsers.add_parser("labels")
    labels_sub = labels.add_subparsers(dest="labels_command", required=True)
    ensure = labels_sub.add_parser("ensure")
    ensure.add_argument("--repos", required=True)
    ensure.add_argument("--receipt", required=True)
    ensure.add_argument("--json", action="store_true")

    issue = subparsers.add_parser("issue-create")
    issue.add_argument("--repo", required=True)
    issue.add_argument("--type", required=True)
    issue.add_argument("--title", required=True)
    issue.add_argument("--body-file")
    issue.add_argument("--parent")
    issue.add_argument("--blocking")
    issue.add_argument("--assignee")
    issue.add_argument("--receipt", required=True)

    pr_link = subparsers.add_parser("pr-link")
    pr_link.add_argument("--pr", required=True)
    pr_link.add_argument("--issue", required=True)
    pr_link.add_argument("--mode", choices=("refs", "closes"), default="refs")
    pr_link.add_argument("--receipt", required=True)

    finality = subparsers.add_parser("finality")
    finality.add_argument("--issue", required=True)
    finality.add_argument("--json", action="store_true")

    assign = subparsers.add_parser("assign")
    assign.add_argument("--issue", required=True)
    group = assign.add_mutually_exclusive_group(required=True)
    group.add_argument("--assignee")
    group.add_argument("--from-ownership-map", action="store_true")
    assign.add_argument("--area")
    assign.add_argument("--receipt", required=True)
    assign.add_argument("--json", action="store_true")

    work_graph = subparsers.add_parser("work-graph")
    work_graph_sub = work_graph.add_subparsers(dest="work_graph_command", required=True)
    work_graph_create = work_graph_sub.add_parser("create")
    work_graph_create.add_argument("--umbrella", required=True)
    work_graph_create.add_argument("--repos", default="all")
    work_graph_create.add_argument("--assignee")
    work_graph_create.add_argument("--receipt", required=True)

    standard_check = subparsers.add_parser("standard-check")
    standard_check.add_argument("--agents-path", default="AGENTS.md")
    standard_check.add_argument("--skill-path", default=".claude/skills/github-work/SKILL.md")
    standard_check.add_argument("--pr-template-path", default=".github/pull_request_template.md")
    standard_check.add_argument(
        "--issue-form-path",
        action="append",
        default=None,
    )
    standard_check.add_argument("--expected-version")
    standard_check.add_argument("--expected-source-sha")
    standard_check.add_argument("--expected-target-digest")

    restore = subparsers.add_parser("restore")
    restore.add_argument("--receipt", required=True)
    return parser


def main(argv: Sequence[str] | None = None, *, runner: GhRunner | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    active_runner = runner or GhRunner(dry_run=args.dry_run)
    active_runner.dry_run = args.dry_run
    try:
        if args.command == "standard-check":
            return command_standard_check(args)
        config = load_targets(args.config)
        config_sha = file_digest(args.config)
        source_sha = active_source_sha()
        ownership = load_json(args.ownership_config) if args.ownership_config else None
        if args.command == "preflight":
            return command_preflight(args, active_runner, config)
        if args.command == "finality":
            return command_finality(args, active_runner, config)
        receipt = Receipt(
            getattr(args, "receipt", None),
            source_sha=source_sha,
            config_digest=config_sha,
        )
        if args.command == "restore":
            return command_restore(args, active_runner, config, receipt)
        if args.command == "labels":
            result = command_labels_ensure(args, active_runner, config, receipt)
        elif args.command == "issue-create":
            result = command_issue_create(args, active_runner, config, receipt)
        elif args.command == "pr-link":
            result = command_pr_link(args, active_runner, config, receipt)
        elif args.command == "assign":
            result = command_assign(args, active_runner, config, ownership, receipt)
        elif args.command == "work-graph":
            result = command_work_graph_create(args, active_runner, config, receipt)
        else:
            raise WorkError(f"unsupported command: {args.command}")
        if result == 0 and not active_runner.dry_run:
            receipt.save()
        return result
    except WorkError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
