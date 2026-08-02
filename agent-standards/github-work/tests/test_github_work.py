from __future__ import annotations

import contextlib
import importlib.util
import io
import hashlib
import json
import stat
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("github_work", ROOT / "github_work.py")
assert SPEC and SPEC.loader
work = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = work
SPEC.loader.exec_module(work)

SOURCE = "a" * 40
DIGEST = "b" * 64
ALL_LABELS = [{"name": value[0]} for value in work.MANAGED_LABELS.values()]
PAGED_ALL_LABELS = [ALL_LABELS]


class FakeRunner:
    def __init__(self, responses=None, dry_run=False):
        self.responses = list(responses or [])
        self.calls = []
        self.dry_run = dry_run

    def run(self, args, mutate=False, check=True):
        self.calls.append((list(args), mutate, check))
        if mutate and self.dry_run:
            return work.CommandResult()
        value = self.responses.pop(0) if self.responses else work.CommandResult()
        if isinstance(value, (dict, list)):
            value = work.CommandResult(stdout=json.dumps(value))
        if check and value.returncode:
            raise work.WorkError(value.stderr or "fake failure")
        return value

    def json(self, args, check=True):
        result = self.run(args, check=check)
        if result.returncode:
            return None
        return json.loads(result.stdout or "null")


def config(classification="managed-label", repos=None):
    names = repos or ["sample-space/sample-app"]
    return {"targets": [{"repo": name, "adapter": "plain", "classification": classification} for name in names]}


def receipt(path=None):
    return work.Receipt(
        path,
        source_sha=SOURCE,
        config_digest=DIGEST,
        transient=path is None,
    )


def managed_preflight_responses(*, labels=None):
    return [
        work.CommandResult(stdout="gh version 2.96.0\n"),
        work.CommandResult(),
        work.CommandResult(),
        [labels] if labels is not None else PAGED_ALL_LABELS,
    ]


def restore_preflight_responses(*, issue_read=True):
    responses = [
        work.CommandResult(stdout="gh version 2.96.0\n"),
        work.CommandResult(),
        work.CommandResult(),
    ]
    if issue_read:
        responses.append(work.CommandResult(stdout="[]"))
    return responses


class HelperTests(unittest.TestCase):
    def test_parser_registers_required_commands(self):
        help_text = work.build_parser().format_help()
        for command in ("preflight", "labels", "issue-create", "work-graph", "pr-link", "finality", "assign", "restore", "standard-check"):
            self.assertIn(command, help_text)

    def test_global_dry_run_order_is_explicit(self):
        parsed = work.build_parser().parse_args(["--dry-run", "preflight"])
        self.assertTrue(parsed.dry_run)
        with self.assertRaises(SystemExit):
            work.build_parser().parse_args(["preflight", "--dry-run"])

    def test_missing_gh_binary_is_an_operational_error(self):
        with mock.patch.object(work.subprocess, "run", side_effect=FileNotFoundError("gh")):
            with self.assertRaisesRegex(work.WorkError, "cannot execute GitHub CLI"):
                work.GhRunner().run(["version"])

    def test_preflight_propagates_operational_failures(self):
        runner = FakeRunner([
            work.CommandResult(stdout="gh version 2.96.0\n"),
            work.CommandResult(),
            work.CommandResult(returncode=1, stderr="denied"),
        ])
        with self.assertRaisesRegex(work.WorkError, "repository unavailable"):
            work.command_preflight(Namespace(repos="sample-space/sample-app"), runner, config())

    def test_parse_issue_url(self):
        self.assertEqual(work.parse_issue_url("https://github.com/sample-space/sample-app/issues/42"), ("sample-space/sample-app", 42))
        self.assertEqual(work.parse_issue_url("sample-space/sample-app#42"), ("sample-space/sample-app", 42))

    def test_issue_state_rejects_non_object_json(self):
        with self.assertRaisesRegex(work.WorkError, "cannot verify issue state"):
            work.issue_state(
                FakeRunner([work.CommandResult(stdout="null")]),
                "sample-space/sample-app#1",
            )

    def test_parse_issue_url_rejects_invalid(self):
        for value in (
            "#42",
            "https://notgithub.com/sample-space/sample-app/issues/42",
            "sample space/sample-app#42",
            "sample-space/sample/app#42",
            "sample-space/sample-app?query#42",
        ):
            with self.subTest(value=value), self.assertRaises(work.WorkError):
                work.parse_issue_url(value)

    def test_repository_labels_flattens_all_paginated_api_pages(self):
        runner = FakeRunner([[
            [{"name": "first"}],
            [{"name": "second"}],
        ]])
        self.assertEqual(
            work.repository_labels(runner, "sample-space/sample-app"),
            [{"name": "first"}, {"name": "second"}],
        )
        self.assertEqual(
            runner.calls[0][0],
            [
                "api",
                "repos/sample-space/sample-app/labels?per_page=100",
                "--paginate",
                "--slurp",
            ],
        )

    def test_repository_labels_rejects_malformed_paginated_response(self):
        with self.assertRaisesRegex(work.WorkError, "malformed paginated response"):
            work.repository_labels(FakeRunner([[{"name": "not-a-page"}]]), "sample-space/sample-app")

    def test_refs_demotes_all_closing_variants(self):
        body = (
            "Closes #3\n"
            "- FIXED sample-space/sample-app#3 after validation\n"
            "resolves sample-space/sample-app#3\n"
            "Closed https://github.com/sample-space/sample-app/issues/3\n"
        )
        rendered = work.linked_body(body, "sample-space/sample-app#3", "refs", "sample-space/sample-app")
        self.assertNotRegex(rendered.lower(), r"(?:closes|closed|fixed|resolves)\s+(?:#3|sample-space/sample-app#3|https://github.com/sample-space/sample-app/issues/3)")
        self.assertEqual(rendered.lower().count("refs"), 3)
        self.assertIn(
            "- FIXED <!-- github-work: non-closing --> sample-space/sample-app#3 after validation",
            rendered,
        )

    def test_refs_preserves_rendered_prose_while_neutralizing_closing_keyword(self):
        body = "The old script fixes #3 incorrectly, so this PR rewrites it.\n"
        rendered = work.linked_body(body, "sample-space/sample-app#3", "refs", "sample-space/sample-app")
        self.assertIn(
            "The old script fixes <!-- github-work: non-closing --> #3 incorrectly",
            rendered,
        )
        self.assertIn("Refs sample-space/sample-app#3", rendered)
        self.assertNotIn("The old script Refs #3", rendered)

    def test_refs_does_not_demote_short_reference_from_other_repo(self):
        body = "Closes #3\n"
        rendered = work.linked_body(body, "sample-space/sample-app#3", "refs", "other-space/other-app")
        self.assertIn("Closes #3", rendered)
        self.assertIn("Refs sample-space/sample-app#3", rendered)

    def test_closes_promotes_only_one_reference(self):
        body = "Refs #3\n- refs sample-space/sample-app#3\n"
        rendered = work.linked_body(body, "sample-space/sample-app#3", "closes", "sample-space/sample-app")
        self.assertEqual(rendered.count("Closes"), 1)
        self.assertEqual(rendered.lower().count("refs"), 1)

    def test_closes_promotes_work_item_reference_not_earlier_summary_reference(self):
        body = "## Summary\n\nFixes #3 by adding X\n\n## Work item\n\nRefs #3\n"
        rendered = work.linked_body(
            body,
            "sample-space/sample-app#3",
            "closes",
            "sample-space/sample-app",
        )
        self.assertIn(
            "## Summary\n\nFixes <!-- github-work: non-closing --> #3 by adding X",
            rendered,
        )
        self.assertIn("## Work item\n\nCloses sample-space/sample-app#3", rendered)

    def test_closes_appends_to_work_item_when_placeholder_was_deleted(self):
        body = "## Summary\n\nRefs #3 in summary\n\n## Work item\n\nNo link yet.\n"
        rendered = work.linked_body(
            body,
            "sample-space/sample-app#3",
            "closes",
            "sample-space/sample-app",
        )
        self.assertIn("## Summary\n\nRefs #3 in summary", rendered)
        self.assertIn(
            "## Work item\n\nNo link yet.\n\nCloses sample-space/sample-app#3",
            rendered,
        )

    def test_pr_closing_link_requires_finality(self):
        responses = managed_preflight_responses() + [
            {
                "blockedBy": {"nodes": [{"state": "OPEN"}], "totalCount": 1},
                "subIssuesSummary": {"total": 0, "completed": 0},
            },
        ]
        args = Namespace(
            pr="https://github.com/sample-space/sample-app/pull/2",
            issue="sample-space/sample-app#4",
            mode="closes",
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = work.command_pr_link(args, FakeRunner(responses), config(), receipt())
        self.assertEqual(result, 1)
        self.assertFalse(json.loads(output.getvalue())["finality"]["eligible"])

    def test_pr_link_reports_partial_state_when_receipt_write_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            current = receipt(str(Path(directory) / "receipt.json"))
            responses = managed_preflight_responses() + [
                {"body": "Original body\n", "url": "https://github.com/sample-space/sample-app/pull/2"},
                work.CommandResult(),
            ]
            args = Namespace(
                pr="https://github.com/sample-space/sample-app/pull/2",
                issue="sample-space/sample-app#4",
                mode="refs",
            )
            output = io.StringIO()
            with mock.patch.object(current, "save", side_effect=work.WorkError("cannot save receipt")):
                with contextlib.redirect_stdout(output), self.assertRaises(work.WorkError):
                    work.command_pr_link(args, FakeRunner(responses), config(), current)
            payload = json.loads(output.getvalue())
            self.assertTrue(payload["partial"])
            self.assertEqual(payload["stage"], "audit")
            self.assertFalse(payload["recovery_fallback_used"])
            self.assertIsNone(payload["recovery_error"])
            self.assertNotIn("before", payload)
            self.assertNotIn("after", payload)
            recovery_path = Path(payload["recovery_path"])
            self.assertEqual(recovery_path.parent, Path(directory))
            self.assertIn("github-work-recovery", recovery_path.name)
            self.assertEqual(stat.S_IMODE(recovery_path.stat().st_mode), 0o600)
            recovery = json.loads(recovery_path.read_text(encoding="utf-8"))
            self.assertEqual(recovery["before"], "Original body\n")
            self.assertIn("Refs sample-space/sample-app#4", recovery["after"])
            recovery_path.unlink()

    def test_pr_template_placeholder_is_replaced(self):
        rendered = work.linked_body("Refs #ISSUE\n", "sample-space/sample-app#3", "refs", "sample-space/sample-app")
        self.assertEqual(rendered, "Refs sample-space/sample-app#3\n")

    def test_finality_blocks_open_relationships(self):
        result = work.finality_result({
            "blockedBy": {"nodes": [{"state": "OPEN"}], "totalCount": 1},
            "subIssuesSummary": {"total": 2, "completed": 1},
        })
        self.assertEqual(result, {
            "eligible": False,
            "failure": None,
            "incomplete_sub_issues": 1,
            "open_blockers": 1,
            "reason": "not_ready",
        })

    def test_finality_accepts_observed_empty_blocked_by_connection(self):
        result = work.finality_result({
            "blockedBy": {"nodes": [], "totalCount": 0},
            "subIssuesSummary": {"total": 0, "completed": 0},
        })
        self.assertTrue(result["eligible"])
        self.assertEqual(result["reason"], "ready")

    def test_finality_returns_eligibility_exit_for_missing_classification(self):
        responses = managed_preflight_responses(labels=[])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = work.command_finality(
                Namespace(issue="sample-space/sample-app#4"), FakeRunner(responses), config()
            )
        self.assertEqual(result, 1)
        self.assertFalse(json.loads(output.getvalue())["eligible"])

    def test_finality_fails_closed_on_missing_or_malformed_fields(self):
        for state in (
            {},
            {"blockedBy": None, "subIssuesSummary": {}},
            {
                "blockedBy": {"nodes": [], "totalCount": 1},
                "subIssuesSummary": {"total": "0", "completed": 0},
            },
        ):
            with self.subTest(state=state), self.assertRaises(work.WorkError):
                work.finality_result(state)

    def test_ownership_candidates_are_unique_and_area_scoped(self):
        ownership = {"mappings": [
            {"repo": "sample-space/sample-app", "area": "ui", "logins": ["sample-user"]},
            {"repo": "sample-space/sample-app", "area": "api", "logins": ["other-user"]},
        ]}
        self.assertEqual(work.ownership_candidates(ownership, "sample-space/sample-app", "ui"), ["sample-user"])

    def test_load_targets_rejects_unknown_adapter(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "targets.yml"
            path.write_text(json.dumps({"targets": [{"repo": "sample-space/sample-app", "adapter": "mystery", "classification": "native-type"}]}))
            with self.assertRaises(work.WorkError):
                work.load_targets(path)

    def test_load_targets_rejects_non_string_target_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "targets.json"
            path.write_text(json.dumps({
                "targets": [{
                    "repo": ["sample-space/sample-app"],
                    "adapter": "plain",
                    "classification": "native-type",
                }],
            }), encoding="utf-8")
            with self.assertRaisesRegex(work.WorkError, "repo must be a non-empty string"):
                work.load_targets(path)

    def test_load_targets_rejects_non_string_work_title(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "targets.json"
            target = config()["targets"][0]
            target["work_title"] = ["not", "a", "string"]
            path.write_text(json.dumps({"targets": [target]}), encoding="utf-8")
            with self.assertRaisesRegex(work.WorkError, "work_title.*non-empty string"):
                work.load_targets(path)

    def test_load_targets_rejects_non_string_auxiliary_work_title(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "targets.json"
            path.write_text(json.dumps({
                "targets": config()["targets"],
                "auxiliary_repositories": [{
                    "repo": "sample-space/aux-app",
                    "classification": "native-type",
                    "work_title": ["not", "a", "string"],
                }],
            }), encoding="utf-8")
            with self.assertRaisesRegex(work.WorkError, "work_title.*non-empty string"):
                work.load_targets(path)

    def test_load_targets_rejects_unhashable_auxiliary_classification(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "targets.json"
            path.write_text(json.dumps({
                "targets": config()["targets"],
                "auxiliary_repositories": [{
                    "repo": "sample-space/aux-app",
                    "classification": ["native-type"],
                }],
            }), encoding="utf-8")
            with self.assertRaisesRegex(work.WorkError, "classification must be a non-empty string"):
                work.load_targets(path)

    def test_load_targets_maps_non_utf8_config_to_operational_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "targets.json"
            path.write_bytes(b"bad-utf8-\x96")
            with self.assertRaisesRegex(work.WorkError, "cannot load JSON-compatible YAML"):
                work.load_targets(path)

    def test_ownership_candidates_prefers_default_then_wildcard_then_specific(self):
        ownership = {
            "mappings": [
                {"repo": "sample-space/sample-app", "logins": ["default-user"]},
                {"repo": "sample-space/sample-app", "area": "*", "logins": ["wild-user"]},
                {"repo": "sample-space/sample-app", "area": "web", "logins": ["web-user"]},
            ],
        }
        self.assertEqual(
            work.ownership_candidates(ownership, "sample-space/sample-app", None),
            ["default-user"],
        )
        self.assertEqual(
            work.ownership_candidates(ownership, "sample-space/sample-app", "web"),
            ["web-user"],
        )
        self.assertEqual(
            work.ownership_candidates(ownership, "sample-space/sample-app", "api"),
            ["wild-user"],
        )

    def test_ownership_resolution_reports_ineligible_default_for_unknown_explicit_area(self):
        ownership = {
            "mappings": [
                {"repo": "sample-space/sample-app", "logins": ["default-user"]},
                {"repo": "sample-space/sample-app", "area": "web", "logins": ["web-user"]},
            ],
        }
        self.assertEqual(
            work.ownership_resolution(ownership, "sample-space/sample-app", "web"),
            (["web-user"], "exact"),
        )
        wildcard_ownership = {
            "mappings": [{
                "repo": "sample-space/sample-app",
                "area": "*",
                "logins": ["wild-user"],
            }],
        }
        self.assertEqual(
            work.ownership_resolution(wildcard_ownership, "sample-space/sample-app", "*"),
            (["wild-user"], "wildcard"),
        )
        self.assertEqual(
            work.ownership_resolution(ownership, "sample-space/sample-app", "webb"),
            ([], "default-ineligible"),
        )

    def test_ownership_resolution_distinguishes_repo_and_area_gaps(self):
        ownership = {
            "mappings": [{
                "repo": "sample-space/sample-app",
                "area": "web",
                "logins": ["web-user"],
            }],
        }
        self.assertEqual(
            work.ownership_resolution(ownership, "sample-space/sample-app", "infra"),
            ([], "area-unmapped"),
        )
        self.assertEqual(
            work.ownership_resolution(ownership, "sample-space/other-app", "web"),
            ([], "repo-unmapped"),
        )
        self.assertEqual(
            work.ownership_resolution(ownership, "sample-space/other-app", None),
            ([], "repo-unmapped"),
        )

    def test_load_ownership_rejects_empty_login_mapping(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ownership.json"
            path.write_text(json.dumps({
                "mappings": [{
                    "repo": "sample-space/sample-app",
                    "logins": [],
                }],
            }), encoding="utf-8")
            with self.assertRaisesRegex(work.WorkError, "non-empty array"):
                work.load_ownership(str(path))

    def test_load_ownership_rejects_non_array_mappings(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ownership.json"
            path.write_text(json.dumps({
                "mappings": {"sample-space/sample-app": ["sample-user"]},
            }), encoding="utf-8")
            with self.assertRaisesRegex(work.WorkError, "mappings array"):
                work.load_ownership(path)

    def test_load_ownership_accepts_repo_wide_mapping_without_area(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ownership.json"
            path.write_text(json.dumps({
                "mappings": [{
                    "repo": "sample-space/sample-app",
                    "logins": ["sample-user"],
                }],
            }), encoding="utf-8")
            ownership = work.load_ownership(path)
            self.assertEqual(
                work.ownership_candidates(ownership, "sample-space/sample-app", None),
                ["sample-user"],
            )
            self.assertEqual(
                work.ownership_candidates(ownership, "sample-space/sample-app", "ui"),
                [],
            )

    def test_labels_ensure_creates_only_missing_after_preflight(self):
        existing = [{"name": "type:bug", "color": "000000", "description": "preserved"}]
        runner = FakeRunner([
            work.CommandResult(stdout="gh version 2.96.0\n"), work.CommandResult(), work.CommandResult(), [existing],
        ])
        current_receipt = receipt()
        args = Namespace(repos="sample-space/sample-app")
        with contextlib.redirect_stdout(io.StringIO()):
            work.command_labels_ensure(args, runner, config(), current_receipt)
        create_calls = [call for call in runner.calls if call[0][:2] == ["label", "create"]]
        self.assertEqual(len(create_calls), 2)
        self.assertEqual(len(current_receipt.data["operations"]), 2)
        self.assertNotIn("--force", create_calls[0][0])

    def test_labels_ensure_reports_created_labels_when_audit_fails(self):
        current = receipt()
        runner = FakeRunner(managed_preflight_responses(labels=[]))
        output = io.StringIO()
        with mock.patch.object(current, "save", side_effect=work.WorkError("cannot save receipt")):
            with contextlib.redirect_stdout(output), self.assertRaises(work.WorkError):
                work.command_labels_ensure(
                    Namespace(repos="sample-space/sample-app"), runner, config(), current
                )
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["stage"], "audit")
        self.assertEqual(payload["created"], [])
        self.assertEqual(
            payload["failed_label"],
            {"name": "type:bug", "repo": "sample-space/sample-app"},
        )

    def test_labels_dry_run_never_records_mutation(self):
        runner = FakeRunner([
            work.CommandResult(stdout="gh version 2.96.0\n"), work.CommandResult(), work.CommandResult(), [],
        ], dry_run=True)
        current_receipt = receipt()
        with contextlib.redirect_stdout(io.StringIO()):
            work.command_labels_ensure(Namespace(repos="sample-space/sample-app"), runner, config(), current_receipt)
        self.assertEqual(current_receipt.data["operations"], [])

    def test_issue_create_preflights_native_type_and_relationship_direction(self):
        responses = [
            work.CommandResult(stdout="gh version 2.96.0\n"), work.CommandResult(),
            work.CommandResult(), [{"name": "Bug"}, {"name": "Feature"}, {"name": "Task"}],
            work.CommandResult(stdout="https://github.com/sample-space/sample-app/issues/7\n"),
            work.CommandResult(),
        ]
        runner = FakeRunner(responses)
        args = Namespace(repo="sample-space/sample-app", type="Task", title="Sample", body_file=None, parent="sample-space/sample-app#2", blocking=None, assignee=None)
        current_receipt = receipt()
        with contextlib.redirect_stdout(io.StringIO()):
            work.command_issue_create(args, runner, config("native-type"), current_receipt)
        commands = [call[0] for call in runner.calls]
        self.assertIn(["issue", "edit", "https://github.com/sample-space/sample-app/issues/2", "--add-sub-issue", "https://github.com/sample-space/sample-app/issues/7"], commands)
        self.assertEqual([operation["kind"] for operation in current_receipt.data["operations"]], ["issue-created", "relationship-added"])

    def test_managed_issue_creation_records_classification_label_for_restore(self):
        runner = FakeRunner([
            work.CommandResult(stdout="https://github.com/sample-space/sample-app/issues/7\n")
        ])
        args = Namespace(
            repo="sample-space/sample-app", type="Task", title="Sample", body_file=None,
            parent=None, blocking=None, assignee=None, preflighted=True,
        )
        current_receipt = receipt()
        with mock.patch.dict(
            work.MANAGED_LABELS,
            {"task": ("kind:task", "8250DF", "Bounded implementation or follow-up work")},
            clear=True,
        ), contextlib.redirect_stdout(io.StringIO()):
            work.command_issue_create(args, runner, config(), current_receipt)
        self.assertEqual(
            [operation["kind"] for operation in current_receipt.data["operations"]],
            ["issue-created", "issue-label-added"],
        )
        self.assertEqual(current_receipt.data["operations"][1]["name"], "kind:task")
        self.assertIn("kind:task", runner.calls[0][0])

    def test_temporary_body_writes_utf8(self):
        with work.temporary_body("Unicode — body 🤖") as path:
            self.assertEqual(Path(path).read_text(encoding="utf-8"), "Unicode — body 🤖")

    def test_temporary_body_maps_filesystem_errors(self):
        with mock.patch.object(
            work.tempfile,
            "NamedTemporaryFile",
            side_effect=OSError("read-only filesystem"),
        ):
            with self.assertRaisesRegex(work.WorkError, "cannot write temporary body"):
                with work.temporary_body("body"):
                    pass

    def test_temporary_body_removes_partial_file_when_write_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            partial = Path(directory) / "partial.md"
            partial.write_text("partial", encoding="utf-8")
            handle = mock.MagicMock()
            handle.__enter__.return_value = handle
            handle.__exit__.return_value = False
            handle.name = str(partial)
            handle.write.side_effect = OSError("disk full")
            with mock.patch.object(work.tempfile, "NamedTemporaryFile", return_value=handle):
                with self.assertRaises(work.WorkError):
                    with work.temporary_body("private body"):
                        pass
            self.assertFalse(partial.exists())

    def test_recovery_writer_falls_back_to_independent_temp_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            receipt_path = Path(directory) / "receipt.json"
            failure = OSError(28, "No space left on device")
            with mock.patch.object(work, "write_recovery_file", side_effect=[failure, None]):
                recovery = work.write_private_recovery_payload(
                    {"before": "private"}, receipt_path
                )
            self.assertTrue(recovery["recovery_fallback_used"])
            self.assertEqual(recovery["recovery_error"], "primary-write-failed")
            self.assertEqual(recovery["recovery_primary_errno"], 28)
            self.assertIn("github-work-recovery", recovery["recovery_path"])

    def test_recovery_writer_double_failure_remains_structured(self):
        receipt_path = Path("/private/receipt.json")
        failures = [
            OSError(28, "No space left on device"),
            OSError(30, "Read-only file system"),
        ]
        with mock.patch.object(work, "write_recovery_file", side_effect=failures):
            recovery = work.write_private_recovery_payload({"before": "private"}, receipt_path)
        self.assertIsNone(recovery["recovery_path"])
        self.assertEqual(recovery["recovery_error"], "primary-and-fallback-write-failed")
        self.assertFalse(recovery["recovery_fallback_used"])
        self.assertEqual(recovery["recovery_primary_errno"], 28)
        self.assertEqual(recovery["recovery_fallback_errno"], 30)
        self.assertEqual(set(recovery), set(work.recovery_fields()))

    def test_issue_create_reports_unknown_mutation_when_gh_returns_no_url(self):
        responses = managed_preflight_responses() + [work.CommandResult()]
        args = Namespace(
            repo="sample-space/sample-app", type="Task", title="Sample", body_file=None,
            parent=None, blocking=None, assignee=None,
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaisesRegex(
            work.PartialWorkError, "returned no issue URL"
        ):
            work.command_issue_create(args, FakeRunner(responses), config(), receipt())
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["stage"], "mutation-result-unknown")
        self.assertEqual(payload["title"], "Sample")
        self.assertIsNone(payload["url"])

    def test_issue_create_reports_partial_when_gh_returns_malformed_url(self):
        responses = managed_preflight_responses() + [
            work.CommandResult(stdout="https://github.com/sample-space/sample-app/issues/7\nversion nag\n"),
        ]
        args = Namespace(
            repo="sample-space/sample-app", type="Task", title="Sample", body_file=None,
            parent=None, blocking=None, assignee=None,
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(work.PartialWorkError):
            work.command_issue_create(args, FakeRunner(responses), config(), receipt())
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["stage"], "mutation-result-unknown")
        self.assertEqual(payload["url"], "version nag")
        self.assertEqual(payload["title"], "Sample")

    def test_issue_create_reports_partial_url_when_relationship_fails(self):
        created = "https://github.com/sample-space/sample-app/issues/7"
        responses = managed_preflight_responses() + [
            work.CommandResult(stdout=created + "\n"),
            work.CommandResult(returncode=1, stderr="parent locked"),
        ]
        args = Namespace(
            repo="sample-space/sample-app", type="Task", title="Sample", body_file=None,
            parent="sample-space/sample-app#2", blocking=None, assignee=None,
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with self.assertRaises(work.WorkError):
                work.command_issue_create(args, FakeRunner(responses), config(), receipt())
        self.assertEqual(
            json.loads(output.getvalue()),
            {
                "completed_relationships": [],
                "partial": True,
                "relationship": {
                    "relation": "sub-issue",
                    "source": "https://github.com/sample-space/sample-app/issues/2",
                    "target": created,
                },
                "relationship_added": None,
                "repo": "sample-space/sample-app",
                "requested_relationships": [
                    {
                        "relation": "sub-issue",
                        "source": "https://github.com/sample-space/sample-app/issues/2",
                    },
                ],
                "stage": "mutation-result-unknown",
                "title": "Sample",
                "type": "Task",
                "url": created,
            },
        )

    def test_issue_create_reports_audit_stage_when_receipt_write_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            current = receipt(str(Path(directory) / "receipt.json"))
            created = "https://github.com/sample-space/sample-app/issues/7"
            responses = managed_preflight_responses() + [
                work.CommandResult(stdout=created + "\n"),
            ]
            args = Namespace(
                repo="sample-space/sample-app",
                type="Task",
                title="Sample",
                body_file=None,
                parent=None,
                blocking=None,
                assignee=None,
            )
            output = io.StringIO()
            with mock.patch.object(current, "save", side_effect=work.WorkError("disk full")):
                with contextlib.redirect_stdout(output), self.assertRaises(work.PartialWorkError):
                    work.command_issue_create(args, FakeRunner(responses), config(), current)
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["stage"], "audit")
            self.assertEqual(payload["completed_relationships"], [])
            self.assertEqual(payload["requested_relationships"], [])
            self.assertIsNone(payload["relationship"])
            self.assertFalse(payload["relationship_added"])

    def test_issue_create_maps_non_utf8_body_to_operational_error(self):
        with tempfile.TemporaryDirectory() as directory:
            body_path = Path(directory) / "body.md"
            body_path.write_bytes(b"bad-utf8-\x96")
            args = Namespace(
                repo="sample-space/sample-app",
                type="Task",
                title="Sample",
                body_file=str(body_path),
                parent=None,
                blocking=None,
                assignee=None,
            )
            with self.assertRaisesRegex(work.WorkError, "cannot read issue body file"):
                work.command_issue_create(
                    args,
                    FakeRunner(managed_preflight_responses()),
                    config(),
                    receipt(),
                )

    def test_issue_create_rejects_unassignable_login_before_creation(self):
        responses = managed_preflight_responses() + [work.CommandResult(returncode=1, stderr="not assignable")]
        runner = FakeRunner(responses)
        args = Namespace(repo="sample-space/sample-app", type="Task", title="Sample", body_file=None, parent=None, blocking=None, assignee="missing-user")
        with self.assertRaises(work.WorkError):
            work.command_issue_create(args, runner, config(), receipt())
        self.assertFalse(any(call[0][:2] == ["issue", "create"] for call in runner.calls))

    def test_issue_create_url_encodes_assignee_probe(self):
        responses = managed_preflight_responses() + [
            work.CommandResult(returncode=1, stderr="not assignable")
        ]
        runner = FakeRunner(responses)
        args = Namespace(
            repo="sample-space/sample-app",
            type="Task",
            title="Sample",
            body_file=None,
            parent=None,
            blocking=None,
            assignee="missing/user",
        )
        with self.assertRaises(work.WorkError):
            work.command_issue_create(args, runner, config(), receipt())
        self.assertIn(
            ["api", "repos/sample-space/sample-app/assignees/missing%2Fuser"],
            [call[0] for call in runner.calls],
        )

    def test_assign_ambiguity_adds_needs_owner_not_assignee(self):
        ownership = {"mappings": [{"repo": "sample-space/sample-app", "area": "*", "logins": ["one-user", "two-user"]}]}
        responses = managed_preflight_responses() + [
            {"labels": [], "assignees": []}, [], work.CommandResult(), work.CommandResult(),
        ]
        runner = FakeRunner(responses)
        args = Namespace(issue="sample-space/sample-app#4", assignee=None, from_ownership_map=True, area=None)
        with contextlib.redirect_stdout(io.StringIO()):
            work.command_assign(args, runner, config(), ownership, receipt())
        commands = [call[0] for call in runner.calls]
        self.assertIn(["issue", "edit", "sample-space/sample-app#4", "--add-label", "needs-owner"], commands)
        self.assertFalse(any("--add-assignee" in command for command in commands))

    def test_assign_map_preserves_existing_human_owner_without_escalation(self):
        ownership = {"mappings": [{
            "repo": "sample-space/sample-app",
            "area": "web",
            "logins": ["one-user", "two-user"],
        }]}
        current_state = {
            "labels": [{"name": "needs-owner"}],
            "assignees": [{"login": "existing-user"}],
        }
        responses = managed_preflight_responses() + [
            current_state,
            current_state,
            work.CommandResult(),
        ]
        runner = FakeRunner(responses)
        args = Namespace(
            issue="sample-space/sample-app#4",
            assignee=None,
            from_ownership_map=True,
            area="web",
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            work.command_assign(args, runner, config(), ownership, receipt())
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["assignees"], ["existing-user"])
        self.assertEqual(payload["candidates"], ["one-user", "two-user"])
        self.assertEqual(payload["reason"], "existing-owner")
        self.assertTrue(payload["needs_owner_removed"])
        commands = [call[0] for call in runner.calls]
        self.assertIn(
            ["issue", "edit", "sample-space/sample-app#4", "--remove-label", "needs-owner"],
            commands,
        )
        self.assertFalse(any("--add-label" in command for command in commands))
        self.assertFalse(any("label" in command and "create" in command for command in commands))

    def test_assign_map_adds_resolved_owner_without_replacing_existing_owner(self):
        ownership = {"mappings": [{
            "repo": "sample-space/sample-app",
            "area": "web",
            "logins": ["resolved-user"],
        }]}
        responses = managed_preflight_responses() + [
            {"labels": [], "assignees": [{"login": "existing-user"}]},
            work.CommandResult(),
            work.CommandResult(),
        ]
        runner = FakeRunner(responses)
        args = Namespace(
            issue="sample-space/sample-app#4",
            assignee=None,
            from_ownership_map=True,
            area="web",
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            work.command_assign(args, runner, config(), ownership, receipt())
        payload = json.loads(output.getvalue())
        self.assertTrue(payload["assigned"])
        self.assertEqual(payload["assignee"], "resolved-user")
        self.assertIn(
            ["issue", "edit", "sample-space/sample-app#4", "--add-assignee", "resolved-user"],
            [call[0] for call in runner.calls],
        )

    def test_assign_needs_owner_partial_preserves_resolution_context(self):
        with tempfile.TemporaryDirectory() as directory:
            ownership = {"mappings": [{
                "repo": "sample-space/sample-app",
                "area": "*",
                "logins": ["one-user", "two-user"],
            }]}
            responses = managed_preflight_responses() + [
                {"labels": [], "assignees": []},
                [],
                work.CommandResult(),
            ]
            args = Namespace(
                issue="sample-space/sample-app#4",
                assignee=None,
                from_ownership_map=True,
                area=None,
            )
            output = io.StringIO()
            with mock.patch.object(work.os, "open", side_effect=PermissionError("denied")):
                with contextlib.redirect_stdout(output), self.assertRaises(work.WorkError):
                    work.command_assign(
                        args,
                        FakeRunner(responses),
                        config(),
                        ownership,
                        receipt(str(Path(directory) / "receipt.json")),
                    )
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["candidates"], ["one-user", "two-user"])
            self.assertEqual(payload["ownership_source"], "wildcard")
            self.assertEqual(payload["stage"], "audit")

    def test_assign_dry_run_reports_planned_stale_label_removal(self):
        ownership = {"mappings": [{
            "repo": "sample-space/sample-app",
            "area": "web",
            "logins": ["existing-user"],
        }]}
        current_state = {
            "labels": [{"name": "needs-owner"}],
            "assignees": [{"login": "existing-user"}],
        }
        runner = FakeRunner(
            managed_preflight_responses() + [current_state, current_state],
            dry_run=True,
        )
        args = Namespace(
            issue="sample-space/sample-app#4",
            assignee=None,
            from_ownership_map=True,
            area="web",
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            work.command_assign(args, runner, config(), ownership, receipt())
        payload = json.loads(output.getvalue())
        self.assertTrue(payload["dry_run"])
        self.assertTrue(payload["needs_owner_removed"])

    def test_assign_success_tolerates_concurrent_stale_label_removal(self):
        ownership = {"mappings": [{
            "repo": "sample-space/sample-app",
            "area": "web",
            "logins": ["resolved-user"],
        }]}
        responses = managed_preflight_responses() + [
            {"labels": [{"name": "needs-owner"}], "assignees": []},
            work.CommandResult(),
            work.CommandResult(),
            {"labels": [], "assignees": [{"login": "resolved-user"}]},
        ]
        args = Namespace(
            issue="sample-space/sample-app#4",
            assignee=None,
            from_ownership_map=True,
            area="web",
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            work.command_assign(args, FakeRunner(responses), config(), ownership, receipt())
        payload = json.loads(output.getvalue())
        self.assertTrue(payload["assigned"])
        self.assertFalse(payload["needs_owner_removed"])

    def test_assign_rejects_empty_or_irrelevant_area_before_preflight(self):
        for args, message in [
            (Namespace(issue="sample-space/sample-app#4", assignee=None,
                       from_ownership_map=True, area=""), "empty"),
            (Namespace(issue="sample-space/sample-app#4", assignee="sample-user",
                       from_ownership_map=False, area="web"), "requires"),
        ]:
            with self.subTest(message=message):
                with self.assertRaisesRegex(work.WorkError, message):
                    work.command_assign(args, FakeRunner([]), config(), None, receipt())

    def test_pr_link_uses_body_file_and_preflight(self):
        responses = managed_preflight_responses() + [{"body": "Closes #4\n", "url": "https://github.com/sample-space/sample-app/pull/2"}, work.CommandResult()]
        runner = FakeRunner(responses)
        args = Namespace(pr="https://github.com/sample-space/sample-app/pull/2", issue="sample-space/sample-app#4", mode="refs")
        with contextlib.redirect_stdout(io.StringIO()):
            work.command_pr_link(args, runner, config(), receipt())
        edit = next(call[0] for call in runner.calls if call[0][:2] == ["pr", "edit"])
        self.assertIn("--body-file", edit)

    def test_assign_marks_failed_mutation_result_as_unknown(self):
        current = receipt()
        responses = managed_preflight_responses() + [
            {"labels": [], "assignees": []},
            work.CommandResult(),
            work.CommandResult(returncode=1, stderr="network timeout"),
        ]
        args = Namespace(
            issue="sample-space/sample-app#4",
            assignee="sample-user",
            from_ownership_map=False,
            area=None,
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(work.WorkError):
            work.command_assign(args, FakeRunner(responses), config(), None, current)
        self.assertEqual(json.loads(output.getvalue())["stage"], "mutation-result-unknown")

    def test_assign_reports_partial_state_when_receipt_write_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            current = receipt(str(Path(directory) / "receipt.json"))
            responses = managed_preflight_responses() + [
                {"labels": [], "assignees": []},
                work.CommandResult(),
                work.CommandResult(),
            ]
            args = Namespace(
                issue="sample-space/sample-app#4",
                assignee="sample-user",
                from_ownership_map=False,
                area=None,
            )
            output = io.StringIO()
            with mock.patch.object(work.os, "open", side_effect=PermissionError("denied")):
                with contextlib.redirect_stdout(output), self.assertRaises(work.WorkError):
                    work.command_assign(args, FakeRunner(responses), config(), None, current)
            self.assertEqual(
                json.loads(output.getvalue()),
                {
                    "assignee": "sample-user",
                    "dry_run": False,
                    "issue": "https://github.com/sample-space/sample-app/issues/4",
                    "needs_owner_removed": False,
                    "ownership_source": "explicit",
                    "partial": True,
                    "stage": "audit",
                },
            )

    def test_work_graph_preserves_partial_receipt_on_failure(self):
        targets = config(repos=["sample-space/one-app", "sample-space/two-app"])
        responses = [work.CommandResult(stdout="gh version 2.96.0\n"), work.CommandResult()]
        for _ in range(2):
            responses.extend([work.CommandResult(), PAGED_ALL_LABELS])
        runner = FakeRunner(responses)
        current_receipt = receipt()
        calls = 0

        def create(args, runner, config, receipt, **_kwargs):
            nonlocal calls
            calls += 1
            if calls == 1:
                receipt.add("issue-created", issue="https://github.com/sample-space/one-app/issues/1")
                payload = {"repo": args.repo, "url": "https://github.com/sample-space/one-app/issues/1"}
                return payload
            raise work.WorkError("second target failed")

        args = Namespace(repos="all", umbrella="sample-space/one-app#9", assignee=None)
        output = io.StringIO()
        with mock.patch.object(work, "command_issue_create", side_effect=create):
            with contextlib.redirect_stdout(output), self.assertRaises(work.PartialWorkError) as caught:
                work.command_work_graph_create(args, runner, targets, current_receipt)
        payload = json.loads(output.getvalue())
        self.assertEqual(caught.exception.payload, payload)
        self.assertEqual(payload["created_tasks"], 1)
        self.assertEqual(payload["failed_repo"], "sample-space/two-app")
        self.assertEqual(payload["issues"][0]["url"], "https://github.com/sample-space/one-app/issues/1")
        self.assertIsNone(payload["failed_partial"])
        self.assertEqual(len(current_receipt.data["operations"]), 1)

    def test_work_graph_preserves_structured_child_partial_payload(self):
        targets = config(repos=["sample-space/one-app"])
        responses = [
            work.CommandResult(stdout="gh version 2.96.0\n"),
            work.CommandResult(),
            work.CommandResult(),
            PAGED_ALL_LABELS,
        ]

        failed = {
            "partial": True,
            "repo": "sample-space/one-app",
            "type": "Task",
            "url": "https://github.com/sample-space/one-app/issues/2",
        }

        def create(*_args, **_kwargs):
            raise work.PartialWorkError("child failed", failed)

        output = io.StringIO()
        args = Namespace(repos="all", umbrella="sample-space/one-app#9", assignee=None)
        with mock.patch.object(work, "command_issue_create", side_effect=create):
            with contextlib.redirect_stdout(output), self.assertRaises(work.PartialWorkError) as caught:
                work.command_work_graph_create(args, FakeRunner(responses), targets, receipt())
        payload = json.loads(output.getvalue())
        self.assertEqual(caught.exception.payload, payload)
        self.assertTrue(payload["partial"])
        self.assertEqual(payload["failed_repo"], "sample-space/one-app")
        self.assertEqual(payload["failed_partial"], failed)

    def test_work_graph_first_child_failure_is_not_partial(self):
        targets = config(repos=["sample-space/one-app"])
        responses = [
            work.CommandResult(stdout="gh version 2.96.0\n"),
            work.CommandResult(),
            work.CommandResult(),
            PAGED_ALL_LABELS,
        ]
        args = Namespace(repos="all", umbrella="sample-space/one-app#9", assignee=None)
        output = io.StringIO()
        with mock.patch.object(
            work,
            "command_issue_create",
            side_effect=work.WorkError("create rejected"),
        ):
            with contextlib.redirect_stdout(output), self.assertRaises(work.WorkError) as caught:
                work.command_work_graph_create(args, FakeRunner(responses), targets, receipt())
        self.assertNotIsInstance(caught.exception, work.PartialWorkError)
        payload = json.loads(output.getvalue())
        self.assertFalse(payload["partial"])
        self.assertEqual(payload["created_tasks"], 0)

    def test_receipt_is_strict_private_and_bound(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            current = receipt(str(path))
            current.add("label-created", repo="sample-space/sample-app", name="type:task")
            current.add("pr-body-changed", pr="https://github.com/sample-space/sample-app/pull/1", before="", after="Refs #1\n")
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            upgraded = work.Receipt(str(path), source_sha="c" * 40, config_digest="d" * 64)
            self.assertEqual(upgraded.data["source_sha"], SOURCE)
            self.assertEqual(upgraded.data["config_digest"], DIGEST)
            upgraded.add("label-created", repo="sample-space/sample-app", name="type:feature")
            self.assertEqual(upgraded.data["operations"][0]["source_sha"], SOURCE)
            self.assertEqual(upgraded.data["operations"][0]["config_digest"], DIGEST)
            self.assertEqual(upgraded.data["operations"][-1]["source_sha"], "c" * 40)
            self.assertEqual(upgraded.data["operations"][-1]["config_digest"], "d" * 64)
            path.chmod(0o644)
            with self.assertRaises(work.WorkError):
                receipt(str(path))
            path.chmod(0o4600)
            with self.assertRaises(work.WorkError):
                receipt(str(path))
            path.chmod(0o600)
            loaded = json.loads(path.read_text())
            del loaded["operations"][0]["operation_id"]
            path.write_text(json.dumps(loaded))
            path.chmod(0o600)
            with self.assertRaises(work.WorkError):
                receipt(str(path))

    def test_receipt_schema_one_remains_loadable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            path.write_text(json.dumps({
                "schema_version": 1,
                "receipt_id": "legacy-receipt",
                "source_sha": SOURCE,
                "config_digest": DIGEST,
                "operations": [],
            }), encoding="utf-8")
            path.chmod(0o600)
            current = work.Receipt(str(path), source_sha=SOURCE, config_digest=None)
            self.assertEqual(current.data["schema_version"], 1)

    def test_receipt_schema_two_from_previous_release_remains_loadable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            path.write_text(json.dumps({
                "schema_version": 2,
                "receipt_id": "previous-release",
                "source_sha": SOURCE,
                "config_digest": DIGEST,
                "operations": [{
                    "operation_id": "operation-1",
                    "status": "restored",
                    "kind": "label-created",
                    "repo": "sample-space/sample-app",
                    "name": "type:task",
                    "restore_mutated": True,
                    "restored_by_source_sha": SOURCE,
                    "restored_by_config_digest": DIGEST,
                    "restored_config_requested": False,
                    "restored_config_unavailable": False,
                }],
            }), encoding="utf-8")
            path.chmod(0o600)
            current = work.Receipt(str(path), source_sha=SOURCE, config_digest=None)
            self.assertEqual(current.data["schema_version"], 2)

    def test_receipt_schema_three_requires_complete_restore_audit_fields(self):
        current = receipt()
        current.add("label-created", repo="sample-space/sample-app", name="type:task")
        current.data["operations"][0]["status"] = "restored"
        with self.assertRaisesRegex(work.WorkError, "restored operation is missing"):
            current.validate()

    def test_receipt_schema_three_rejects_null_restoring_source(self):
        current = receipt()
        current.add("label-created", repo="sample-space/sample-app", name="type:task")
        operation = current.data["operations"][0]
        operation.update({
            "status": "restored",
            "restore_mutated": True,
            "restored_by_source_sha": None,
            "restored_by_config_digest": None,
            "restored_config_requested": False,
            "restored_config_status": "absent",
            "restored_config_unavailable": False,
        })
        with self.assertRaisesRegex(work.WorkError, "restored_by_source_sha must not be null"):
            current.validate()

    def test_receipt_validation_accepts_explicitly_unavailable_config_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            path.write_text(json.dumps({
                "schema_version": work.SCHEMA_VERSION,
                "receipt_id": "receipt",
                "source_sha": SOURCE,
                "config_digest": None,
                "operations": [],
            }), encoding="utf-8")
            path.chmod(0o600)
            current = work.Receipt(str(path), source_sha=SOURCE, config_digest=None)
            self.assertIsNone(current.data["config_digest"])

    def test_receipt_save_uses_exclusive_non_following_temporary_file(self):
        with tempfile.TemporaryDirectory() as directory:
            current = receipt(str(Path(directory) / "receipt.json"))
            original_open = work.os.open
            with mock.patch.object(work.os, "open", wraps=original_open) as opened:
                current.save()
            flags = opened.call_args.args[1]
            self.assertTrue(flags & work.os.O_EXCL)
            if hasattr(work.os, "O_NOFOLLOW"):
                self.assertTrue(flags & work.os.O_NOFOLLOW)

    def test_receipt_save_maps_os_errors_to_work_error(self):
        with tempfile.TemporaryDirectory() as directory:
            current = receipt(str(Path(directory) / "receipt.json"))
            with mock.patch.object(work.os, "open", side_effect=PermissionError("denied")):
                with self.assertRaisesRegex(work.WorkError, "cannot save receipt"):
                    current.save()

    def test_main_hides_success_output_when_noop_receipt_save_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "targets.json"
            receipt_path = root / "noop-receipt.json"
            config_path.write_text(json.dumps(config()), encoding="utf-8")
            runner = FakeRunner(managed_preflight_responses())
            stdout = io.StringIO()
            stderr = io.StringIO()
            with mock.patch.object(work.os, "open", side_effect=PermissionError("denied")):
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    result = work.main([
                        "--config", str(config_path),
                        "labels", "ensure",
                        "--repos", "sample-space/sample-app",
                        "--receipt", str(receipt_path),
                    ], runner=runner)
            self.assertEqual(result, 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("cannot save receipt", stderr.getvalue())

    def test_main_restore_tolerates_invalid_optional_target_config(self):
        with tempfile.TemporaryDirectory() as directory:
            invalid_config = Path(directory) / "invalid-targets.json"
            invalid_config.write_text("{", encoding="utf-8")
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add(
                "issue-label-added",
                issue="https://github.com/sample-space/sample-app/issues/9",
                name="needs-owner",
            )
            responses = restore_preflight_responses() + [{"labels": [], "assignees": []}]
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = work.main([
                    "--config", str(invalid_config),
                    "restore", "--receipt", path,
                ], runner=FakeRunner(responses))
            self.assertEqual(result, 0)
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["reason"], "restored")
            self.assertTrue(payload["config_requested"])
            self.assertEqual(payload["config_status"], "invalid")
            self.assertTrue(payload["config_unavailable"])
            restored = receipt(path)
            operation = restored.data["operations"][0]
            self.assertEqual(
                operation["restored_by_config_digest"],
                hashlib.sha256(b"{").hexdigest(),
            )
            self.assertTrue(operation["restored_config_requested"])
            self.assertEqual(operation["restored_config_status"], "invalid")
            self.assertTrue(operation["restored_config_unavailable"])

    def test_main_restore_records_empty_supplied_config_as_unavailable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add(
                "issue-label-added",
                issue="https://github.com/sample-space/sample-app/issues/9",
                name="needs-owner",
            )
            responses = restore_preflight_responses() + [{"labels": [], "assignees": []}]
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = work.main([
                    "--config", "",
                    "--ownership-config", "",
                    "restore", "--receipt", path,
                ], runner=FakeRunner(responses))
            self.assertEqual(result, 0)
            payload = json.loads(output.getvalue())
            self.assertTrue(payload["config_requested"])
            self.assertEqual(payload["config_status"], "empty")
            self.assertTrue(payload["config_unavailable"])

    def test_restore_dry_run_replays_chained_pr_bodies_in_order(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add(
                "pr-body-changed",
                pr="https://github.com/sample-space/sample-app/pull/10",
                before="A",
                after="B",
            )
            current.add(
                "pr-body-changed",
                pr="https://github.com/sample-space/sample-app/pull/10",
                before="B",
                after="C",
            )
            current.data["operations"][1]["pr"] += "#issuecomment-123"
            current.save()
            responses = restore_preflight_responses(issue_read=False) + [{"body": "C"}]
            output = io.StringIO()
            runner = FakeRunner(responses, dry_run=True)
            with contextlib.redirect_stdout(output):
                result = work.command_restore(
                    Namespace(receipt=path),
                    runner,
                    current,
                )
            self.assertEqual(result, 0)
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["mutated_operations"], 2)
            self.assertEqual(payload["reason"], "restored")
            self.assertFalse(any(
                "issues?per_page=1" in " ".join(call[0])
                for call in runner.calls
            ))

    def test_restore_marks_operations_and_second_run_is_noop(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add("label-created", repo="sample-space/sample-app", name="type:task")
            first_responses = restore_preflight_responses() + [[{"name": "type:task"}], [], [], work.CommandResult()]
            first = FakeRunner(first_responses)
            with contextlib.redirect_stdout(io.StringIO()):
                work.command_restore(Namespace(receipt=path), first, current)
            reloaded = receipt(path)
            self.assertEqual(reloaded.data["operations"][0]["status"], "restored")
            second = FakeRunner([])
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                work.command_restore(Namespace(receipt=path), second, reloaded)
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["restored_operations"], 0)
            self.assertEqual(payload["reason"], "already_restored")
            self.assertEqual(second.calls, [])

    def test_restore_reapplies_reversibly_removed_issue_label(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add(
                "issue-label-removed",
                issue="sample-space/sample-app#4",
                name="needs-owner",
            )
            responses = restore_preflight_responses() + [
                {"labels": [], "assignees": []},
                work.CommandResult(),
            ]
            runner = FakeRunner(responses)
            with contextlib.redirect_stdout(io.StringIO()):
                work.command_restore(Namespace(receipt=path), runner, current)
            self.assertIn(
                [
                    "issue", "edit", "https://github.com/sample-space/sample-app/issues/4",
                    "--add-label", "needs-owner",
                ],
                [call[0] for call in runner.calls],
            )

    def test_restore_rejects_unrecognized_blocked_by_rest_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add(
                "relationship-added",
                source="sample-space/sample-app#9",
                target="sample-space/sample-app#12",
                relation="blocked-by",
            )
            responses = restore_preflight_responses() + [
                [[{"number": 12, "state": "OPEN"}]],
            ]
            with self.assertRaisesRegex(work.WorkError, "blocked-by response lacks html_url"):
                work.command_restore(
                    Namespace(receipt=path), FakeRunner(responses), current,
                )

    def test_restore_names_unparseable_relationship_rest_url(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add(
                "relationship-added",
                source="sample-space/sample-app#9",
                target="sample-space/sample-app#12",
                relation="blocked-by",
            )
            responses = restore_preflight_responses() + [
                [[{"html_url": "https://github.com/sample-space/sample-app/pull/7"}]],
            ]
            with self.assertRaisesRegex(
                work.WorkError, "blocked-by response contains an invalid issue URL"
            ):
                work.command_restore(
                    Namespace(receipt=path), FakeRunner(responses), current,
                )

    def test_restore_reconciles_source_deleted_during_relationship_read(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add(
                "relationship-added",
                source="sample-space/sample-app#9",
                target="sample-space/sample-app#12",
                relation="blocked-by",
            )
            responses = restore_preflight_responses() + [
                work.CommandResult(returncode=1, stderr="Not Found (HTTP 404)"),
                work.CommandResult(returncode=1, stderr="issue view failed"),
                work.CommandResult(returncode=1, stderr="Not Found (HTTP 404)"),
            ]
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = work.command_restore(
                    Namespace(receipt=path), FakeRunner(responses), current,
                )
            self.assertEqual(result, 0)
            self.assertEqual(json.loads(output.getvalue())["reason"], "missing_issues")
            self.assertTrue(current.data["operations"][0]["restore_missing"])

    def test_restore_flattens_paginated_relationship_pages(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add(
                "relationship-added",
                source="sample-space/sample-app#9",
                target="sample-space/sample-app#12",
                relation="sub-issue",
            )
            responses = restore_preflight_responses() + [
                [
                    [{"html_url": "https://github.com/sample-space/sample-app/issues/11"}],
                    [{"html_url": "https://github.com/sample-space/sample-app/issues/12"}],
                ],
                work.CommandResult(),
            ]
            runner = FakeRunner(responses)
            with contextlib.redirect_stdout(io.StringIO()):
                result = work.command_restore(Namespace(receipt=path), runner, current)
            self.assertEqual(result, 0)
            self.assertTrue(any("--slurp" in call[0] for call in runner.calls))
            self.assertTrue(any("--remove-sub-issue" in call[0] for call in runner.calls))

    def test_restore_rejects_unverified_flag_on_non_relationship_operation(self):
        current = receipt()
        current.add("label-created", repo="sample-space/sample-app", name="type:task")
        current.mark_restored(current.data["operations"][0], mutated=False)
        current.data["operations"][0]["restore_unverified"] = True
        with self.assertRaisesRegex(work.WorkError, "only valid for relationship"):
            current.validate()

    def test_restore_skips_blocked_repo_and_compensates_healthy_repo(self):
        current = receipt()
        current.add("issue-created", issue="sample-space/blocked#1")
        current.add("issue-created", issue="sample-space/healthy#2")
        responses = [
            work.CommandResult(stdout="gh version 2.96.0\n"),
            work.CommandResult(),
            work.CommandResult(),
            work.CommandResult(returncode=1, stderr="Forbidden (HTTP 403)"),
            work.CommandResult(),
            work.CommandResult(stdout="[]"),
            {"state": "CLOSED", "labels": [], "assignees": []},
        ]
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = work.command_restore(Namespace(receipt="unused"), FakeRunner(responses), current)
        self.assertEqual(result, 3)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["blocked_repositories"][0]["repo"], "sample-space/blocked")
        self.assertEqual(current.data["operations"][0]["status"], "active")
        self.assertEqual(current.data["operations"][1]["status"], "restored")

    def test_relationship_issue_preflight_includes_source_and_target_repositories(self):
        current = receipt()
        current.add(
            "relationship-added",
            relation="sub-issue",
            source="sample-space/source#1",
            target="other-space/target#2",
        )
        self.assertEqual(
            work.receipt_issue_repositories(current),
            {"sample-space/source", "other-space/target"},
        )

    def test_relationship_operation_includes_source_and_target_repositories(self):
        operation = {
            "kind": "relationship-added",
            "source": "sample-space/source#1",
            "target": "other-space/target#2",
        }
        self.assertEqual(
            work.operation_repositories(operation),
            {"sample-space/source", "other-space/target"},
        )

    def test_restore_skips_blocked_pr_repo_and_compensates_healthy_repo(self):
        current = receipt()
        current.add(
            "pr-body-changed",
            pr="https://github.com/sample-space/blocked/pull/1",
            before="Before",
            after="After",
        )
        current.add("issue-created", issue="sample-space/healthy#2")
        responses = [
            work.CommandResult(stdout="gh version 2.96.0\n"),
            work.CommandResult(),
            work.CommandResult(returncode=1, stderr="Not Found (HTTP 404)"),
            work.CommandResult(),
            work.CommandResult(stdout="[]"),
            {"state": "CLOSED", "labels": [], "assignees": []},
        ]
        output = io.StringIO()
        runner = FakeRunner(responses)
        with contextlib.redirect_stdout(output):
            result = work.command_restore(Namespace(receipt="unused"), runner, current)
        self.assertEqual(result, 3)
        self.assertEqual(current.data["operations"][0]["status"], "active")
        self.assertEqual(current.data["operations"][1]["status"], "restored")
        self.assertFalse(any(call[0][:2] == ["pr", "view"] for call in runner.calls))

    def test_restore_requires_issue_read_access_before_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add("issue-created", issue="sample-space/sample-app#4")
            responses = [
                work.CommandResult(stdout="gh version 2.96.0\n"),
                work.CommandResult(),
                work.CommandResult(),
                work.CommandResult(returncode=1, stderr="Not Found (HTTP 404)"),
            ]
            runner = FakeRunner(responses)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = work.command_restore(Namespace(receipt=path), runner, current)
            self.assertEqual(result, 3)
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["reason"], "blocked_repositories")
            self.assertEqual(payload["blocked_repositories"][0]["repo"], "sample-space/sample-app")
            self.assertFalse(any(call[0][:2] == ["issue", "close"] for call in runner.calls))
            self.assertEqual(current.data["operations"][0]["status"], "active")

    def test_restore_falls_back_to_mutation_when_rest_endpoint_is_unavailable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add(
                "relationship-added",
                source="sample-space/sample-app#9",
                target="sample-space/sample-app#12",
                relation="blocked-by",
            )
            responses = restore_preflight_responses() + [
                work.CommandResult(returncode=1, stderr="Not Found (HTTP 404)"),
                {"blockedBy": []},
                work.CommandResult(),
            ]
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = work.command_restore(Namespace(receipt=path), FakeRunner(responses), current)
            self.assertEqual(result, 0)
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["mutated_operations"], 0)
            self.assertEqual(payload["reason"], "unverified_relationships")
            self.assertEqual(payload["unverified_relationship_operations"], 1)
            operation = current.data["operations"][0]
            self.assertTrue(operation["restore_unverified"])
            self.assertTrue(operation["restore_fallback_succeeded"])
            self.assertIn("endpoint unavailable", operation["restore_probe_error"])
            self.assertEqual(payload["unverified_relationships"], [{
                "fallback_succeeded": True,
                "probe_error": operation["restore_probe_error"],
                "relation": "blocked-by",
                "source": "https://github.com/sample-space/sample-app/issues/9",
                "target": "https://github.com/sample-space/sample-app/issues/12",
            }])
            second_output = io.StringIO()
            with contextlib.redirect_stdout(second_output):
                second_result = work.command_restore(
                    Namespace(receipt=path), FakeRunner(), current,
                )
            self.assertEqual(second_result, 0)
            second_payload = json.loads(second_output.getvalue())
            self.assertEqual(second_payload["reason"], "already_restored")
            self.assertEqual(second_payload["unverified_relationship_operations"], 0)
            self.assertEqual(second_payload["standing_unverified_operations"], 1)
            self.assertEqual(second_payload["unverified_relationships"], payload["unverified_relationships"])

    def test_receipt_repositories_excludes_completed_repositories(self):
        current = receipt()
        current.add("issue-created", issue="sample-space/completed#1")
        current.add("issue-created", issue="sample-space/active#2")
        current.mark_restored(current.data["operations"][0], mutated=False)
        self.assertEqual(work.receipt_repositories(current), {"sample-space/active"})

    def test_restore_records_benign_unverified_fallback_failure(self):
        current = receipt()
        current.add(
            "relationship-added",
            source="sample-space/sample-app#9",
            target="sample-space/sample-app#12",
            relation="blocked-by",
        )
        responses = restore_preflight_responses() + [
            work.CommandResult(returncode=1, stderr="Not Found (HTTP 404)"),
            {"blockedBy": []},
            work.CommandResult(returncode=1, stderr="no blocked-by relationship"),
        ]
        with contextlib.redirect_stdout(io.StringIO()):
            result = work.command_restore(Namespace(receipt="unused"), FakeRunner(responses), current)
        self.assertEqual(result, 0)
        self.assertFalse(current.data["operations"][0]["restore_fallback_succeeded"])

    def test_restore_dry_fallback_reports_unverified_without_claiming_mutation(self):
        current = receipt()
        current.add(
            "relationship-added",
            source="sample-space/sample-app#9",
            target="sample-space/sample-app#12",
            relation="blocked-by",
        )
        responses = restore_preflight_responses() + [
            work.CommandResult(returncode=1, stderr="Not Found (HTTP 404)"),
            {"blockedBy": []},
        ]
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = work.command_restore(
                Namespace(receipt="unused"), FakeRunner(responses, dry_run=True), current,
            )
        self.assertEqual(result, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["mutated_operations"], 0)
        self.assertEqual(payload["unverified_relationship_operations"], 1)
        self.assertIsNone(payload["unverified_relationships"][0]["fallback_succeeded"])

    def test_restore_terminally_records_unknown_unverified_fallback_failure(self):
        current = receipt()
        current.add(
            "relationship-added",
            source="sample-space/sample-app#9",
            target="sample-space/sample-app#12",
            relation="blocked-by",
        )
        responses = restore_preflight_responses() + [
            work.CommandResult(returncode=1, stderr="Not Found (HTTP 404)"),
            {"state": "OPEN"},
            work.CommandResult(returncode=1, stderr="unexpected dependency failure"),
        ]
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = work.command_restore(Namespace(receipt="unused"), FakeRunner(responses), current)
        self.assertEqual(result, 0)
        details = json.loads(output.getvalue())["unverified_relationships"][0]
        self.assertFalse(details["fallback_succeeded"])
        self.assertIn("fallback mutation failed", details["probe_error"])
        self.assertEqual(current.data["operations"][0]["status"], "restored")

    def test_restore_skips_exactly_absent_sub_issue_without_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add(
                "relationship-added",
                source="sample-space/sample-app#9",
                target="sample-space/sample-app#12",
                relation="sub-issue",
            )
            responses = restore_preflight_responses() + [
                [[{"html_url": "https://github.com/sample-space/sample-app/issues/13"}]],
            ]
            runner = FakeRunner(responses)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = work.command_restore(Namespace(receipt=path), runner, current)
            self.assertEqual(result, 0)
            self.assertEqual(json.loads(output.getvalue())["mutated_operations"], 0)
            self.assertFalse(any("--remove-sub-issue" in call[0] for call in runner.calls))

    def test_restore_terminally_reconciles_deleted_issue_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add("issue-created", issue="sample-space/sample-app#4")
            responses = restore_preflight_responses() + [
                work.CommandResult(returncode=1, stderr="issue view failed"),
                work.CommandResult(returncode=1, stderr="gh: Not Found (HTTP 404)"),
            ]
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = work.command_restore(Namespace(receipt=path), FakeRunner(responses), current)
            self.assertEqual(result, 0)
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["reason"], "missing_issues")
            self.assertEqual(payload["missing_issue_operations"], 1)
            operation = current.data["operations"][0]
            self.assertEqual(operation["status"], "restored")
            self.assertTrue(operation["restore_missing"])

    def test_restore_preserves_issue_probe_failure_diagnostics(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add("issue-created", issue="sample-space/sample-app#4")
            responses = restore_preflight_responses() + [
                work.CommandResult(returncode=1, stderr="GraphQL rate limited"),
                work.CommandResult(returncode=1, stderr="HTTP 429 secondary rate limit"),
            ]
            with self.assertRaisesRegex(
                work.WorkError, "cannot verify referenced issue.*HTTP 429 secondary rate limit"
            ):
                work.command_restore(
                    Namespace(receipt=path), FakeRunner(responses), current,
                )

    def test_restore_does_not_tolerate_non_relationship_missing_resource(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add(
                "relationship-added",
                source="sample-space/sample-app#9",
                target="sample-space/sample-app#12",
                relation="sub-issue",
            )
            responses = restore_preflight_responses() + [
                [[{"html_url": "https://github.com/sample-space/sample-app/issues/12"}]],
                work.CommandResult(returncode=1, stderr="source issue not found"),
            ]
            with self.assertRaisesRegex(work.WorkError, "relationship restore failed"):
                work.command_restore(
                    Namespace(receipt=path), FakeRunner(responses), current,
                )

    def test_restore_requires_reenabled_issues_before_label_usage_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add("label-created", repo="sample-space/sample-app", name="type:task")
            responses = [
                work.CommandResult(stdout="gh version 2.96.0\n"),
                work.CommandResult(),
                work.CommandResult(),
                work.CommandResult(returncode=1, stderr="Gone (HTTP 410)"),
                {"name": "type:task"},
                [],
                work.CommandResult(),
            ]
            runner = FakeRunner(responses)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = work.command_restore(Namespace(receipt=path), runner, current)
            self.assertEqual(result, 3)
            self.assertEqual(json.loads(output.getvalue())["reason"], "blocked_repositories")
            self.assertEqual(current.data["operations"][0]["status"], "active")
            self.assertFalse(any(call[0][:2] == ["label", "delete"] for call in runner.calls))

    def test_restore_treats_exact_label_http_404_as_already_deleted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add("label-created", repo="sample-space/sample-app", name="type:task")
            responses = restore_preflight_responses() + [
                work.CommandResult(returncode=1, stderr="gh: Not Found (HTTP 404)"),
            ]
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = work.command_restore(
                    Namespace(receipt=path), FakeRunner(responses), current,
                )
            self.assertEqual(result, 0)
            self.assertEqual(json.loads(output.getvalue())["reason"], "restored")
            self.assertEqual(current.data["operations"][0]["status"], "restored")

    def test_restore_uses_exact_label_lookup_before_definition_delete(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add("label-created", repo="sample-space/sample-app", name="type:task")
            responses = restore_preflight_responses() + [
                work.CommandResult(stdout='{"name":"type:task"}'),
                [],
                [],
                work.CommandResult(),
            ]
            runner = FakeRunner(responses)
            with contextlib.redirect_stdout(io.StringIO()):
                work.command_restore(Namespace(receipt=path), runner, current)
            self.assertIn(
                ["api", "repos/sample-space/sample-app/labels/type%3Atask"],
                [call[0] for call in runner.calls],
            )

    def test_restore_mixed_label_lifecycle_converges_in_real_and_dry_runs(self):
        def make_receipt(path):
            current = receipt(path)
            current.add("label-created", repo="sample-space/sample-app", name="needs-owner")
            current.add(
                "issue-label-added",
                issue="sample-space/sample-app#5",
                name="needs-owner",
            )
            current.add(
                "issue-label-removed",
                issue="sample-space/sample-app#7",
                name="needs-owner",
            )
            return current

        with tempfile.TemporaryDirectory() as directory:
            real = make_receipt(str(Path(directory) / "real.json"))
            real_responses = restore_preflight_responses() + [
                {"labels": [], "assignees": []},
                work.CommandResult(),
                {"labels": [{"name": "needs-owner"}], "assignees": []},
                work.CommandResult(),
                [{"name": "needs-owner"}],
                [{"url": "https://github.com/sample-space/sample-app/issues/7"}],
                [],
            ]
            real_output = io.StringIO()
            with contextlib.redirect_stdout(real_output):
                result = work.command_restore(
                    Namespace(receipt=str(real.path)),
                    FakeRunner(real_responses),
                    real,
                )
            self.assertEqual(result, 0)
            real_payload = json.loads(real_output.getvalue())
            self.assertEqual(real_payload["skipped_labels_in_use"], 0)
            self.assertEqual(real_payload["retained_label_definitions"], 1)
            self.assertEqual(real_payload["reason"], "retained_labels")
            self.assertEqual(real_payload["mutated_operations"], 2)
            self.assertTrue(all(op["status"] == "restored" for op in real.data["operations"]))

            dry = make_receipt(str(Path(directory) / "dry.json"))
            dry_responses = restore_preflight_responses() + [
                {"labels": [], "assignees": []},
                {"labels": [{"name": "needs-owner"}], "assignees": []},
                [{"name": "needs-owner"}],
                [],
                [],
            ]
            dry_output = io.StringIO()
            with contextlib.redirect_stdout(dry_output):
                result = work.command_restore(
                    Namespace(receipt=str(dry.path)),
                    FakeRunner(dry_responses, dry_run=True),
                    dry,
                )
            self.assertEqual(result, 0)
            dry_payload = json.loads(dry_output.getvalue())
            self.assertEqual(dry_payload["skipped_labels_in_use"], 0)
            self.assertEqual(dry_payload["retained_label_definitions"], 1)
            self.assertEqual(dry_payload["reason"], "retained_labels")
            self.assertEqual(dry_payload["mutated_operations"], 2)

    def test_restore_dry_run_replays_interleaved_label_operations_in_order(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add("label-created", repo="sample-space/sample-app", name="needs-owner")
            current.add(
                "issue-label-removed", issue="sample-space/sample-app#7", name="needs-owner",
            )
            current.add(
                "issue-label-added", issue="sample-space/sample-app#7", name="needs-owner",
            )
            responses = restore_preflight_responses() + [
                {"labels": [{"name": "needs-owner"}], "assignees": []},
                {"labels": [{"name": "needs-owner"}], "assignees": []},
                [{"name": "needs-owner"}],
                [{"url": "https://github.com/sample-space/sample-app/issues/7"}],
                [],
            ]
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = work.command_restore(
                    Namespace(receipt=path),
                    FakeRunner(responses, dry_run=True),
                    current,
                )
            self.assertEqual(result, 0)
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["reason"], "retained_labels")
            self.assertEqual(payload["retained_label_definitions"], 1)
            self.assertEqual(payload["mutated_operations"], 2)

    def test_restore_deletes_unused_definition_after_same_issue_lifecycle(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add("label-created", repo="sample-space/sample-app", name="needs-owner")
            current.add(
                "issue-label-added", issue="sample-space/sample-app#4", name="needs-owner",
            )
            current.add(
                "issue-label-removed", issue="sample-space/sample-app#4", name="needs-owner",
            )
            responses = restore_preflight_responses() + [
                {"labels": [], "assignees": []},
                work.CommandResult(),
                {"labels": [{"name": "needs-owner"}], "assignees": []},
                work.CommandResult(),
                [{"name": "needs-owner"}],
                [],
                [],
                work.CommandResult(),
            ]
            runner = FakeRunner(responses)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = work.command_restore(Namespace(receipt=path), runner, current)
            self.assertEqual(result, 0)
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["reason"], "restored")
            self.assertEqual(payload["retained_label_definitions"], 0)
            self.assertIn(
                ["label", "delete", "needs-owner", "--repo", "sample-space/sample-app", "--yes"],
                [call[0] for call in runner.calls],
            )

    def test_restore_retry_retains_definition_for_already_reapplied_label(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add("label-created", repo="sample-space/sample-app", name="needs-owner")
            current.add(
                "issue-label-removed", issue="sample-space/sample-app#7", name="needs-owner",
            )
            current.mark_restored(current.data["operations"][1], mutated=True)
            responses = restore_preflight_responses() + [
                [{"name": "needs-owner"}],
                [{"url": "https://github.com/sample-space/sample-app/issues/7"}],
                [],
            ]
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = work.command_restore(
                    Namespace(receipt=path), FakeRunner(responses), current,
                )
            self.assertEqual(result, 0)
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["reason"], "retained_labels")
            self.assertEqual(payload["retained_label_definitions"], 1)

    def test_restore_tolerates_missing_definition_for_removed_label(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add(
                "issue-label-removed",
                issue="sample-space/sample-app#4",
                name="needs-owner",
            )
            responses = restore_preflight_responses() + [
                {"labels": [], "assignees": []},
                work.CommandResult(returncode=1, stderr="label not found"),
            ]
            with contextlib.redirect_stdout(io.StringIO()):
                result = work.command_restore(
                    Namespace(receipt=path),
                    FakeRunner(responses),
                    current,
                )
            self.assertEqual(result, 0)
            self.assertEqual(current.data["operations"][0]["status"], "restored")

    def test_restore_does_not_tolerate_non_label_missing_resource(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add(
                "issue-label-removed",
                issue="sample-space/sample-app#4",
                name="needs-owner",
            )
            responses = restore_preflight_responses() + [
                {"labels": [], "assignees": []},
                work.CommandResult(returncode=1, stderr="issue does not exist"),
            ]
            with self.assertRaisesRegex(work.WorkError, "issue does not exist"):
                work.command_restore(
                    Namespace(receipt=path), FakeRunner(responses), current,
                )

    def test_restore_rejects_receipt_without_operations(self):
        current = receipt()
        runner = FakeRunner([])
        with self.assertRaisesRegex(work.WorkError, "receipt not found"):
            work.command_restore(Namespace(receipt="missing"), runner, current)
        self.assertEqual(runner.calls, [])

    def test_restore_accepts_persisted_noop_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.save()
            reloaded = receipt(path)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = work.command_restore(Namespace(receipt=path), FakeRunner([]), reloaded)
            self.assertEqual(result, 0)
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["restored_operations"], 0)
            self.assertEqual(payload["reason"], "empty")

    def test_main_preflight_fails_fast_on_supplied_invalid_ownership_config(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "targets.json"
            ownership_path = root / "ownership.json"
            config_path.write_text(json.dumps(config()), encoding="utf-8")
            ownership_path.write_text('{"mappings": {}}', encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                result = work.main([
                    "--config", str(config_path),
                    "--ownership-config", str(ownership_path),
                    "preflight", "--repos", "sample-space/sample-app",
                ], runner=FakeRunner([]))
            self.assertEqual(result, 2)
            self.assertIn("mappings array", stderr.getvalue())

    def test_main_assign_distinguishes_empty_ownership_config(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "targets.json"
            config_path.write_text(json.dumps(config()), encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                result = work.main([
                    "--config", str(config_path),
                    "--ownership-config", "",
                    "assign",
                    "--issue", "sample-space/sample-app#1",
                    "--from-ownership-map",
                    "--receipt", str(Path(directory) / "receipt.json"),
                ], runner=FakeRunner([]))
            self.assertEqual(result, 2)
            self.assertIn("supplied but is empty", stderr.getvalue())

    def test_main_rejects_empty_assignee_before_loading_config(self):
        commands = [
            ["issue-create", "--repo", "sample-space/sample-app", "--type", "Task",
             "--title", "Sample", "--assignee", "", "--receipt", "receipt.json"],
            ["assign", "--issue", "sample-space/sample-app#1", "--assignee", "",
             "--receipt", "receipt.json"],
            ["work-graph", "create", "--umbrella", "sample-space/sample-app#1",
             "--repos", "all", "--assignee", "", "--receipt", "receipt.json"],
        ]
        for command in commands:
            with self.subTest(command=command):
                runner = FakeRunner([])
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    result = work.main(["--config", "missing.json", *command], runner=runner)
                self.assertEqual(result, 2)
                self.assertIn("--assignee was supplied but is empty", stderr.getvalue())
                self.assertEqual(runner.calls, [])

    def test_main_rejects_empty_receipt_for_every_receipt_command(self):
        commands = [
            ["labels", "ensure", "--repos", "all", "--receipt", ""],
            ["issue-create", "--repo", "sample-space/sample-app", "--type", "Task",
             "--title", "Sample", "--receipt", ""],
            ["pr-link", "--pr", "sample-space/sample-app#2", "--issue",
             "sample-space/sample-app#1", "--mode", "refs", "--receipt", ""],
            ["assign", "--issue", "sample-space/sample-app#1", "--assignee",
             "sample-user", "--receipt", ""],
            ["work-graph", "create", "--umbrella", "sample-space/sample-app#1",
             "--repos", "all", "--receipt", ""],
            ["restore", "--receipt", ""],
        ]
        for command in commands:
            with self.subTest(command=command):
                runner = FakeRunner([])
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    result = work.main(["--config", "missing.json", *command], runner=runner)
                self.assertEqual(result, 2)
                self.assertIn("--receipt was supplied but is empty", stderr.getvalue())
                self.assertEqual(runner.calls, [])

    def test_main_rejects_empty_optional_issue_strings(self):
        for option in ("--parent", "--blocking", "--body-file"):
            with self.subTest(option=option):
                runner = FakeRunner([])
                stderr = io.StringIO()
                command = [
                    "--config", "missing.json",
                    "issue-create", "--repo", "sample-space/sample-app", "--type", "Task",
                    "--title", "Sample", option, "", "--receipt", "receipt.json",
                ]
                with contextlib.redirect_stderr(stderr):
                    result = work.main(command, runner=runner)
                self.assertEqual(result, 2)
                self.assertIn("was supplied but is empty", stderr.getvalue())
                self.assertEqual(runner.calls, [])

    def test_receipt_requires_explicit_validated_transient_mode(self):
        with self.assertRaisesRegex(work.WorkError, "receipt path was supplied but is empty"):
            work.Receipt("", source_sha=SOURCE, config_digest=DIGEST)
        with self.assertRaisesRegex(work.WorkError, "receipt path is required"):
            work.Receipt(None, source_sha=SOURCE, config_digest=DIGEST)
        current = work.Receipt(
            None,
            source_sha=SOURCE,
            config_digest=DIGEST,
            transient=True,
        )
        current.data["operations"].append({"kind": "invalid"})
        with self.assertRaisesRegex(work.WorkError, "unsupported receipt operation"):
            current.save()

    def test_standard_check_ignores_empty_config_arguments(self):
        runner = FakeRunner([])
        with mock.patch.object(work, "command_standard_check", return_value=0) as command:
            result = work.main([
                "--config", "",
                "--ownership-config", "",
                "standard-check",
            ], runner=runner)
        self.assertEqual(result, 0)
        command.assert_called_once()
        self.assertEqual(runner.calls, [])

    def test_main_rejects_empty_config_ownership_and_title_before_external_work(self):
        commands = [
            ["--config", "", "labels", "ensure", "--repos", "all",
             "--receipt", "receipt.json"],
            ["--config", "missing.json", "--ownership-config", "", "issue-create",
             "--repo", "sample-space/sample-app", "--type", "Task", "--title", "Sample",
             "--receipt", "receipt.json"],
            ["--config", "missing.json", "issue-create", "--repo",
             "sample-space/sample-app", "--type", "Task", "--title", "",
             "--receipt", "receipt.json"],
        ]
        for command in commands:
            with self.subTest(command=command):
                runner = FakeRunner([])
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    result = work.main(command, runner=runner)
                self.assertEqual(result, 2)
                self.assertIn("was supplied but is empty", stderr.getvalue())
                self.assertEqual(runner.calls, [])

    def test_main_assign_from_ownership_map_uses_loaded_config(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "targets.json"
            ownership_path = root / "ownership.json"
            config_path.write_text(json.dumps(config()), encoding="utf-8")
            ownership_path.write_text(json.dumps({
                "mappings": [{
                    "repo": "sample-space/sample-app",
                    "area": "web",
                    "logins": ["sample-user"],
                }],
            }), encoding="utf-8")
            responses = managed_preflight_responses() + [
                {"labels": [], "assignees": []},
                work.CommandResult(),
            ]
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = work.main([
                    "--config", str(config_path),
                    "--ownership-config", str(ownership_path),
                    "--dry-run",
                    "assign",
                    "--issue", "sample-space/sample-app#1",
                    "--from-ownership-map",
                    "--area", "web",
                    "--receipt", str(root / "receipt.json"),
                ], runner=FakeRunner(responses))
            self.assertEqual(result, 0)
            payload = json.loads(output.getvalue())
            self.assertTrue(payload["assigned"])
            self.assertEqual(payload["assignee"], "sample-user")
            self.assertEqual(payload["ownership_source"], "exact")

    def test_main_persists_receipt_for_successful_noop_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "targets.json"
            receipt_path = root / "noop-receipt.json"
            config_path.write_text(json.dumps(config()), encoding="utf-8")
            runner = FakeRunner(managed_preflight_responses())
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = work.main([
                    "--config", str(config_path),
                    "labels", "ensure",
                    "--repos", "sample-space/sample-app",
                    "--receipt", str(receipt_path),
                ], runner=runner)
            self.assertEqual(result, 0)
            self.assertTrue(receipt_path.exists())
            self.assertEqual(json.loads(receipt_path.read_text(encoding="utf-8"))["operations"], [])

    def test_partial_managed_label_restore_can_retry_after_reference_removal(self):
        current = receipt()
        for name in ("type:bug", "type:feature", "type:task"):
            current.add("label-created", repo="sample-space/sample-app", name=name)
        first_responses = restore_preflight_responses() + [
            PAGED_ALL_LABELS,
            [{"url": "https://github.com/sample-space/sample-app/issues/9"}],
            [],
            PAGED_ALL_LABELS,
            [],
            [],
            work.CommandResult(),
            PAGED_ALL_LABELS,
            [],
            [],
            work.CommandResult(),
        ]
        with contextlib.redirect_stdout(io.StringIO()):
            first_result = work.command_restore(
                Namespace(receipt="unused"), FakeRunner(first_responses), current
            )
        self.assertEqual(first_result, 3)
        self.assertEqual(
            [operation["status"] for operation in current.data["operations"]],
            ["restored", "restored", "active"],
        )
        second_responses = restore_preflight_responses() + [
            [{"name": "type:task"}],
            [],
            [],
            work.CommandResult(),
        ]
        with contextlib.redirect_stdout(io.StringIO()):
            second_result = work.command_restore(
                Namespace(receipt="unused"), FakeRunner(second_responses), current
            )
        self.assertEqual(second_result, 0)
        self.assertTrue(all(operation["status"] == "restored" for operation in current.data["operations"]))

    def test_label_restore_skips_labels_that_are_in_use(self):
        current = receipt()
        current.add("label-created", repo="sample-space/sample-app", name="type:task")
        responses = restore_preflight_responses() + [
            [{"name": "type:task"}],
            [{"url": "https://github.com/sample-space/sample-app/issues/9"}],
            [],
        ]
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = work.command_restore(Namespace(receipt="unused"), FakeRunner(responses), current)
        self.assertEqual(result, 3)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["skipped_labels_in_use"], 1)
        self.assertEqual(payload["reason"], "labels_in_use")
        self.assertEqual(current.data["operations"][0]["status"], "active")

    def test_restore_dry_run_simulates_pending_issue_label_removal(self):
        current = receipt()
        issue = "https://github.com/sample-space/sample-app/issues/9"
        current.add("label-created", repo="sample-space/sample-app", name="needs-owner")
        current.add("issue-label-added", issue=issue + "#issuecomment-123", name="needs-owner")
        self.assertEqual(current.data["operations"][1]["issue"], issue)
        responses = restore_preflight_responses() + [
            {"labels": [{"name": "needs-owner"}], "assignees": []},
            [{"name": "needs-owner"}],
            [{"url": issue}],
            [],
        ]
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = work.command_restore(
                Namespace(receipt="unused"), FakeRunner(responses, dry_run=True), current
            )
        payload = json.loads(output.getvalue())
        self.assertEqual(result, 0)
        self.assertEqual(payload["restored_operations"], 2)
        self.assertEqual(payload["mutated_operations"], 2)
        self.assertEqual(payload["reason"], "restored")
        self.assertEqual(payload["skipped_labels_in_use"], 0)
        self.assertTrue(all(operation["status"] == "active" for operation in current.data["operations"]))

    def test_restore_counts_verified_noop_operation_as_restored_not_mutated(self):
        current = receipt()
        current.add(
            "issue-label-added",
            issue="https://github.com/sample-space/sample-app/issues/9",
            name="needs-owner",
        )
        responses = restore_preflight_responses() + [{"labels": [], "assignees": []}]
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = work.command_restore(
                Namespace(receipt="unused"), FakeRunner(responses), current
            )
        payload = json.loads(output.getvalue())
        self.assertEqual(result, 0)
        self.assertEqual(payload["restored_operations"], 1)
        self.assertEqual(payload["mutated_operations"], 0)
        self.assertEqual(payload["reason"], "restored")
        self.assertEqual(payload["total_operations"], 1)

    def test_relationship_restore_fails_on_unknown_error(self):
        current = receipt()
        current.add("relationship-added", relation="sub-issue", source="sample-space/sample-app#1", target="sample-space/sample-app#2")
        responses = restore_preflight_responses() + [
            [[{"html_url": "https://github.com/sample-space/sample-app/issues/2"}]],
            work.CommandResult(returncode=1, stderr="permission denied"),
        ]
        with self.assertRaises(work.WorkError):
            work.command_restore(Namespace(receipt="unused"), FakeRunner(responses), current)

    def test_skill_body_is_greedily_wrapped_at_documented_width(self):
        lines = (ROOT / "SKILL.body.md").read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            [],
            [(index, len(line)) for index, line in enumerate(lines, 1) if len(line) > 100],
        )
        underfilled: list[int] = []
        paragraph: list[tuple[int, str]] = []
        in_code = False
        in_frontmatter = False

        def flush() -> None:
            for (line_number, line), (_, following) in zip(paragraph, paragraph[1:]):
                next_word = following.split()[0]
                if len(line) + 1 + len(next_word) <= 100:
                    underfilled.append(line_number)
            paragraph.clear()

        for index, line in enumerate(lines, 1):
            if index == 1 and line == "---":
                in_frontmatter = True
                continue
            if in_frontmatter:
                if line == "---":
                    in_frontmatter = False
                continue
            if line.startswith("```"):
                flush()
                in_code = not in_code
                continue
            if in_code or not line or line.startswith(("#", "<!--")):
                flush()
                continue
            paragraph.append((index, line))
        flush()
        self.assertEqual([], underfilled)

    def test_standard_check_requires_matching_provenance_and_content(self):
        helper_source = "#!/usr/bin/env python3\nprint('sample')\n"
        helper_digest = hashlib.sha256(helper_source.encode()).hexdigest()
        helper_marker = (
            "# github-work-standard: version=1.0.0 source=" + SOURCE + " target=" + DIGEST
            + " content=" + helper_digest + "\n"
        )
        helper_text = "#!/usr/bin/env python3\n" + helper_marker + "print('sample')\n"
        managed_source = "<!-- BEGIN github-work-standard -->\nmanaged content\n<!-- END github-work-standard -->"
        managed_digest = hashlib.sha256(managed_source.encode()).hexdigest()
        managed_marker = (
            "<!-- github-work-standard: version=1.0.0 source=" + SOURCE + " target=" + DIGEST
            + " content=" + managed_digest + " -->"
        )
        managed_text = managed_source.replace(
            "<!-- BEGIN github-work-standard -->",
            "<!-- BEGIN github-work-standard -->\n" + managed_marker,
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            helper = root / "github_work.py"
            agents = root / "AGENTS.md"
            skill = root / "SKILL.md"
            pr_template = root / "pull_request_template.md"
            workflow = root / "github-work-standard.yml"
            gitignore = root / ".gitignore"
            prettierignore = root / ".prettierignore"
            issue_forms = [root / name for name in ("bug.yml", "feature.yml", "task.yml")]
            helper.write_text(helper_text)
            agents.write_text("x" * 12000 + "\n" + managed_text)
            skill.write_text(managed_text)
            pr_template.write_text(managed_text)
            workflow_source = "name: GitHub work standard\n"
            workflow_digest = hashlib.sha256(workflow_source.encode()).hexdigest()
            workflow.write_text(
                "# github-work-standard: version=1.0.0 source="
                + SOURCE
                + " target="
                + DIGEST
                + " content="
                + workflow_digest
                + "\n"
                + workflow_source
            )
            gitignore.write_text(
                "# BEGIN github-work-standard\n"
                ".github-work/\n*github-work-targets*\n*github-work-ownership*\n"
                "*.github-work-receipt.json*\n*github-work-recovery*.json*\n"
                "# END github-work-standard\n"
            )
            prettierignore.write_text(
                "# BEGIN github-work-standard\n"
                ".github/ISSUE_TEMPLATE/bug.yml\n"
                ".github/ISSUE_TEMPLATE/feature.yml\n"
                ".github/ISSUE_TEMPLATE/task.yml\n"
                ".github/pull_request_template.md\n"
                ".github/PULL_REQUEST_TEMPLATE.md\n"
                ".github/workflows/github-work-standard.yml\n"
                "scripts/github_work.py\n"
                "# END github-work-standard\n"
            )
            for form in issue_forms:
                form.write_text(managed_text)
            args = Namespace(
                agents_path=str(agents), skill_path=str(skill), pr_template_path=str(pr_template),
                workflow_path=str(workflow), gitignore_path=str(gitignore),
                prettierignore_path=str(prettierignore),
                issue_form_path=[str(path) for path in issue_forms], expected_version=None,
                expected_source_sha=None, expected_target_digest=None,
            )
            with mock.patch.object(work, "__file__", str(helper)), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(work.command_standard_check(args), 0)
            skill.write_text(skill.read_text().replace(
                "managed content",
                "# github-work-standard: version=fake source=fake target=fake content=fake\nmanaged content",
            ))
            with mock.patch.object(work, "__file__", str(helper)), self.assertRaises(work.WorkError):
                work.command_standard_check(args)
            skill.write_text(managed_text.replace("managed content", "changed content"))
            with mock.patch.object(work, "__file__", str(helper)), self.assertRaises(work.WorkError):
                work.command_standard_check(args)
            skill.write_text(managed_text)
            gitignore.write_text(gitignore.read_text().replace("*github-work-ownership*\n", ""))
            with mock.patch.object(work, "__file__", str(helper)), self.assertRaises(work.WorkError):
                work.command_standard_check(args)


if __name__ == "__main__":
    unittest.main()
