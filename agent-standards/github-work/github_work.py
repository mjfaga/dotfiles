#!/usr/bin/env python3
"""Repository-neutral GitHub work lifecycle helper.

Canonical upstream release tag: agent-standards-github-work-v1.0.69

Configuration files use JSON syntax (which is valid YAML) so the helper has no
third-party runtime dependencies.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
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
from typing import Any, Iterable, Iterator, NoReturn, Sequence
from urllib.parse import quote

SCHEMA_VERSION = 3
SUPPORTED_SCHEMA_VERSIONS = frozenset(range(1, SCHEMA_VERSION + 1))
CONFIG_STATUSES = frozenset({"absent", "empty", "invalid", "ok", "unreadable"})
MIN_GH_VERSION = (2, 96, 0)
MANAGED_LABELS = {
    "bug": ("type:bug", "B60205", "Unexpected problem or incorrect behavior"),
    "feature": ("type:feature", "1D76DB", "Requested capability or improvement"),
    "task": ("type:task", "8250DF", "Bounded implementation or follow-up work"),
}
CLOSING_WORDS = ("Closes", "Fixes", "Resolves")
NEEDS_OWNER_LABEL = ("needs-owner", "D876E3", "Ownership requires explicit triage")
RELATIONSHIP_SPECS = (
    ("parent", "sub-issue", "--add-sub-issue"),
    ("blocking", "blocked-by", "--add-blocked-by"),
)


class WorkError(RuntimeError):
    """A hard precondition or mutation failure."""


class RelationshipEndpointUnavailable(WorkError):
    """A live source has no REST relationship endpoint; mutation fallback is required."""


class EligibilityError(WorkError):
    """A reachable repository is missing required issue classification."""


class PartialWorkError(WorkError):
    """A mutation failed after producing structured partial state."""

    def __init__(self, message: str, payload: dict[str, Any]) -> None:
        super().__init__(message)
        self.payload = payload


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
    "issue-label-removed": {"issue", "name"},
    "assignee-added": {"issue", "login"},
}


class Receipt:
    def __init__(
        self,
        path: str | None,
        *,
        source_sha: str,
        config_digest: str | None,
        config_requested: bool = False,
        config_unavailable: bool = False,
        config_status: str = "absent",
        transient: bool = False,
    ) -> None:
        if path == "":
            raise WorkError("receipt path was supplied but is empty")
        if path is None and not transient:
            raise WorkError("receipt path is required; use transient=True for in-memory receipts")
        if path is not None and transient:
            raise WorkError("transient receipts must not have a path")
        self.path = Path(path) if path is not None else None
        self.transient = transient
        self.loaded = bool(self.path and self.path.exists())
        self.source_sha = source_sha
        self.config_digest = config_digest
        self.config_requested = config_requested
        self.config_unavailable = config_unavailable
        self.config_status = config_status
        if config_status not in CONFIG_STATUSES:
            raise WorkError(f"invalid current config status: {config_status}")
        self.data: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "receipt_id": str(uuid.uuid4()),
            "source_sha": source_sha,
            "config_digest": config_digest,
            "operations": [],
        }
        if self.loaded:
            if self.path is None:
                raise WorkError("loaded receipt has no path")
            if stat.S_IMODE(self.path.stat().st_mode) != 0o600:
                raise WorkError("existing receipt permissions must be exactly 0600")
            self.data = load_json(self.path)
            self.validate()

    def validate(self) -> None:
        required = {"schema_version", "receipt_id", "source_sha", "config_digest", "operations"}
        if required - self.data.keys():
            raise WorkError("receipt is missing required metadata")
        if self.data["schema_version"] not in SUPPORTED_SCHEMA_VERSIONS:
            raise WorkError("unsupported receipt schema")
        if not isinstance(self.data["receipt_id"], str) or not self.data["receipt_id"]:
            raise WorkError("receipt_id must be a non-empty string")
        if not isinstance(self.data["source_sha"], str) or not re.fullmatch(
            r"(?:[0-9a-f]{40}|development)", self.data["source_sha"]
        ):
            raise WorkError("receipt source_sha is malformed")
        config_digest = self.data["config_digest"]
        if config_digest is not None and (
            not isinstance(config_digest, str)
            or not re.fullmatch(r"[0-9a-f]{64}", config_digest)
        ):
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
            if self.data["schema_version"] >= 3:
                for attribution_field in ("source_sha", "config_digest"):
                    if operation.get(attribution_field) is None:
                        raise WorkError(
                            f"receipt operation {attribution_field} is required at schema v3"
                        )
            for metadata_field, pattern in (
                ("source_sha", r"(?:[0-9a-f]{40}|development)"),
                ("config_digest", r"[0-9a-f]{64}"),
                ("restored_by_source_sha", r"(?:[0-9a-f]{40}|development)"),
                ("restored_by_config_digest", r"[0-9a-f]{64}"),
            ):
                metadata = operation.get(metadata_field)
                if metadata is not None and (
                    not isinstance(metadata, str) or not re.fullmatch(pattern, metadata)
                ):
                    raise WorkError(f"receipt operation {metadata_field} is malformed")
            for boolean_field in (
                "restore_fallback_succeeded",
                "restore_missing",
                "restore_mutated",
                "restore_unverified",
                "restored_config_requested",
                "restored_config_unavailable",
            ):
                if boolean_field in operation and not isinstance(operation[boolean_field], bool):
                    raise WorkError(f"receipt operation {boolean_field} must be boolean")
            if operation.get("restore_unverified") is True and kind != "relationship-added":
                raise WorkError("restore_unverified is only valid for relationship operations")
            restore_probe_error = operation.get("restore_probe_error")
            if restore_probe_error is not None and (
                not isinstance(restore_probe_error, str) or not restore_probe_error
            ):
                raise WorkError("receipt operation restore_probe_error must be a non-empty string")
            if (
                "restored_config_status" in operation
                and operation["restored_config_status"] not in CONFIG_STATUSES
            ):
                raise WorkError("receipt operation restored_config_status is invalid")
            schema_version = self.data["schema_version"]
            if schema_version >= 2 and operation["status"] == "restored":
                required_restore_fields = {
                    "restored_config_requested",
                    "restored_config_unavailable",
                }
                if schema_version >= 3:
                    required_restore_fields.update({
                        "restore_mutated",
                        "restored_by_config_digest",
                        "restored_by_source_sha",
                        "restored_config_status",
                    })
                missing_restore_fields = required_restore_fields - operation.keys()
                if missing_restore_fields:
                    raise WorkError(
                        "receipt restored operation is missing: "
                        + ", ".join(sorted(missing_restore_fields))
                    )
                if (
                    schema_version >= 3
                    and operation["restored_by_source_sha"] is None
                ):
                    raise WorkError("receipt restored_by_source_sha must not be null")

    def add(self, kind: str, **details: Any) -> None:
        if kind not in OPERATION_FIELDS or OPERATION_FIELDS[kind] - details.keys():
            raise WorkError(f"invalid receipt operation: {kind}")
        for field in ("issue", "source", "target"):
            if field in details and isinstance(details[field], str):
                details[field] = canonical_issue_reference(details[field])
        if "pr" in details and isinstance(details["pr"], str):
            details["pr"] = canonical_pr_reference(details["pr"])
        self.data["operations"].append({
            "operation_id": str(uuid.uuid4()),
            "status": "active",
            "kind": kind,
            "source_sha": self.source_sha,
            "config_digest": self.config_digest,
            **details,
        })
        self.save()

    def mark_restored(
        self,
        operation: dict[str, Any],
        *,
        fallback_succeeded: bool | None = None,
        missing: bool = False,
        mutated: bool,
        probe_error: str | None = None,
        unverified: bool = False,
    ) -> None:
        operation["status"] = "restored"
        if fallback_succeeded is not None:
            operation["restore_fallback_succeeded"] = fallback_succeeded
        operation["restore_missing"] = missing
        operation["restore_mutated"] = mutated
        if probe_error is not None:
            operation["restore_probe_error"] = probe_error
        operation["restore_unverified"] = unverified
        operation["restored_by_source_sha"] = self.source_sha
        operation["restored_by_config_digest"] = self.config_digest
        operation["restored_config_requested"] = self.config_requested
        operation["restored_config_unavailable"] = self.config_unavailable
        operation["restored_config_status"] = self.config_status
        self.save()

    def ensure_saved(self) -> None:
        """Persist the initial empty receipt; no-op after any operation has been saved."""
        if not self.loaded:
            self.save()

    def save(self) -> None:
        self.validate()
        if self.transient:
            self.loaded = True
            return
        if self.path is None:
            raise WorkError("persistent receipt has no path")
        temporary = self.path.with_name(f".{self.path.name}.{uuid.uuid4().hex}.tmp")
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            descriptor = os.open(temporary, flags, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(json.dumps(self.data, indent=2, sort_keys=True) + "\n")
            temporary.replace(self.path)
            self.path.chmod(0o600)
        except OSError as exc:
            with contextlib.suppress(OSError):
                temporary.unlink(missing_ok=True)
            raise WorkError(f"cannot save receipt {self.path}: {exc}") from exc
        self.loaded = True


def load_json(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
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
    source = Path(__file__).read_text(encoding="utf-8", errors="replace")
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
    if path is None:
        raise WorkError("--config is required")
    if not path:
        raise WorkError("--config was supplied but is empty")
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
        for field in required:
            if not isinstance(target[field], str) or not target[field]:
                raise WorkError(f"target field {field} must be a non-empty string")
        if target["repo"] in seen:
            raise WorkError(f"duplicate target: {target['repo']}")
        seen.add(target["repo"])
        if target["adapter"] not in {"generated-modern", "generated-legacy", "plain"}:
            raise WorkError(f"unknown adapter for {target['repo']}: {target['adapter']}")
        if target["classification"] not in {"native-type", "managed-label"}:
            raise WorkError(f"unknown classification for {target['repo']}")
        if "work_title" in target and (
            not isinstance(target["work_title"], str) or not target["work_title"]
        ):
            raise WorkError(f"work_title for {target['repo']} must be a non-empty string")
    auxiliary = config.get("auxiliary_repositories", [])
    if not isinstance(auxiliary, list):
        raise WorkError("auxiliary_repositories must be an array")
    for item in auxiliary:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("repo"), str)
            or not item["repo"]
        ):
            raise WorkError("auxiliary repository entries require a non-empty repo")
        if (
            not isinstance(item.get("classification"), str)
            or not item["classification"]
        ):
            raise WorkError("auxiliary classification must be a non-empty string")
        if item["classification"] not in {"native-type", "managed-label"}:
            raise WorkError(f"unknown auxiliary classification for {item.get('repo')}")
        if "work_title" in item and (
            not isinstance(item["work_title"], str) or not item["work_title"]
        ):
            raise WorkError(f"work_title for {item['repo']} must be a non-empty string")
        if "adapter" in item:
            if not isinstance(item["adapter"], str) or not item["adapter"]:
                raise WorkError(f"adapter for {item['repo']} must be a non-empty string")
            if item["adapter"] not in {"generated-modern", "generated-legacy", "plain"}:
                raise WorkError(f"unknown adapter for {item['repo']}: {item['adapter']}")
        if item["repo"] in seen:
            raise WorkError(f"duplicate repository configuration: {item['repo']}")
        seen.add(item["repo"])
    return config


def load_ownership(path: str | Path) -> dict[str, Any]:
    config = load_json(path)
    mappings = config.get("mappings")
    if not isinstance(mappings, list):
        raise WorkError("ownership config requires a mappings array")
    for mapping in mappings:
        if not isinstance(mapping, dict):
            raise WorkError("every ownership mapping must be an object")
        if not isinstance(mapping.get("repo"), str) or not mapping["repo"]:
            raise WorkError("ownership mapping repo must be a non-empty string")
        if "area" in mapping and (
            not isinstance(mapping["area"], str) or not mapping["area"]
        ):
            raise WorkError("ownership mapping area must be a non-empty string when present")
        logins = mapping.get("logins")
        if not isinstance(logins, list) or not logins or any(
            not isinstance(login, str) or not login for login in logins
        ):
            raise WorkError("ownership mapping logins must be a non-empty array of strings")
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
    repository = r"[A-Za-z0-9._-]+/[A-Za-z0-9._-]+"
    match = re.fullmatch(
        rf"https://github\.com/({repository})/issues/(\d+)(?:[?#].*)?",
        value,
    )
    if match:
        return match.group(1), int(match.group(2))
    match = re.fullmatch(rf"({repository})#(\d+)", value)
    if match:
        return match.group(1), int(match.group(2))
    raise WorkError(f"expected issue URL or OWNER/REPO#N: {value}")


def issue_url(repo: str, number: int) -> str:
    return f"https://github.com/{repo}/issues/{number}"


def canonical_issue_reference(value: str) -> str:
    return issue_url(*parse_issue_url(value))


def parse_pr_url(value: str) -> tuple[str, int]:
    repository = r"[A-Za-z0-9._-]+/[A-Za-z0-9._-]+"
    match = re.fullmatch(
        rf"https://github\.com/({repository})/pull/(\d+)(?:[?#].*)?",
        value,
    )
    if not match:
        raise WorkError(f"expected pull request URL: {value}")
    return match.group(1), int(match.group(2))


def canonical_pr_reference(value: str) -> str:
    repo, number = parse_pr_url(value)
    return f"https://github.com/{repo}/pull/{number}"


def json_print(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


@contextmanager
def temporary_body(content: str) -> Iterator[str]:
    path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", delete=False, suffix=".md", encoding="utf-8"
        ) as handle:
            path = Path(handle.name)
            handle.write(content)
    except OSError as exc:
        if path is not None:
            with contextlib.suppress(OSError):
                path.unlink(missing_ok=True)
        raise WorkError(f"cannot write temporary body file: {exc}") from exc
    if path is None:
        raise WorkError("temporary body path was not created")
    try:
        yield str(path)
    finally:
        with contextlib.suppress(OSError):
            path.unlink(missing_ok=True)


def write_recovery_file(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        handle = os.fdopen(descriptor, "w", encoding="utf-8")
    except BaseException:
        with contextlib.suppress(OSError):
            os.close(descriptor)
        raise
    with handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    path.chmod(0o600)


def recovery_fields() -> dict[str, Any]:
    return {
        "recovery_error": None,
        "recovery_fallback_attempted_path": None,
        "recovery_fallback_detail": None,
        "recovery_fallback_errno": None,
        "recovery_fallback_used": False,
        "recovery_path": None,
        "recovery_primary_attempted_path": None,
        "recovery_primary_detail": None,
        "recovery_primary_errno": None,
    }


def recovery_error_fields(exc: BaseException, prefix: str, attempted_path: Path) -> dict[str, Any]:
    return {
        f"recovery_{prefix}_attempted_path": str(attempted_path),
        f"recovery_{prefix}_detail": getattr(exc, "strerror", None) or str(exc) or None,
        f"recovery_{prefix}_errno": getattr(exc, "errno", None),
    }


def write_private_recovery_payload(
    payload: dict[str, Any],
    receipt_path: Path | None,
) -> dict[str, Any]:
    result = recovery_fields()
    if receipt_path is None:
        result["recovery_error"] = "receipt-path-unavailable"
        return result
    primary_path = receipt_path.parent / (
        f"{receipt_path.name or 'receipt'}.github-work-recovery-{uuid.uuid4()}.json"
    )
    try:
        write_recovery_file(primary_path, payload)
        result["recovery_path"] = str(primary_path)
        result["recovery_primary_attempted_path"] = str(primary_path)
        return result
    except Exception as primary_error:
        result.update(recovery_error_fields(primary_error, "primary", primary_path))
        with contextlib.suppress(OSError):
            primary_path.unlink(missing_ok=True)
    fallback_path = Path(tempfile.gettempdir()) / f"github-work-recovery-{uuid.uuid4()}.json"
    result["recovery_fallback_attempted_path"] = str(fallback_path)
    try:
        write_recovery_file(fallback_path, payload)
        result["recovery_error"] = "primary-write-failed"
        result["recovery_fallback_used"] = True
        result["recovery_path"] = str(fallback_path)
        return result
    except Exception as fallback_error:
        result.update(recovery_error_fields(fallback_error, "fallback", fallback_path))
        with contextlib.suppress(OSError):
            fallback_path.unlink(missing_ok=True)
        result["recovery_error"] = "primary-and-fallback-write-failed"
        return result


def pr_link_partial_payload(
    args: argparse.Namespace,
    before: str,
    recovery: dict[str, Any],
    stage: str,
) -> dict[str, Any]:
    return {
        "before_length": len(before),
        "before_sha256": hashlib.sha256(before.encode("utf-8")).hexdigest(),
        "issue": canonical_issue_reference(args.issue),
        "mode": args.mode,
        "partial": True,
        "pr": canonical_pr_reference(args.pr),
        "stage": stage,
        **recovery,
    }


def gh_version(runner: GhRunner) -> tuple[int, int, int]:
    text = runner.run(["version"]).stdout
    match = re.search(r"gh version (\d+)\.(\d+)\.(\d+)", text)
    if not match:
        raise WorkError("cannot parse gh version")
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def issue_state(
    runner: GhRunner,
    value: str,
    *,
    include_relationships: bool = False,
) -> dict[str, Any]:
    fields = "url,state,labels,assignees,title,body"
    if include_relationships:
        fields += ",subIssuesSummary,blockedBy"
    state = runner.json([
        "issue", "view", value,
        "--json", fields,
    ])
    if not isinstance(state, dict):
        raise WorkError(f"cannot verify issue state: {value}")
    return state


def restore_issue_state(runner: GhRunner, value: str) -> dict[str, Any] | None:
    """Read issue state, returning None only when exact REST lookup confirms deletion."""
    try:
        return issue_state(runner, value)
    except WorkError as state_error:
        repo, number = parse_issue_url(value)
        result = runner.run(["api", f"repos/{repo}/issues/{number}"], check=False)
        detail = f"{result.stderr}\n{result.stdout}".lower()
        if result.returncode != 0 and "http 404" in detail:
            return None
        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
            raise WorkError(f"cannot verify referenced issue {value}: {message}") from state_error
        raise state_error


def restore_relationship_state(
    runner: GhRunner,
    endpoint: str,
    response_name: str,
    source: str,
) -> list[str] | None:
    """Return canonical related issue URLs, or None when the source was deleted."""
    result = runner.run(["api", endpoint, "--paginate", "--slurp"], check=False)
    if result.returncode != 0:
        detail = f"{result.stderr}\n{result.stdout}".lower()
        message = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        if "http 404" in detail:
            if restore_issue_state(runner, source) is None:
                return None
            raise RelationshipEndpointUnavailable(
                f"{response_name} endpoint unavailable for live source {source}: {message}"
            )
        raise WorkError(f"cannot verify {response_name} relationships for {source}: {message}")
    try:
        pages = json.loads(result.stdout or "null")
    except json.JSONDecodeError as exc:
        raise WorkError(f"{response_name} paginated response is not valid JSON") from exc
    if not isinstance(pages, list) or any(not isinstance(page, list) for page in pages):
        raise WorkError(f"{response_name} paginated response must be an array of pages")
    canonical_urls: list[str] = []
    for item in (item for page in pages for item in page):
        if not isinstance(item, dict) or not isinstance(item.get("html_url"), str):
            raise WorkError(f"{response_name} response lacks html_url entries")
        try:
            canonical_urls.append(canonical_issue_reference(item["html_url"]))
        except WorkError as exc:
            raise WorkError(
                f"{response_name} response contains an invalid issue URL: {item['html_url']}"
            ) from exc
    return canonical_urls


def issue_read_preflight(runner: GhRunner, repo: str) -> None:
    """Prove issue-read scope before interpreting resource 404s as absence."""
    result = runner.run(["api", f"repos/{repo}/issues?per_page=1"], check=False)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise WorkError(f"cannot verify issue read access for restore in {repo}: {message}")


def issue_labels(state: dict[str, Any]) -> set[str]:
    return {item["name"] for item in state.get("labels", [])}


def issue_assignees(state: dict[str, Any]) -> set[str]:
    return {item["login"] for item in state.get("assignees", [])}


def repository_labels(
    runner: GhRunner,
    repo: str,
    *,
    check: bool = True,
) -> list[dict[str, Any]] | None:
    pages = runner.json(
        ["api", f"repos/{repo}/labels?per_page=100", "--paginate", "--slurp"],
        check=check,
    )
    if pages is None:
        return None
    if not isinstance(pages, list) or any(not isinstance(page, list) for page in pages):
        raise WorkError(f"cannot read labels for {repo}: malformed paginated response")
    labels = [item for page in pages for item in page]
    if any(not isinstance(item, dict) for item in labels):
        raise WorkError(f"cannot read labels for {repo}: malformed label entry")
    return labels


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
        current = repository_labels(runner, repo, check=False)
        if current is None:
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
        current = repository_labels(runner, repo) or []
        by_name = {item["name"]: item for item in current}
        for name, color, description in MANAGED_LABELS.values():
            if name in by_name:
                unchanged += 1
                continue
            label = {"repo": repo, "name": name}
            try:
                runner.run([
                    "label", "create", name, "--repo", repo,
                    "--color", color, "--description", description,
                ], mutate=True)
            except WorkError:
                json_print({
                    "created": created,
                    "failed_label": label,
                    "partial": True,
                    "stage": "mutation-result-unknown",
                })
                raise
            if not runner.dry_run:
                try:
                    receipt.add("label-created", repo=repo, name=name)
                except WorkError:
                    json_print({
                        "created": created,
                        "failed_label": label,
                        "partial": True,
                        "stage": "audit",
                    })
                    raise
            created.append(label)
    if not runner.dry_run:
        receipt.ensure_saved()
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


def raise_issue_partial(
    exc: WorkError,
    args: argparse.Namespace,
    created_url: str | None,
    *,
    emit: bool,
    stage: str,
    relationship: dict[str, str] | None = None,
    relationship_added: bool | None = False,
    completed_relationships: list[dict[str, str]] | None = None,
) -> NoReturn:
    requested_relationships = [
        {"relation": relation, "source": canonical_issue_reference(source)}
        for attribute, relation, _ in RELATIONSHIP_SPECS
        if (source := getattr(args, attribute, None))
    ]
    payload = {
        "completed_relationships": completed_relationships or [],
        "partial": True,
        "relationship": relationship,
        "relationship_added": relationship_added,
        "repo": args.repo,
        "requested_relationships": requested_relationships,
        "stage": stage,
        "title": args.title,
        "type": args.type,
        "url": created_url,
    }
    if emit:
        json_print(payload)
    raise PartialWorkError(str(exc), payload) from exc


def command_issue_create(
    args: argparse.Namespace,
    runner: GhRunner,
    config: dict[str, Any],
    receipt: Receipt,
    *,
    emit: bool = True,
) -> dict[str, Any]:
    target = target_for(config, args.repo)
    related_repos = [args.repo]
    if args.parent:
        related_repos.append(parse_issue_url(args.parent)[0])
    if args.blocking:
        related_repos.append(parse_issue_url(args.blocking)[0])
    if not getattr(args, "preflighted", False):
        mutation_preflight(runner, config, related_repos)
    kind = args.type.lower()
    if kind not in MANAGED_LABELS:
        raise WorkError("--type must be Bug, Feature, or Task")
    if args.assignee:
        validation = runner.run(["api", f"repos/{args.repo}/assignees/{quote(args.assignee, safe='')}"], check=False)
        if validation.returncode != 0:
            raise WorkError(f"not assignable in {args.repo}: {args.assignee}")
    try:
        body = (
            Path(args.body_file).read_text(encoding="utf-8")
            if args.body_file
            else default_issue_body(args.type, args.title)
        )
    except (OSError, UnicodeDecodeError) as exc:
        raise WorkError(f"cannot read issue body file: {exc}") from exc
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
        payload = {"dry_run": True, "repo": args.repo, "type": args.type}
        if emit:
            json_print(payload)
        return payload
    output_lines = result.stdout.strip().splitlines()
    if not output_lines:
        raise_issue_partial(
            WorkError("gh issue create returned no issue URL"),
            args,
            None,
            emit=emit,
            stage="mutation-result-unknown",
            relationship_added=None,
        )
    created_url = output_lines[-1]
    try:
        parse_issue_url(created_url)
    except WorkError as exc:
        raise_issue_partial(
            exc,
            args,
            created_url,
            emit=emit,
            stage="mutation-result-unknown",
            relationship_added=None,
        )
    relationships = [
        ({
            "relation": relation,
            "source": canonical_issue_reference(source),
            "target": canonical_issue_reference(created_url),
        }, flag)
        for attribute, relation, flag in RELATIONSHIP_SPECS
        if (source := getattr(args, attribute, None))
    ]
    completed_relationships: list[dict[str, str]] = []
    next_relationship = relationships[0][0] if relationships else None
    try:
        receipt.add("issue-created", issue=created_url)
    except WorkError as exc:
        raise_issue_partial(
            exc,
            args,
            created_url,
            emit=emit,
            stage="audit",
            relationship=next_relationship,
            completed_relationships=completed_relationships,
        )
    if target["classification"] == "managed-label":
        try:
            receipt.add("issue-label-added", issue=created_url, name=MANAGED_LABELS[kind][0])
        except WorkError as exc:
            raise_issue_partial(
                exc,
                args,
                created_url,
                emit=emit,
                stage="audit",
                relationship=next_relationship,
                completed_relationships=completed_relationships,
            )
    for relationship, flag in relationships:
        relationship_command = [
            "issue", "edit", relationship["source"], flag, created_url,
        ]
        try:
            runner.run(relationship_command, mutate=True)
        except WorkError as exc:
            raise_issue_partial(
                exc,
                args,
                created_url,
                emit=emit,
                stage="mutation-result-unknown",
                relationship=relationship,
                relationship_added=None,
                completed_relationships=completed_relationships,
            )
        try:
            receipt.add("relationship-added", **relationship)
        except WorkError as exc:
            raise_issue_partial(
                exc,
                args,
                created_url,
                emit=emit,
                stage="audit",
                relationship=relationship,
                relationship_added=True,
                completed_relationships=completed_relationships,
            )
        completed_relationships.append(relationship)
    payload = {"url": created_url, "repo": args.repo, "type": args.type}
    if emit:
        json_print(payload)
    return payload


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
    target = target_reference_pattern(issue, pr_repo)
    closing_keyword = r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)"
    closing_line = re.compile(
        rf"^(?P<prefix>\s*(?:[-*]\s+)?){closing_keyword}\s+"
        rf"(?P<reference>{target.pattern})\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    demoted = closing_line.sub(
        lambda match: f"{match.group('prefix')}Refs {match.group('reference')}",
        body,
    )
    closing_in_prose = re.compile(
        rf"(?P<keyword>\b{closing_keyword})\s+(?P<reference>{target.pattern})",
        re.IGNORECASE,
    )
    demoted = closing_in_prose.sub(
        lambda match: (
            f"{match.group('keyword')} <!-- github-work: non-closing --> "
            f"{match.group('reference')}"
        ),
        demoted,
    )
    placeholder = re.compile(r"\bRefs\s+#ISSUE\b", re.IGNORECASE)
    if placeholder.search(demoted):
        return placeholder.sub(f"{keyword} {reference}", demoted, count=1).rstrip() + "\n"
    refs = re.compile(rf"\bRefs\s+(?P<reference>{target.pattern})", re.IGNORECASE)
    if mode == "refs":
        if refs.search(demoted):
            return demoted.rstrip() + "\n"
        desired = f"Refs {reference}"
        return demoted.rstrip() + ("\n\n" if demoted.strip() else "") + desired + "\n"
    desired = f"Closes {reference}"
    work_item = re.compile(r"(?ms)(^## Work item[^\n]*\n.*?)(?=^## |\Z)")
    section_match = work_item.search(demoted)
    if section_match:
        section = section_match.group(1)
        if refs.search(section):
            section = refs.sub(desired, section, count=1)
        else:
            section = section.rstrip() + "\n\n" + desired + "\n"
        demoted = demoted[: section_match.start(1)] + section + demoted[section_match.end(1) :]
        return demoted.rstrip() + "\n"
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
        finality = finality_result(
            issue_state(runner, args.issue, include_relationships=True)
        )
        if not finality["eligible"]:
            json_print({
                "changed": False,
                "finality": finality,
                "mode": args.mode,
                "pr": canonical_pr_reference(args.pr),
            })
            return 1
    current = runner.json(["pr", "view", args.pr, "--json", "body,url"])
    if not isinstance(current, dict):
        raise WorkError(f"cannot read pull request: {args.pr}")
    before = current.get("body") or ""
    after = linked_body(before, args.issue, args.mode, pr_repo)
    if before == after:
        if not runner.dry_run:
            receipt.ensure_saved()
        json_print({
            "changed": False,
            "pr": canonical_pr_reference(args.pr),
            "mode": args.mode,
        })
        return 0
    with temporary_body(after) as path:
        try:
            runner.run(["pr", "edit", args.pr, "--body-file", path], mutate=True)
        except WorkError:
            recovery = write_private_recovery_payload(
                {"after": after, "before": before}, receipt.path
            )
            json_print(pr_link_partial_payload(
                args,
                before,
                recovery,
                "mutation-result-unknown",
            ))
            raise
    if not runner.dry_run:
        try:
            receipt.add("pr-body-changed", pr=args.pr, before=before, after=after)
            receipt.ensure_saved()
        except WorkError:
            recovery = write_private_recovery_payload(
                {"after": after, "before": before}, receipt.path
            )
            json_print(pr_link_partial_payload(
                args,
                before,
                recovery,
                "audit",
            ))
            raise
    json_print({
        "changed": True,
        "dry_run": runner.dry_run,
        "pr": canonical_pr_reference(args.pr),
        "mode": args.mode,
    })
    return 0


def finality_result(state: dict[str, Any]) -> dict[str, Any]:
    blocked_by = state.get("blockedBy")
    if not isinstance(blocked_by, dict):
        raise WorkError("finality response lacks a valid blockedBy connection")
    blockers = blocked_by.get("nodes")
    total_blockers = blocked_by.get("totalCount")
    if (
        not isinstance(blockers, list)
        or not isinstance(total_blockers, int)
        or isinstance(total_blockers, bool)
        or total_blockers != len(blockers)
    ):
        raise WorkError("finality blockedBy connection is incomplete")
    if "subIssuesSummary" not in state or not isinstance(state["subIssuesSummary"], dict):
        raise WorkError("finality response lacks a valid subIssuesSummary object")
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
        "reason": "ready" if eligible else "not_ready",
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
    result = finality_result(
        issue_state(runner, args.issue, include_relationships=True)
    )
    json_print(result)
    return 0 if result["eligible"] else 1


def ownership_resolution(
    config: dict[str, Any], repo: str, area: str | None
) -> tuple[list[str], str]:
    """Resolve a validated ownership config with fail-closed explicit-area matching."""
    mappings = [mapping for mapping in config["mappings"] if mapping["repo"] == repo]
    defaults = [mapping for mapping in mappings if "area" not in mapping]
    wildcards = [mapping for mapping in mappings if mapping.get("area") == "*"]
    selected: list[dict[str, Any]] = []
    if not mappings:
        source = "repo-unmapped"
    elif area is not None:
        exact = [mapping for mapping in mappings if mapping.get("area") == area]
        if area == "*" and wildcards:
            selected, source = wildcards, "wildcard"
        elif exact:
            selected, source = exact, "exact"
        elif wildcards:
            selected, source = wildcards, "wildcard"
        elif defaults:
            source = "default-ineligible"
        else:
            source = "area-unmapped"
    else:
        specific = [mapping for mapping in mappings if mapping.get("area") not in {None, "*"}]
        if defaults:
            selected, source = defaults, "default"
        elif wildcards:
            selected, source = wildcards, "wildcard"
        elif specific:
            selected, source = specific, "specific-union"
        else:
            raise WorkError("validated ownership mappings could not be resolved")
    candidates = sorted({login for mapping in selected for login in mapping["logins"]})
    return candidates, source


def ownership_candidates(config: dict[str, Any], repo: str, area: str | None) -> list[str]:
    return ownership_resolution(config, repo, area)[0]


def add_needs_owner(
    runner: GhRunner,
    issue: str,
    receipt: Receipt,
    candidates: list[str],
    ownership_source: str,
    state: dict[str, Any],
) -> None:
    if NEEDS_OWNER_LABEL[0] in issue_labels(state):
        return
    repo, _ = parse_issue_url(issue)
    labels = repository_labels(runner, repo)
    if labels is None:
        raise WorkError(f"cannot verify ownership labels in {repo}")
    label_created = False
    if NEEDS_OWNER_LABEL[0] not in {item.get("name") for item in labels if isinstance(item, dict)}:
        try:
            runner.run([
                "label", "create", NEEDS_OWNER_LABEL[0], "--repo", repo,
                "--color", NEEDS_OWNER_LABEL[1], "--description", NEEDS_OWNER_LABEL[2],
            ], mutate=True)
        except WorkError:
            json_print({
                "action": "create-label",
                "candidates": candidates,
                "dry_run": runner.dry_run,
                "issue": canonical_issue_reference(issue),
                "name": NEEDS_OWNER_LABEL[0],
                "needs_owner_removed": False,
                "ownership_source": ownership_source,
                "partial": True,
                "repo": repo,
                "stage": "mutation-result-unknown",
            })
            raise
        label_created = not runner.dry_run
        if not runner.dry_run:
            try:
                receipt.add("label-created", repo=repo, name=NEEDS_OWNER_LABEL[0])
            except WorkError:
                json_print({
                    "action": "create-label",
                    "candidates": candidates,
                    "dry_run": runner.dry_run,
                    "issue": canonical_issue_reference(issue),
                    "name": NEEDS_OWNER_LABEL[0],
                    "needs_owner_removed": False,
                    "ownership_source": ownership_source,
                    "partial": True,
                    "repo": repo,
                    "stage": "audit",
                })
                raise
    try:
        runner.run(["issue", "edit", issue, "--add-label", NEEDS_OWNER_LABEL[0]], mutate=True)
    except WorkError:
        json_print({
            "action": "add-label",
            "candidates": candidates,
            "dry_run": runner.dry_run,
            "issue": canonical_issue_reference(issue),
            "label_created": label_created,
            "name": NEEDS_OWNER_LABEL[0],
            "needs_owner_removed": False,
            "ownership_source": ownership_source,
            "partial": True,
            "repo": repo,
            "stage": "mutation-result-unknown",
        })
        raise
    if not runner.dry_run:
        try:
            receipt.add("issue-label-added", issue=issue, name=NEEDS_OWNER_LABEL[0])
        except WorkError:
            json_print({
                "action": "add-label",
                "candidates": candidates,
                "dry_run": runner.dry_run,
                "issue": canonical_issue_reference(issue),
                "label_created": label_created,
                "name": NEEDS_OWNER_LABEL[0],
                "needs_owner_removed": False,
                "ownership_source": ownership_source,
                "partial": True,
                "repo": repo,
                "stage": "audit",
            })
            raise


def validate_cli_args(args: argparse.Namespace) -> None:
    """Reject supplied-but-empty or incompatible string options."""
    attributes = ["receipt", "assignee", "parent", "blocking", "body_file", "title"]
    command = getattr(args, "command", None)
    if command not in {"restore", "standard-check"}:
        attributes.extend(("config", "ownership_config"))
    for attribute in attributes:
        value = getattr(args, attribute, None)
        if value is not None and not value:
            option = attribute.replace("_", "-")
            raise WorkError(f"--{option} was supplied but is empty")
    area = getattr(args, "area", None)
    if area is not None:
        if not area:
            raise WorkError("--area was supplied but is empty")
        if not getattr(args, "from_ownership_map", False):
            raise WorkError("--area requires --from-ownership-map")


def remove_needs_owner(
    runner: GhRunner,
    issue: str,
    state: dict[str, Any],
    receipt: Receipt,
    context: dict[str, Any],
) -> bool:
    """Remove a stale needs-owner label and record the reversible mutation."""
    if NEEDS_OWNER_LABEL[0] not in issue_labels(state):
        return False
    live_state = issue_state(runner, issue)
    if NEEDS_OWNER_LABEL[0] not in issue_labels(live_state):
        return False
    try:
        result = runner.run(
            ["issue", "edit", issue, "--remove-label", NEEDS_OWNER_LABEL[0]],
            mutate=True,
            check=False,
        )
        if result.returncode != 0:
            detail = f"{result.stderr}\n{result.stdout}".lower()
            if any(
                marker in detail
                for marker in ("label not found", "label does not exist", "not labeled")
            ):
                return False
            raise WorkError(result.stderr.strip() or result.stdout.strip() or "label removal failed")
    except WorkError:
        json_print({
            **context,
            "action": "remove-label",
            "issue": canonical_issue_reference(issue),
            "name": NEEDS_OWNER_LABEL[0],
            "needs_owner_removed": None,
            "partial": True,
            "stage": "mutation-result-unknown",
        })
        raise
    if not runner.dry_run:
        try:
            receipt.add("issue-label-removed", issue=issue, name=NEEDS_OWNER_LABEL[0])
        except WorkError:
            json_print({
                **context,
                "action": "remove-label",
                "issue": canonical_issue_reference(issue),
                "name": NEEDS_OWNER_LABEL[0],
                "needs_owner_removed": None,
                "partial": True,
                "stage": "audit",
            })
            raise
    return True


def command_assign(
    args: argparse.Namespace,
    runner: GhRunner,
    config: dict[str, Any],
    ownership: dict[str, Any] | None,
    receipt: Receipt,
) -> int:
    # Keep the CLI invariant for direct in-process callers too.
    validate_cli_args(args)
    repo, _ = parse_issue_url(args.issue)
    mutation_preflight(runner, config, [repo])
    assignee = args.assignee
    ownership_source = "explicit"
    state: dict[str, Any] | None = None
    if args.from_ownership_map:
        if ownership is None:
            # In-process callers may bypass main's ownership-config validation.
            raise WorkError("--ownership-config is required with --from-ownership-map")
        candidates, ownership_source = ownership_resolution(ownership, repo, args.area)
        candidates = [candidate for candidate in candidates if not candidate.endswith("[bot]")]
        state = issue_state(runner, args.issue)
        human_assignees = sorted(
            login for login in issue_assignees(state) if not login.endswith("[bot]")
        )
        resolved_assignee = candidates[0] if len(candidates) == 1 else None
        if human_assignees and (
            resolved_assignee is None or resolved_assignee in human_assignees
        ):
            needs_owner_removed = remove_needs_owner(
                runner,
                args.issue,
                state,
                receipt,
                {
                    "assignee": resolved_assignee,
                    "assignee_added": False,
                    "assignees": human_assignees,
                    "candidates": candidates,
                    "ownership_source": ownership_source,
                },
            )
            if not runner.dry_run:
                receipt.ensure_saved()
            json_print({
                "assigned": False,
                "assignee": resolved_assignee,
                "assignees": human_assignees,
                "candidates": candidates,
                "dry_run": runner.dry_run,
                "needs_owner_removed": needs_owner_removed,
                "ownership_source": ownership_source,
                "reason": "already-assigned" if resolved_assignee else "existing-owner",
            })
            return 0
        if len(candidates) != 1:
            add_needs_owner(
                runner, args.issue, receipt, candidates, ownership_source, state
            )
            if not runner.dry_run:
                receipt.ensure_saved()
            json_print({
                "assigned": False,
                "candidates": candidates,
                "dry_run": runner.dry_run,
                "needs_owner_removed": False,
                "ownership_source": ownership_source,
                "reason": "zero-matches" if not candidates else "multiple-matches",
            })
            return 0
        assignee = candidates[0]
    if not assignee:
        raise WorkError("provide --assignee or --from-ownership-map")
    if assignee.endswith("[bot]"):
        raise WorkError("bot identities cannot be planned issue owners")
    if state is None:
        state = issue_state(runner, args.issue)
    if assignee in issue_assignees(state):
        assignees = sorted(
            login for login in issue_assignees(state) if not login.endswith("[bot]")
        )
        needs_owner_removed = remove_needs_owner(
            runner,
            args.issue,
            state,
            receipt,
            {
                "assignee": assignee,
                "assignee_added": False,
                "assignees": assignees,
                "candidates": [assignee],
                "ownership_source": ownership_source,
            },
        )
        if not runner.dry_run:
            receipt.ensure_saved()
        json_print({
            "assigned": False,
            "assignee": assignee,
            "assignees": assignees,
            "candidates": [assignee],
            "dry_run": runner.dry_run,
            "needs_owner_removed": needs_owner_removed,
            "ownership_source": ownership_source,
            "reason": "already-assigned",
        })
        return 0
    validation = runner.run(["api", f"repos/{repo}/assignees/{quote(assignee, safe='')}"], check=False)
    if validation.returncode != 0:
        raise WorkError(f"not assignable in {repo}: {assignee}")
    try:
        runner.run(["issue", "edit", args.issue, "--add-assignee", assignee], mutate=True)
    except WorkError:
        json_print({
            "assignee": assignee,
            "dry_run": runner.dry_run,
            "issue": canonical_issue_reference(args.issue),
            "needs_owner_removed": False,
            "ownership_source": ownership_source,
            "partial": True,
            "stage": "mutation-result-unknown",
        })
        raise
    if not runner.dry_run:
        try:
            receipt.add("assignee-added", issue=args.issue, login=assignee)
            receipt.ensure_saved()
        except WorkError:
            json_print({
                "assignee": assignee,
                "dry_run": runner.dry_run,
                "issue": canonical_issue_reference(args.issue),
                "needs_owner_removed": False,
                "ownership_source": ownership_source,
                "partial": True,
                "stage": "audit",
            })
            raise
    needs_owner_removed = remove_needs_owner(
        runner,
        args.issue,
        state,
        receipt,
        {
            "assignee": assignee,
            "assignee_added": not runner.dry_run,
            "assignees": sorted({
                login for login in issue_assignees(state) if not login.endswith("[bot]")
            } | {assignee}),
            "candidates": [assignee],
            "ownership_source": ownership_source,
        },
    )
    json_print({
        "assigned": True,
        "assignee": assignee,
        "dry_run": runner.dry_run,
        "needs_owner_removed": needs_owner_removed,
        "ownership_source": ownership_source,
    })
    return 0


def restore_pr_body(
    runner: GhRunner,
    operation: dict[str, Any],
    simulated_bodies: dict[str, str] | None = None,
) -> bool:
    pr = operation["pr"]
    simulation_key = canonical_pr_reference(pr)
    if (
        runner.dry_run
        and simulated_bodies is not None
        and simulation_key in simulated_bodies
    ):
        body = simulated_bodies[simulation_key]
    else:
        current = runner.json(["pr", "view", pr, "--json", "body"])
        if not isinstance(current, dict):
            raise WorkError(f"cannot read pull request: {pr}")
        body = current.get("body") or ""
    if body == operation["before"]:
        return False
    if body != operation["after"]:
        raise WorkError(f"refusing to overwrite independently changed PR body: {pr}")
    with temporary_body(operation["before"]) as path:
        runner.run(["pr", "edit", pr, "--body-file", path], mutate=True)
    if runner.dry_run and simulated_bodies is not None:
        simulated_bodies[simulation_key] = operation["before"]
    return True


def receipt_repositories(receipt: Receipt) -> set[str]:
    repos: set[str] = set()
    for operation in receipt.data["operations"]:
        if operation.get("status") != "active":
            continue
        for key in ("issue", "source", "target"):
            if key in operation:
                repos.add(parse_issue_url(operation[key])[0])
        if "pr" in operation:
            repos.add(parse_pr_url(operation["pr"])[0])
        if "repo" in operation:
            repos.add(operation["repo"])
    return repos


def receipt_issue_repositories(receipt: Receipt) -> set[str]:
    """Return repositories whose active compensation needs issue-scoped reads."""
    repos: set[str] = set()
    for operation in receipt.data["operations"]:
        if operation.get("status") != "active" or operation.get("kind") == "pr-body-changed":
            continue
        if isinstance(operation.get("repo"), str):
            repos.add(operation["repo"])
        references = [operation.get("issue", operation.get("source"))]
        if operation.get("kind") == "relationship-added":
            references.append(operation.get("target"))
        for reference in references:
            if isinstance(reference, str):
                repos.add(parse_issue_url(reference)[0])
    return repos


def operation_repositories(operation: dict[str, Any]) -> set[str]:
    repos: set[str] = set()
    if operation.get("kind") == "pr-body-changed":
        repos.add(parse_pr_url(operation["pr"])[0])
    if isinstance(operation.get("repo"), str):
        repos.add(operation["repo"])
    for key in ("issue", "source", "target"):
        reference = operation.get(key)
        if isinstance(reference, str):
            repos.add(parse_issue_url(reference)[0])
    return repos


def unverified_relationship_details(operation: dict[str, Any]) -> dict[str, Any]:
    return {
        "fallback_succeeded": operation.get("restore_fallback_succeeded"),
        "probe_error": operation.get("restore_probe_error"),
        "relation": operation["relation"],
        "source": operation["source"],
        "target": operation["target"],
    }


def command_restore(
    args: argparse.Namespace,
    runner: GhRunner,
    receipt: Receipt,
) -> int:
    if not receipt.data["operations"]:
        if not receipt.loaded:
            raise WorkError(f"receipt not found: {receipt.path}")
        json_print({
            "already_restored_operations": 0,
            "blocked_repositories": [],
            "config_requested": receipt.config_requested,
            "config_status": receipt.config_status,
            "config_unavailable": receipt.config_unavailable,
            "dry_run": runner.dry_run,
            "missing_issue_operations": 0,
            "mutated_operations": 0,
            "reason": "empty",
            "unverified_relationship_operations": 0,
            "unverified_relationships": [],
            "standing_missing_operations": 0,
            "standing_unverified_operations": 0,
            "restored_operations": 0,
            "retained_label_definitions": 0,
            "skipped_labels_in_use": 0,
            "total_operations": 0,
        })
        return 0
    standing_missing = sum(
        operation.get("status") == "restored" and operation.get("restore_missing") is True
        for operation in receipt.data["operations"]
    )
    standing_unverified_details = [
        unverified_relationship_details(operation)
        for operation in receipt.data["operations"]
        if operation.get("status") == "restored"
        and operation.get("restore_unverified") is True
    ]
    standing_unverified = len(standing_unverified_details)
    if all(operation["status"] == "restored" for operation in receipt.data["operations"]):
        json_print({
            "already_restored_operations": len(receipt.data["operations"]),
            "blocked_repositories": [],
            "config_requested": receipt.config_requested,
            "config_status": receipt.config_status,
            "config_unavailable": receipt.config_unavailable,
            "dry_run": runner.dry_run,
            "missing_issue_operations": 0,
            "mutated_operations": 0,
            "reason": "already_restored",
            "unverified_relationship_operations": 0,
            "unverified_relationships": standing_unverified_details,
            "standing_missing_operations": standing_missing,
            "standing_unverified_operations": standing_unverified,
            "restored_operations": 0,
            "retained_label_definitions": 0,
            "skipped_labels_in_use": 0,
            "total_operations": len(receipt.data["operations"]),
        })
        return 0
    basic_preflight(runner)
    repositories = receipt_repositories(receipt)
    issue_repositories = receipt_issue_repositories(receipt)
    blocked_repositories: dict[str, str] = {}
    for repo in sorted(repositories):
        try:
            repository_preflight(runner, repo)
            if repo in issue_repositories:
                issue_read_preflight(runner, repo)
        except WorkError as exc:
            blocked_repositories[repo] = str(exc)
    restored = 0
    missing_issue_operations = 0
    mutated_operations = 0
    unverified_relationship_operations = 0
    run_unverified_details: list[dict[str, Any]] = []
    already_restored = 0
    skipped_in_use = 0
    retained_label_definitions = 0
    # Simulation is dry-run only. Real replay deliberately re-reads GitHub state so retries after
    # partial failures do not trust stale in-process state.
    simulated_issue_labels: dict[tuple[str, str], bool] = {}
    simulated_pr_bodies: dict[str, str] = {}
    all_issue_label_reapplications = {
        (canonical_issue_reference(operation["issue"]), operation["name"])
        for operation in receipt.data["operations"]
        if operation["kind"] == "issue-label-removed"
    }
    for operation in reversed(receipt.data["operations"]):
        if operation["status"] == "restored":
            already_restored += 1
            continue
        kind = operation["kind"]
        touched_repositories = operation_repositories(operation)
        if touched_repositories & set(blocked_repositories):
            continue
        fallback_succeeded: bool | None = None
        probe_error: str | None = None
        mutated = False
        unverified = False
        operation_state: dict[str, Any] | None = None
        issue_reference = operation.get("issue")
        if isinstance(issue_reference, str):
            operation_state = restore_issue_state(runner, issue_reference)
            if operation_state is None:
                if not runner.dry_run:
                    receipt.mark_restored(operation, missing=True, mutated=False)
                restored += 1
                missing_issue_operations += 1
                continue
        if kind == "pr-body-changed":
            mutated = restore_pr_body(runner, operation, simulated_pr_bodies)
        elif kind == "assignee-added":
            if operation_state is None:
                raise WorkError("assignee restore lacks issue state")
            state = operation_state
            if operation["login"] in issue_assignees(state):
                runner.run(["issue", "edit", operation["issue"], "--remove-assignee", operation["login"]], mutate=True)
                mutated = True
        elif kind == "issue-label-added":
            if operation_state is None:
                raise WorkError("label restore lacks issue state")
            state = operation_state
            label_key = (canonical_issue_reference(operation["issue"]), operation["name"])
            label_present = simulated_issue_labels.get(
                label_key, operation["name"] in issue_labels(state)
            )
            if label_present:
                runner.run(["issue", "edit", operation["issue"], "--remove-label", operation["name"]], mutate=True)
                mutated = True
                if runner.dry_run:
                    simulated_issue_labels[label_key] = False
        elif kind == "issue-label-removed":
            if operation_state is None:
                raise WorkError("label reapplication lacks issue state")
            state = operation_state
            label_key = (canonical_issue_reference(operation["issue"]), operation["name"])
            label_present = simulated_issue_labels.get(
                label_key, operation["name"] in issue_labels(state)
            )
            if not label_present:
                result = runner.run(
                    ["issue", "edit", operation["issue"], "--add-label", operation["name"]],
                    mutate=True,
                    check=False,
                )
                if result.returncode == 0:
                    mutated = True
                    if runner.dry_run:
                        simulated_issue_labels[label_key] = True
                else:
                    detail = f"{result.stderr}\n{result.stdout}".lower()
                    if not any(
                        marker in detail
                        for marker in (
                            "label not found", "label does not exist", "unknown label"
                        )
                    ):
                        raise WorkError(
                            result.stderr.strip() or result.stdout.strip()
                            or "label reapplication failed"
                        )
        elif kind == "relationship-added":
            # Exact REST membership also establishes source existence; no GraphQL read is needed.
            source_repo, source_number = parse_issue_url(operation["source"])
            if operation["relation"] == "sub-issue":
                endpoint = f"repos/{source_repo}/issues/{source_number}/sub_issues"
                response_name = "sub-issue"
                flag = "--remove-sub-issue"
                relationship_markers = (
                    "sub-issue not found", "no sub-issue", "not a sub-issue"
                )
            else:
                endpoint = (
                    f"repos/{source_repo}/issues/{source_number}/dependencies/blocked_by"
                )
                response_name = "blocked-by"
                flag = "--remove-blocked-by"
                relationship_markers = (
                    "blocked-by not found", "no blocked-by", "not blocked"
                )
            try:
                related_issues = restore_relationship_state(
                    runner,
                    endpoint,
                    response_name,
                    operation["source"],
                )
            except RelationshipEndpointUnavailable as exc:
                # The mutation command can still use GraphQL on deployments without REST support.
                probe_error = str(exc)
                relationship_present = True
                unverified = True
            else:
                if related_issues is None:
                    if not runner.dry_run:
                        receipt.mark_restored(operation, missing=True, mutated=False)
                    restored += 1
                    missing_issue_operations += 1
                    continue
                target = canonical_issue_reference(operation["target"])
                relationship_present = target in related_issues
            if relationship_present:
                result = runner.run(
                    ["issue", "edit", operation["source"], flag, operation["target"]],
                    mutate=True,
                    check=False,
                )
                if result.returncode == 0:
                    fallback_succeeded = (
                        None if runner.dry_run
                        else True if unverified
                        else None
                    )
                    mutated = not unverified
                else:
                    detail = f"{result.stderr}\n{result.stdout}".lower()
                    tolerated = any(
                        marker in detail
                        for marker in (*relationship_markers, "no relationship", "not related")
                    )
                    if unverified:
                        fallback_succeeded = False
                        if not tolerated:
                            mutation_error = result.stderr.strip() or result.stdout.strip()
                            probe_error = (
                                f"{probe_error}; fallback mutation failed: {mutation_error}"
                            )
                    elif not tolerated:
                        mutation_error = result.stderr.strip() or result.stdout.strip()
                        raise WorkError(f"relationship restore failed: {mutation_error}")
        elif kind == "issue-created":
            if operation_state is None:
                raise WorkError("issue restore lacks issue state")
            state = operation_state
            if str(state.get("state")).upper() == "OPEN":
                runner.run(["issue", "close", operation["issue"], "--reason", "not planned"], mutate=True)
                mutated = True
        elif kind == "label-created":
            label_result = runner.run(
                [
                    "api",
                    f"repos/{operation['repo']}/labels/{quote(operation['name'], safe='')}",
                ],
                check=False,
            )
            label_exists = label_result.returncode == 0
            if not label_exists:
                detail = f"{label_result.stderr}\n{label_result.stdout}".lower()
                # Repository preflight already established access, so HTTP 404 identifies the
                # exact label resource as absent rather than an inaccessible repository.
                if "http 404" not in detail:
                    raise WorkError(
                        f"cannot verify label {operation['name']} in {operation['repo']}: "
                        f"{label_result.stderr.strip() or label_result.stdout.strip()}"
                    )
            if label_exists:
                issue_uses = runner.json([
                    "issue", "list", "--repo", operation["repo"], "--state", "all",
                    "--label", operation["name"], "--limit", "101", "--json", "url",
                ])
                if not isinstance(issue_uses, list):
                    raise WorkError(f"cannot verify label usage in {operation['repo']}")
                if len(issue_uses) >= 101:
                    raise WorkError(
                        f"cannot verify complete label usage in {operation['repo']}: "
                        "issue read reached the fail-closed limit"
                    )
                # Pull-request usage is existence-only, so one result is sufficient.
                pr_uses = runner.json([
                    "pr", "list", "--repo", operation["repo"], "--state", "all",
                    "--label", operation["name"], "--limit", "1", "--json", "url",
                ])
                if not isinstance(pr_uses, list):
                    raise WorkError(f"cannot verify label usage in {operation['repo']}")
                observed_issue_uses = {
                    canonical_issue_reference(use.get("url", ""))
                    for use in issue_uses
                    if isinstance(use, dict)
                }
                if runner.dry_run:
                    for (issue, name), present in simulated_issue_labels.items():
                        if (
                            name == operation["name"]
                            and parse_issue_url(issue)[0] == operation["repo"]
                        ):
                            if present:
                                observed_issue_uses.add(issue)
                            else:
                                observed_issue_uses.discard(issue)
                reapplication_targets = {
                    issue for issue, name in all_issue_label_reapplications
                    if name == operation["name"]
                    and parse_issue_url(issue)[0] == operation["repo"]
                }
                if observed_issue_uses or pr_uses:
                    if not pr_uses and observed_issue_uses <= reapplication_targets:
                        retained_label_definitions += 1
                    else:
                        skipped_in_use += 1
                        continue
                else:
                    runner.run([
                        "label", "delete", operation["name"], "--repo", operation["repo"],
                        "--yes",
                    ], mutate=True)
                    mutated = True
        if not runner.dry_run:
            receipt.mark_restored(
                operation,
                fallback_succeeded=fallback_succeeded,
                mutated=mutated,
                probe_error=probe_error,
                unverified=unverified,
            )
        restored += 1
        mutated_operations += int(mutated)
        unverified_relationship_operations += int(unverified)
        if unverified:
            details_operation = {
                **operation,
                "restore_fallback_succeeded": fallback_succeeded,
                "restore_probe_error": probe_error,
            }
            run_unverified_details.append(unverified_relationship_details(details_operation))
    json_print({
        "already_restored_operations": already_restored,
        "blocked_repositories": [
            {"error": error, "repo": repo}
            for repo, error in sorted(blocked_repositories.items())
        ],
        "config_requested": receipt.config_requested,
        "config_status": receipt.config_status,
        "config_unavailable": receipt.config_unavailable,
        "dry_run": runner.dry_run,
        "missing_issue_operations": missing_issue_operations,
        "mutated_operations": mutated_operations,
        "reason": (
            "blocked_repositories" if blocked_repositories
            else "labels_in_use" if skipped_in_use
            else "retained_labels" if retained_label_definitions
            else "unverified_relationships" if unverified_relationship_operations
            else "missing_issues" if missing_issue_operations
            else "restored"
        ),
        "restored_operations": restored,
        "retained_label_definitions": retained_label_definitions,
        "standing_missing_operations": standing_missing + missing_issue_operations,
        "standing_unverified_operations": (
            standing_unverified + unverified_relationship_operations
        ),
        "skipped_labels_in_use": skipped_in_use,
        "unverified_relationship_operations": unverified_relationship_operations,
        "unverified_relationships": standing_unverified_details + run_unverified_details,
        "total_operations": len(receipt.data["operations"]),
    })
    return 3 if skipped_in_use or blocked_repositories else 0


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
            preflighted=True,
        )
        try:
            child_payload = command_issue_create(
                child_args,
                runner,
                config,
                receipt,
                emit=False,
            )
        except PartialWorkError as child_error:
            # A child partial always represents GitHub state that needs reconciliation.
            aggregate = {
                "created_tasks": len(created),
                "failed_partial": child_error.payload,
                "failed_repo": repo,
                "issues": created,
                "partial": True,
                "umbrella": args.umbrella,
            }
            json_print(aggregate)
            raise PartialWorkError(str(child_error), aggregate) from child_error
        except WorkError as child_error:
            is_partial = bool(created) and not runner.dry_run
            aggregate = {
                "created_tasks": len(created),
                "failed_partial": None,
                "failed_repo": repo,
                "issues": created,
                "partial": is_partial,
                "umbrella": args.umbrella,
            }
            json_print(aggregate)
            if is_partial:
                raise PartialWorkError(str(child_error), aggregate) from child_error
            raise
        created.append(child_payload)
    if not runner.dry_run:
        receipt.ensure_saved()
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


def verify_hash_managed_block(
    text: str,
    required_lines: tuple[str, ...],
    label: str,
) -> None:
    begin = "# BEGIN github-work-standard"
    end = "# END github-work-standard"
    if text.count(begin) != 1 or text.count(end) != 1:
        raise WorkError(f"{label} requires one complete github-work-standard block")
    start = text.index(begin) + len(begin)
    finish = text.index(end, start)
    lines = {line.strip() for line in text[start:finish].splitlines() if line.strip()}
    missing = [line for line in required_lines if line not in lines]
    if missing:
        raise WorkError(f"{label} github-work-standard block is missing: {', '.join(missing)}")


def command_standard_check(args: argparse.Namespace) -> int:
    helper_text = Path(__file__).read_text(encoding="utf-8")
    helper = provenance_from_text(helper_text)
    verify_content(helper_text, helper, managed_region=False)
    identity = {key: helper[key] for key in ("version", "source", "target")}
    checked: dict[str, str] = {"helper": str(Path(__file__))}
    paths = [
        ("agents", args.agents_path, True),
        ("skill", args.skill_path, True),
        ("pull-request-template", args.pr_template_path, True),
        ("workflow", args.workflow_path, False),
        *((f"issue-form-{index + 1}", path, True) for index, path in enumerate(
            args.issue_form_path or [
                ".github/ISSUE_TEMPLATE/bug.yml",
                ".github/ISSUE_TEMPLATE/feature.yml",
                ".github/ISSUE_TEMPLATE/task.yml",
            ]
        )),
    ]
    for label, raw_path, managed_region in paths:
        path = Path(raw_path)
        if not path.is_file():
            raise WorkError(f"standard-check path is missing: {path}")
        text = path.read_text(encoding="utf-8")
        marker = provenance_from_text(text)
        verify_content(text, marker, managed_region=managed_region)
        if {key: marker[key] for key in identity} != identity:
            raise WorkError(f"{label} provenance does not match helper provenance")
        checked[label] = str(path)
    ignore_contracts = (
        (
            "gitignore",
            args.gitignore_path,
            (
                ".github-work/",
                "*github-work-targets*",
                "*github-work-ownership*",
                "*.github-work-receipt.json*",
                "*github-work-recovery*.json*",
            ),
        ),
        (
            "prettierignore",
            args.prettierignore_path,
            (
                ".github/ISSUE_TEMPLATE/bug.yml",
                ".github/ISSUE_TEMPLATE/feature.yml",
                ".github/ISSUE_TEMPLATE/task.yml",
                ".github/pull_request_template.md",
                ".github/PULL_REQUEST_TEMPLATE.md",
                ".github/workflows/github-work-standard.yml",
                "scripts/github_work.py",
            ),
        ),
    )
    for label, raw_path, required_lines in ignore_contracts:
        path = Path(raw_path)
        if not path.is_file():
            raise WorkError(f"standard-check path is missing: {path}")
        verify_hash_managed_block(
            path.read_text(encoding="utf-8"),
            required_lines,
            label,
        )
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
    parser.add_argument(
        "--ownership-config",
        help="private ownership configuration used only by assign --from-ownership-map",
    )
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
    issue.add_argument("--assignee", help="non-empty login to assign")
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
    group.add_argument("--assignee", help="non-empty login to assign")
    group.add_argument("--from-ownership-map", action="store_true")
    assign.add_argument(
        "--area",
        help="non-empty ownership area used only with --from-ownership-map",
    )
    assign.add_argument("--receipt", required=True)
    assign.add_argument("--json", action="store_true")

    work_graph = subparsers.add_parser("work-graph")
    work_graph_sub = work_graph.add_subparsers(dest="work_graph_command", required=True)
    work_graph_create = work_graph_sub.add_parser("create")
    work_graph_create.add_argument("--umbrella", required=True)
    work_graph_create.add_argument("--repos", default="all")
    work_graph_create.add_argument("--assignee", help="non-empty login to assign")
    work_graph_create.add_argument("--receipt", required=True)

    standard_check = subparsers.add_parser("standard-check")
    standard_check.add_argument("--agents-path", default="AGENTS.md")
    standard_check.add_argument("--skill-path", default=".claude/skills/github-work/SKILL.md")
    standard_check.add_argument("--pr-template-path", default=".github/pull_request_template.md")
    standard_check.add_argument(
        "--workflow-path",
        default=".github/workflows/github-work-standard.yml",
    )
    standard_check.add_argument("--gitignore-path", default=".gitignore")
    standard_check.add_argument("--prettierignore-path", default=".prettierignore")
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
        validate_cli_args(args)
        if args.command == "standard-check":
            return command_standard_check(args)
        source_sha = active_source_sha()
        if args.command == "restore":
            config_requested = args.config is not None
            config_sha = None
            config_status = "absent"
            if config_requested and not args.config:
                config_status = "empty"
            elif config_requested:
                try:
                    config_sha = file_digest(args.config)
                except Exception:
                    config_status = "unreadable"
                else:
                    try:
                        load_targets(args.config)
                    except Exception:
                        config_status = "invalid"
                    else:
                        config_status = "ok"
            config_unavailable = config_status in {"empty", "invalid", "unreadable"}
            receipt = Receipt(
                args.receipt,
                source_sha=source_sha,
                config_digest=config_sha,
                config_requested=config_requested,
                config_unavailable=config_unavailable,
                config_status=config_status,
            )
            return command_restore(args, active_runner, receipt)
        config = load_targets(args.config)
        config_sha = file_digest(args.config)
        ownership = load_ownership(args.ownership_config) if args.ownership_config else None
        if args.command == "preflight":
            return command_preflight(args, active_runner, config)
        if args.command == "finality":
            return command_finality(args, active_runner, config)
        receipt = Receipt(
            getattr(args, "receipt", None),
            source_sha=source_sha,
            config_digest=config_sha,
            config_requested=True,
            config_status="ok",
        )
        if args.command == "labels":
            return command_labels_ensure(args, active_runner, config, receipt)
        if args.command == "issue-create":
            command_issue_create(args, active_runner, config, receipt)
            return 0
        if args.command == "pr-link":
            return command_pr_link(args, active_runner, config, receipt)
        if args.command == "assign":
            if args.from_ownership_map:
                if args.ownership_config is None:
                    raise WorkError("--ownership-config is required with --from-ownership-map")
                if ownership is None:
                    raise WorkError("ownership config was not loaded")
            return command_assign(args, active_runner, config, ownership, receipt)
        if args.command == "work-graph":
            return command_work_graph_create(args, active_runner, config, receipt)
        raise WorkError(f"unsupported command: {args.command}")
    except WorkError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
