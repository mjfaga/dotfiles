from __future__ import annotations

import contextlib
import importlib.util
import io
import hashlib
import json
import os
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
    return work.Receipt(path, source_sha=SOURCE, config_digest=DIGEST)


def managed_preflight_responses(*, labels=None):
    return [
        work.CommandResult(stdout="gh version 2.96.0\n"),
        work.CommandResult(),
        work.CommandResult(),
        labels if labels is not None else ALL_LABELS,
    ]


def restore_preflight_responses():
    return [
        work.CommandResult(stdout="gh version 2.96.0\n"),
        work.CommandResult(),
        work.CommandResult(),
    ]


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

    def test_parse_issue_url_rejects_invalid(self):
        with self.assertRaises(work.WorkError):
            work.parse_issue_url("#42")

    def test_refs_demotes_all_closing_variants(self):
        body = (
            "Closes #3\n"
            "- FIXED sample-space/sample-app#3 after validation\n"
            "resolves sample-space/sample-app#3\n"
            "Closed https://github.com/sample-space/sample-app/issues/3\n"
        )
        rendered = work.linked_body(body, "sample-space/sample-app#3", "refs", "sample-space/sample-app")
        self.assertNotRegex(rendered.lower(), r"(?:closes|closed|fixed|resolves)\s+(?:#3|sample-space/sample-app#3|https://github.com/sample-space/sample-app/issues/3)")
        self.assertEqual(rendered.lower().count("refs"), 4)

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

    def test_pr_closing_link_requires_finality(self):
        responses = managed_preflight_responses() + [
            {"blockedBy": [{"state": "OPEN"}], "subIssuesSummary": {"total": 0, "completed": 0}},
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
            self.assertEqual(payload["before"], "Original body\n")
            self.assertIn("Refs sample-space/sample-app#4", payload["after"])

    def test_pr_template_placeholder_is_replaced(self):
        rendered = work.linked_body("Refs #ISSUE\n", "sample-space/sample-app#3", "refs", "sample-space/sample-app")
        self.assertEqual(rendered, "Refs sample-space/sample-app#3\n")

    def test_finality_blocks_open_relationships(self):
        result = work.finality_result({"blockedBy": [{"state": "OPEN"}], "subIssuesSummary": {"total": 2, "completed": 1}})
        self.assertEqual(result, {
            "eligible": False,
            "failure": None,
            "incomplete_sub_issues": 1,
            "open_blockers": 1,
            "reason": "not_ready",
        })

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
        for state in ({}, {"blockedBy": None, "subIssuesSummary": {}}, {"blockedBy": [], "subIssuesSummary": {"total": "0", "completed": 0}}):
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

    def test_labels_ensure_creates_only_missing_after_preflight(self):
        existing = [{"name": "type:bug", "color": "000000", "description": "preserved"}]
        runner = FakeRunner([
            work.CommandResult(stdout="gh version 2.96.0\n"), work.CommandResult(), work.CommandResult(), existing,
        ])
        current_receipt = receipt()
        args = Namespace(repos="sample-space/sample-app")
        with contextlib.redirect_stdout(io.StringIO()):
            work.command_labels_ensure(args, runner, config(), current_receipt)
        create_calls = [call for call in runner.calls if call[0][:2] == ["label", "create"]]
        self.assertEqual(len(create_calls), 2)
        self.assertEqual(len(current_receipt.data["operations"]), 2)
        self.assertNotIn("--force", create_calls[0][0])

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
        self.assertIn(["issue", "edit", "sample-space/sample-app#2", "--add-sub-issue", "https://github.com/sample-space/sample-app/issues/7"], commands)
        self.assertEqual([operation["kind"] for operation in current_receipt.data["operations"]], ["issue-created", "relationship-added"])

    def test_managed_issue_creation_records_classification_label_for_restore(self):
        responses = managed_preflight_responses() + [
            work.CommandResult(stdout="https://github.com/sample-space/sample-app/issues/7\n")
        ]
        runner = FakeRunner(responses)
        args = Namespace(
            repo="sample-space/sample-app", type="Task", title="Sample", body_file=None,
            parent=None, blocking=None, assignee=None,
        )
        current_receipt = receipt()
        with contextlib.redirect_stdout(io.StringIO()):
            work.command_issue_create(args, runner, config(), current_receipt)
        self.assertEqual(
            [operation["kind"] for operation in current_receipt.data["operations"]],
            ["issue-created", "issue-label-added"],
        )
        self.assertEqual(current_receipt.data["operations"][1]["name"], "type:task")

    def test_temporary_body_writes_utf8(self):
        with work.temporary_body("Unicode — body 🤖") as path:
            self.assertEqual(Path(path).read_text(encoding="utf-8"), "Unicode — body 🤖")

    def test_issue_create_fails_when_gh_returns_no_url(self):
        responses = managed_preflight_responses() + [work.CommandResult()]
        args = Namespace(
            repo="sample-space/sample-app", type="Task", title="Sample", body_file=None,
            parent=None, blocking=None, assignee=None,
        )
        with self.assertRaisesRegex(work.WorkError, "returned no issue URL"):
            work.command_issue_create(args, FakeRunner(responses), config(), receipt())

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
            {"partial": True, "repo": "sample-space/sample-app", "type": "Task", "url": created},
        )

    def test_issue_create_rejects_unassignable_login_before_creation(self):
        responses = managed_preflight_responses() + [work.CommandResult(returncode=1, stderr="not assignable")]
        runner = FakeRunner(responses)
        args = Namespace(repo="sample-space/sample-app", type="Task", title="Sample", body_file=None, parent=None, blocking=None, assignee="missing-user")
        with self.assertRaises(work.WorkError):
            work.command_issue_create(args, runner, config(), receipt())
        self.assertFalse(any(call[0][:2] == ["issue", "create"] for call in runner.calls))

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

    def test_pr_link_uses_body_file_and_preflight(self):
        responses = managed_preflight_responses() + [{"body": "Closes #4\n", "url": "https://github.com/sample-space/sample-app/pull/2"}, work.CommandResult()]
        runner = FakeRunner(responses)
        args = Namespace(pr="https://github.com/sample-space/sample-app/pull/2", issue="sample-space/sample-app#4", mode="refs")
        with contextlib.redirect_stdout(io.StringIO()):
            work.command_pr_link(args, runner, config(), receipt())
        edit = next(call[0] for call in runner.calls if call[0][:2] == ["pr", "edit"])
        self.assertIn("--body-file", edit)

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
                {"assignee": "sample-user", "issue": "sample-space/sample-app#4", "partial": True},
            )

    def test_work_graph_preserves_partial_receipt_on_failure(self):
        targets = config(repos=["sample-space/one-app", "sample-space/two-app"])
        responses = [work.CommandResult(stdout="gh version 2.96.0\n"), work.CommandResult()]
        for _ in range(2):
            responses.extend([work.CommandResult(), ALL_LABELS])
        runner = FakeRunner(responses)
        current_receipt = receipt()
        calls = 0

        def create(args, runner, config, receipt):
            nonlocal calls
            calls += 1
            if calls == 1:
                receipt.add("issue-created", issue="https://github.com/sample-space/one-app/issues/1")
                print(json.dumps({"repo": args.repo, "url": "https://github.com/sample-space/one-app/issues/1"}))
                return 0
            raise work.WorkError("second target failed")

        args = Namespace(repos="all", umbrella="sample-space/one-app#9", assignee=None)
        output = io.StringIO()
        with mock.patch.object(work, "command_issue_create", side_effect=create):
            with contextlib.redirect_stdout(output), self.assertRaises(work.WorkError):
                work.command_work_graph_create(args, runner, targets, current_receipt)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["created_tasks"], 1)
        self.assertEqual(payload["failed_repo"], "sample-space/two-app")
        self.assertEqual(payload["issues"][0]["url"], "https://github.com/sample-space/one-app/issues/1")
        self.assertIsNone(payload["failed_partial"])
        self.assertEqual(len(current_receipt.data["operations"]), 1)

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

    def test_restore_marks_operations_and_second_run_is_noop(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.add("label-created", repo="sample-space/sample-app", name="type:task")
            first_responses = restore_preflight_responses() + [[{"name": "type:task"}], [], [], work.CommandResult()]
            first = FakeRunner(first_responses)
            with contextlib.redirect_stdout(io.StringIO()):
                work.command_restore(Namespace(receipt=path), first, config(), current)
            reloaded = receipt(path)
            self.assertEqual(reloaded.data["operations"][0]["status"], "restored")
            second = FakeRunner([])
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                work.command_restore(Namespace(receipt=path), second, config(), reloaded)
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["restored_operations"], 0)
            self.assertEqual(payload["reason"], "already_restored")
            self.assertEqual(second.calls, [])

    def test_restore_rejects_receipt_without_operations(self):
        current = receipt()
        runner = FakeRunner([])
        with self.assertRaisesRegex(work.WorkError, "receipt not found"):
            work.command_restore(Namespace(receipt="missing"), runner, config(), current)
        self.assertEqual(runner.calls, [])

    def test_restore_accepts_persisted_noop_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "receipt.json")
            current = receipt(path)
            current.save()
            reloaded = receipt(path)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = work.command_restore(Namespace(receipt=path), FakeRunner([]), config(), reloaded)
            self.assertEqual(result, 0)
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["restored_operations"], 0)
            self.assertEqual(payload["reason"], "empty")

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
            ALL_LABELS,
            [{"url": "https://github.com/sample-space/sample-app/issues/9"}],
            [],
            ALL_LABELS,
            [],
            [],
            work.CommandResult(),
            ALL_LABELS,
            [],
            [],
            work.CommandResult(),
        ]
        with contextlib.redirect_stdout(io.StringIO()):
            first_result = work.command_restore(
                Namespace(receipt="unused"), FakeRunner(first_responses), config(), current
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
                Namespace(receipt="unused"), FakeRunner(second_responses), config(), current
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
            result = work.command_restore(Namespace(receipt="unused"), FakeRunner(responses), config(), current)
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
                Namespace(receipt="unused"), FakeRunner(responses, dry_run=True), config(), current
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
                Namespace(receipt="unused"), FakeRunner(responses), {"targets": []}, current
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
        responses = restore_preflight_responses() + [work.CommandResult(returncode=1, stderr="permission denied")]
        with self.assertRaises(work.WorkError):
            work.command_restore(Namespace(receipt="unused"), FakeRunner(responses), config(), current)

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
            issue_forms = [root / name for name in ("bug.yml", "feature.yml", "task.yml")]
            helper.write_text(helper_text)
            agents.write_text("x" * 12000 + "\n" + managed_text)
            skill.write_text(managed_text)
            pr_template.write_text(managed_text)
            for form in issue_forms:
                form.write_text(managed_text)
            args = Namespace(
                agents_path=str(agents), skill_path=str(skill), pr_template_path=str(pr_template),
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


if __name__ == "__main__":
    unittest.main()
