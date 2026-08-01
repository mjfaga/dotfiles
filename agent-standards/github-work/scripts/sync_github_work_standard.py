#!/usr/bin/env python3
"""Render the public GitHub-work standard into explicitly configured targets."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

BEGIN = "<!-- BEGIN github-work-standard -->"
END = "<!-- END github-work-standard -->"
VALID_ADAPTERS = {"generated-modern", "generated-legacy", "plain"}
VALID_CLASSIFICATIONS = {"native-type", "managed-label"}


class RenderError(RuntimeError):
    pass


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RenderError(f"cannot load JSON-compatible YAML: {path}") from exc
    if not isinstance(value, dict):
        raise RenderError(f"expected object: {path}")
    return value


def validate_targets(config: dict[str, Any]) -> list[dict[str, Any]]:
    targets = config.get("targets")
    if not isinstance(targets, list):
        raise RenderError("target config requires a targets array")
    repos: set[str] = set()
    for target in targets:
        if not isinstance(target, dict):
            raise RenderError("target entries must be objects")
        for key in ("repo", "checkout", "adapter", "classification", "agents_source_path", "skill_source_path"):
            if not isinstance(target.get(key), str) or not target[key]:
                raise RenderError(f"target requires {key}")
        if target["repo"] in repos:
            raise RenderError(f"duplicate target: {target['repo']}")
        repos.add(target["repo"])
        if target["adapter"] not in VALID_ADAPTERS:
            raise RenderError(f"unknown adapter for {target['repo']}: {target['adapter']}")
        if target["classification"] not in VALID_CLASSIFICATIONS:
            raise RenderError(f"unknown classification for {target['repo']}")
        if not isinstance(target.get("checks", []), list):
            raise RenderError(f"checks must be an array for {target['repo']}")
        path_fields = (
            "agents_source_path", "skill_source_path", "issue_forms_path",
            "pr_template_path", "helper_path", "standard_workflow_path",
            "gitignore_path", "prettierignore_path",
        )
        for field in path_fields:
            value = target.get(field)
            if value is None:
                continue
            path = Path(value)
            if path.is_absolute() or ".." in path.parts:
                raise RenderError(f"{field} must stay relative to checkout for {target['repo']}")
        agents = target["agents_source_path"]
        skill = target["skill_source_path"]
        adapter = target["adapter"]
        if adapter == "plain" and (agents != "AGENTS.md" or skill.endswith(".src.md")):
            raise RenderError(f"plain adapter paths are invalid for {target['repo']}")
        if adapter != "plain" and (not agents.endswith(".src.md") or not skill.endswith(".src.md")):
            raise RenderError(f"generated adapter paths must be source files for {target['repo']}")
        if adapter == "generated-modern" and ".claude/skills/" not in skill:
            raise RenderError(f"modern skill path is invalid for {target['repo']}")
        if adapter == "generated-legacy" and "docs/skills/" not in skill:
            raise RenderError(f"legacy skill path is invalid for {target['repo']}")
        remove_labels = target.get("remove_labels", [])
        if not isinstance(remove_labels, list) or not all(isinstance(label, str) for label in remove_labels):
            raise RenderError(f"remove_labels must be a string array for {target['repo']}")
    return targets


def digest_target(target: dict[str, Any]) -> str:
    encoded = json.dumps(target, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def marker_payload(content: str) -> str:
    start = content.find(BEGIN)
    end = content.find(END)
    if start < 0 or end < 0 or end < start:
        raise RenderError("canonical fragment lacks bounded markers")
    return content[start : end + len(END)]


def frontmatter_payload(content: str) -> str:
    if not content.startswith("---\n"):
        raise RenderError("canonical skill must start with YAML frontmatter")
    end = content.find("\n---\n", 4)
    if end < 0:
        raise RenderError("canonical skill frontmatter is unterminated")
    return content[: end + len("\n---\n")].rstrip("\n")


def merge_marker(original: str, block: str) -> str:
    start = original.find(BEGIN)
    end = original.find(END)
    if (start < 0) != (end < 0):
        raise RenderError("found only one github-work-standard marker")
    if start >= 0:
        if original.find(BEGIN, start + len(BEGIN)) >= 0 or original.find(END, end + len(END)) >= 0:
            raise RenderError("multiple github-work-standard marker blocks")
        return original[:start] + block + original[end + len(END) :]
    separator = "" if not original else ("\n" if original.endswith("\n") else "\n\n")
    return original + separator + block + "\n"


def merge_hash_marker(original: str, content: str) -> str:
    begin = "# BEGIN github-work-standard"
    end_marker = "# END github-work-standard"
    start = original.find(begin)
    end = original.find(end_marker)
    if (start < 0) != (end < 0):
        raise RenderError("found only one github-work-standard hash marker")
    block = f"{begin}\n{content.rstrip()}\n{end_marker}"
    if start >= 0:
        if original.find(begin, start + len(begin)) >= 0 or original.find(
            end_marker, end + len(end_marker)
        ) >= 0:
            raise RenderError("multiple github-work-standard hash marker blocks")
        return original[:start] + block + original[end + len(end_marker) :]
    separator = "" if not original else ("\n" if original.endswith("\n") else "\n\n")
    return original + separator + block + "\n"


def provenance(
    version: str,
    source_sha: str,
    target_digest: str,
    content_digest: str,
    prefix: str = "<!--",
) -> str:
    payload = (
        f"github-work-standard: version={version} source={source_sha} "
        f"target={target_digest} content={content_digest}"
    )
    if prefix == "#":
        return f"# {payload}\n"
    return f"<!-- {payload} -->\n"


def render_marked_source(source: str, version: str, source_sha: str, target_digest: str) -> str:
    block = marker_payload(source)
    content_digest = hashlib.sha256(block.encode("utf-8")).hexdigest()
    marker = provenance(version, source_sha, target_digest, content_digest).rstrip("\n")
    return block.replace(BEGIN, f"{BEGIN}\n{marker}", 1)


def render_skill_file(original: str, source: str, version: str, source_sha: str, target_digest: str) -> str:
    merged = merge_marker(original, render_marked_source(source, version, source_sha, target_digest))
    frontmatter = frontmatter_payload(source)
    if merged.startswith("---\n"):
        existing_end = merged.find("\n---\n", 4)
        if existing_end < 0:
            raise RenderError("existing skill frontmatter is unterminated")
        merged = merged[existing_end + len("\n---\n") :].lstrip("\n")
    return frontmatter + "\n\n" + merged


def form_header(
    kind: str,
    classification: str,
    labels: list[str] | None = None,
    provenance_marker: str | None = None,
) -> str:
    managed_labels = list(dict.fromkeys(labels or []))
    lines = [f"# {BEGIN}"]
    provenance_index = len(lines)
    if classification == "native-type":
        lines.append(f"type: {kind.title()}")
    else:
        managed = f"type:{kind.lower()}"
        if managed not in managed_labels:
            managed_labels.append(managed)
    if managed_labels:
        lines.append("labels:")
        lines.extend(f"  - {json.dumps(label)}" for label in managed_labels)
    lines.append(f"# {END}")
    if provenance_marker:
        unmanaged_block = "\n".join(lines)
        content_digest = hashlib.sha256(unmanaged_block.encode("utf-8")).hexdigest()
        lines.insert(provenance_index, f"# {provenance_marker} content={content_digest}")
    return "\n".join(lines)


def parse_inline_labels(value: str) -> list[str]:
    try:
        parsed = ast.literal_eval(value)
    except (SyntaxError, ValueError) as exc:
        raise RenderError("cannot parse existing inline labels") from exc
    if not isinstance(parsed, list) or not all(isinstance(label, str) for label in parsed):
        raise RenderError("existing labels must be a string array")
    return parsed


def adopt_existing_classification(existing: str) -> tuple[str, list[str]]:
    lines = existing.splitlines(keepends=True)
    kept: list[str] = []
    labels: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if re.match(r"^type\s*:", line):
            index += 1
            continue
        label_match = re.match(r"^labels\s*:\s*(.*?)\s*(?:\n)?$", line)
        if not label_match:
            kept.append(line)
            index += 1
            continue
        inline = label_match.group(1)
        index += 1
        if inline:
            labels.extend(parse_inline_labels(inline))
            continue
        while index < len(lines):
            item = re.match(r"^\s+-\s+['\"]?([^'\"\n]+)['\"]?\s*$", lines[index])
            if not item:
                break
            labels.append(item.group(1).strip())
            index += 1
    return "".join(kept), labels


def merge_form(
    existing: str,
    kind: str,
    classification: str,
    new_form: str,
    remove_labels: list[str] | None = None,
    provenance_marker: str | None = None,
) -> str:
    begin = f"# {BEGIN}"
    end = f"# {END}"
    remove = set(remove_labels or [])
    if not existing:
        data = json.loads(new_form)
        block = form_header(kind, classification, provenance_marker=provenance_marker)
        lines = [
            block,
            f"name: {json.dumps(data['name'])}",
            f"description: {json.dumps(data['description'])}",
            f"title: {json.dumps(data.get('title') or f'[{kind.title()}] ')}",
            "body:",
        ]
        for item in data["body"]:
            lines.extend([
                f"  - type: {item['type']}",
                f"    id: {item['id']}",
                "    attributes:",
                f"      label: {json.dumps(item['attributes']['label'])}",
            ])
            if item.get("validations", {}).get("required"):
                lines.extend(["    validations:", "      required: true"])
        return "\n".join(lines) + "\n"
    start = existing.find(begin)
    finish = existing.find(end)
    if (start < 0) != (finish < 0):
        raise RenderError("found only one issue-form marker")
    if start >= 0:
        old_block = existing[start : finish + len(end)]
        _, adopted_labels = adopt_existing_classification(old_block)
        labels = [label for label in adopted_labels if label not in remove and not label.startswith("type:")]
        block = form_header(kind, classification, labels, provenance_marker)
        return existing[:start] + block + existing[finish + len(end) :]
    remainder, adopted_labels = adopt_existing_classification(existing)
    labels = [label for label in adopted_labels if label not in remove and not label.startswith("type:")]
    return form_header(kind, classification, labels, provenance_marker) + "\n" + remainder


def marked_helper(source: str, version: str, source_sha: str, target_digest: str) -> str:
    lines = source.splitlines(keepends=True)
    content_digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    marker = provenance(version, source_sha, target_digest, content_digest, prefix="#")
    if lines and lines[0].startswith("#!"):
        return lines[0] + marker + "".join(lines[1:])
    return marker + source


def marked_yaml(source: str, version: str, source_sha: str, target_digest: str) -> str:
    content_digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    return provenance(version, source_sha, target_digest, content_digest, prefix="#") + source


def safe_output_path(checkout: Path, relative: str) -> Path:
    candidate = (checkout / relative).resolve()
    try:
        candidate.relative_to(checkout)
    except ValueError as exc:
        raise RenderError(f"output path escapes checkout: {relative}") from exc
    return candidate


def expected_files(
    source_root: Path,
    target: dict[str, Any],
    version: str,
    source_sha: str,
    checkout_override: str | None = None,
) -> dict[Path, str]:
    checkout = Path(checkout_override or target["checkout"]).resolve()
    if not checkout.is_dir():
        raise RenderError(f"checkout does not exist: {target['checkout']}")
    target_digest = digest_target(target)
    agents_path = safe_output_path(checkout, target["agents_source_path"])
    skill_path = safe_output_path(checkout, target["skill_source_path"])
    agents_original = agents_path.read_text(encoding="utf-8") if agents_path.exists() else ""
    skill_original = skill_path.read_text(encoding="utf-8") if skill_path.exists() else ""
    agents_source = (source_root / "AGENTS.fragment.md").read_text(encoding="utf-8")
    skill_source = (source_root / "SKILL.body.md").read_text(encoding="utf-8")
    agents_block = render_marked_source(agents_source, version, source_sha, target_digest)
    files = {
        agents_path: merge_marker(agents_original, agents_block),
        skill_path: render_skill_file(skill_original, skill_source, version, source_sha, target_digest),
    }
    form_dir_relative = target.get("issue_forms_path", ".github/ISSUE_TEMPLATE")
    filenames = target.get("issue_form_files", {"bug": "bug.yml", "feature": "feature.yml", "task": "task.yml"})
    if not isinstance(filenames, dict) or set(filenames) != {"bug", "feature", "task"}:
        raise RenderError(f"issue_form_files must define bug, feature, and task for {target['repo']}")
    for kind in ("bug", "feature", "task"):
        path = safe_output_path(checkout, str(Path(form_dir_relative) / filenames[kind]))
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        source = (source_root / "issue-forms" / f"{kind}.yml").read_text(encoding="utf-8")
        form_marker = f"github-work-standard: version={version} source={source_sha} target={target_digest}"
        files[path] = merge_form(
            existing,
            kind,
            target["classification"],
            source,
            target.get("remove_labels", []),
            form_marker,
        )
    pr_path = safe_output_path(checkout, target.get("pr_template_path", ".github/pull_request_template.md"))
    existing_pr = pr_path.read_text(encoding="utf-8") if pr_path.exists() else ""
    pr_block = render_marked_source(
        (source_root / "pull_request_template.md").read_text(encoding="utf-8"),
        version,
        source_sha,
        target_digest,
    )
    files[pr_path] = merge_marker(existing_pr, pr_block)
    helper_path = safe_output_path(checkout, target.get("helper_path", "scripts/github_work.py"))
    files[helper_path] = marked_helper(
        (source_root / "github_work.py").read_text(encoding="utf-8"),
        version,
        source_sha,
        target_digest,
    )
    workflow_path = safe_output_path(
        checkout,
        target.get("standard_workflow_path", ".github/workflows/github-work-standard.yml"),
    )
    files[workflow_path] = marked_yaml(
        (source_root / "github-work-standard.yml").read_text(encoding="utf-8"),
        version,
        source_sha,
        target_digest,
    )
    for path_key, default_path, fragment_name in (
        ("gitignore_path", ".gitignore", "gitignore.fragment"),
        ("prettierignore_path", ".prettierignore", "prettierignore.fragment"),
    ):
        ignore_path = safe_output_path(checkout, target.get(path_key, default_path))
        ignore_original = (
            ignore_path.read_text(encoding="utf-8") if ignore_path.exists() else ""
        )
        ignore_content = (source_root / fragment_name).read_text(encoding="utf-8")
        files[ignore_path] = merge_hash_marker(ignore_original, ignore_content)
    return files


def select_targets(targets: list[dict[str, Any]], repos: str) -> list[dict[str, Any]]:
    if repos == "all":
        return targets
    wanted = {item.strip() for item in repos.split(",") if item.strip()}
    selected = [target for target in targets if target["repo"] in wanted]
    missing = wanted - {target["repo"] for target in selected}
    if missing:
        raise RenderError(f"unknown targets: {sorted(missing)}")
    return selected


def parse_checkout_overrides(values: list[str], targets: list[dict[str, Any]]) -> dict[str, str]:
    known = {target["repo"] for target in targets}
    overrides: dict[str, str] = {}
    for value in values:
        repo, separator, checkout = value.partition("=")
        if not separator or not repo or not checkout:
            raise RenderError("--checkout-override must use OWNER/REPO=/absolute/path")
        if repo not in known:
            raise RenderError(f"checkout override targets unknown repository: {repo}")
        if repo in overrides:
            raise RenderError(f"duplicate checkout override: {repo}")
        if not Path(checkout).is_absolute():
            raise RenderError(f"checkout override must be absolute: {repo}")
        overrides[repo] = checkout
    return overrides


def verify_source(source_root: Path, source_sha: str, source_tag: str) -> None:
    if not re_full_sha(source_sha):
        raise RenderError("--source-sha must be a 40-character lowercase commit SHA")
    head = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"],
        check=False,
        text=True,
        capture_output=True,
    )
    tag = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", f"refs/tags/{source_tag}^{{commit}}"],
        check=False,
        text=True,
        capture_output=True,
    )
    if head.returncode != 0 or head.stdout.strip() != source_sha:
        raise RenderError("source checkout HEAD does not match --source-sha")
    if tag.returncode != 0 or tag.stdout.strip() != source_sha:
        raise RenderError("immutable source tag does not resolve to --source-sha")
    top = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "--show-toplevel"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    relative = source_root.relative_to(Path(top))
    dirty = subprocess.run(
        ["git", "-C", top, "status", "--porcelain", "--", str(relative)],
        check=True,
        text=True,
        capture_output=True,
    ).stdout
    if dirty:
        raise RenderError("public standard source tree has uncommitted changes")


def sync(args: argparse.Namespace) -> int:
    source_root = Path(args.source_root).resolve()
    verify_source(source_root, args.source_sha, args.source_tag)
    metadata = load_object(source_root / "standard.yml")
    version = str(metadata["version"])
    all_targets = validate_targets(load_object(Path(args.config)))
    targets = select_targets(all_targets, args.repos)
    overrides = parse_checkout_overrides(getattr(args, "checkout_override", []), all_targets)
    drift: list[str] = []
    changed: list[str] = []
    for target in targets:
        for path, content in expected_files(
            source_root,
            target,
            version,
            args.source_sha,
            overrides.get(target["repo"]),
        ).items():
            current = path.read_text(encoding="utf-8") if path.exists() else None
            if current == content:
                continue
            drift.append(str(path))
            if args.check or args.dry_run:
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            if path.name == "github_work.py":
                path.chmod(0o755)
            changed.append(str(path))
    result = {
        "target_count": len(targets),
        "drift_count": len(drift),
        "changed_count": len(changed),
        "drift": drift,
        "changed": changed,
        "check": args.check,
        "dry_run": args.dry_run,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if args.check and drift else 0


def re_full_sha(value: str) -> bool:
    return len(value) == 40 and all(character in "0123456789abcdef" for character in value)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--config", required=True)
    result.add_argument("--source-root", default=str(Path(__file__).resolve().parents[1]))
    result.add_argument("--source-sha", required=True)
    result.add_argument("--source-tag", required=True)
    result.add_argument("--repos", default="all")
    result.add_argument(
        "--checkout-override",
        action="append",
        default=[],
        metavar="OWNER/REPO=/ABSOLUTE/PATH",
        help="render a configured target into a temporary feature worktree without changing its digest",
    )
    mode = result.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    try:
        return sync(parser().parse_args(argv))
    except RenderError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
