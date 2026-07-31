#!/usr/bin/env python3
"""Fail if runtime-private target/ownership values appear in public sources."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence

TEXT_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".json", ".txt"}
GENERIC_PATTERNS = {
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github-token": re.compile(r"\b(?:gh[opusr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    "aws-key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "machine-path": re.compile(r"/(?:Users|home)/[^/\s]+/"),
}
COMMON_PATH_PARTS = {"Users", "home", "projects", "repos", "runtime", "private", "tmp", "var", "workspace", "workspaces"}


class PublicContentError(RuntimeError):
    pass


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise PublicContentError(f"cannot read JSON-compatible YAML: {path}") from exc
    if not isinstance(value, dict):
        raise PublicContentError(f"expected object: {path}")
    return value


def add_repo_tokens(values: set[str], repo: Any) -> None:
    if not isinstance(repo, str) or "/" not in repo:
        return
    owner, name = repo.split("/", 1)
    values.update(value for value in (repo, owner, name) if len(value) >= 5)


def private_values(targets: dict[str, Any], ownership: dict[str, Any]) -> set[str]:
    values: set[str] = set()
    repositories = [*targets.get("targets", []), *targets.get("auxiliary_repositories", [])]
    for target in repositories:
        if not isinstance(target, dict):
            continue
        add_repo_tokens(values, target.get("repo"))
        checkout = target.get("checkout")
        if isinstance(checkout, str) and len(checkout) >= 5:
            values.add(checkout)
            values.update(
                part for part in Path(checkout).parts
                if len(part) >= 5 and part not in COMMON_PATH_PARTS
            )
        for key in ("ownership_key", "private_key"):
            value = target.get(key)
            if isinstance(value, str) and len(value) >= 5:
                values.add(value)
    for mapping in ownership.get("mappings", []):
        if not isinstance(mapping, dict):
            continue
        add_repo_tokens(values, mapping.get("repo"))
        area = mapping.get("area")
        if isinstance(area, str) and len(area) >= 5 and area != "*":
            values.add(area)
        for login in mapping.get("logins", []):
            if isinstance(login, str) and len(login) >= 5:
                values.add(login)
    return values


def public_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        if any(part in {"__pycache__", ".git"} for part in path.parts):
            continue
        yield path


def contains_token(text: str, value: str) -> bool:
    return bool(re.search(rf"(?<![A-Za-z0-9_-]){re.escape(value)}(?![A-Za-z0-9_-])", text))


def is_receipt_artifact(path: Path, text: str) -> bool:
    if path.suffix not in {".json", ".yml", ".yaml"}:
        return False
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return False
    return isinstance(value, dict) and "receipt_id" in value and isinstance(value.get("operations"), list)


def scan(root: Path, values: set[str]) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    for path in public_files(root):
        text = path.read_text(errors="replace")
        relative = str(path.relative_to(root))
        for value in sorted(values):
            if contains_token(text, value):
                violations.append({"file": relative, "kind": "private-value", "value": value})
        if is_receipt_artifact(path, text):
            violations.append({"file": relative, "kind": "rollout-receipt", "value": "<redacted>"})
        for name, pattern in GENERIC_PATTERNS.items():
            if pattern.search(text):
                violations.append({"file": relative, "kind": name, "value": "<redacted>"})
    return violations


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--targets", required=True)
    result.add_argument("--ownership", required=True)
    result.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        values = private_values(load(Path(args.targets)), load(Path(args.ownership)))
        violations = scan(Path(args.root).resolve(), values)
    except PublicContentError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"public_content_violations": len(violations), "violations": violations}, indent=2, sort_keys=True))
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
