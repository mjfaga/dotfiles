from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("sync_standard", ROOT / "scripts" / "sync_github_work_standard.py")
assert SPEC and SPEC.loader
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)


def target(checkout: Path, adapter="generated-modern", classification="native-type"):
    if adapter == "generated-modern":
        agents, skill = "AGENTS.src.md", ".claude/skills/github-work/SKILL.src.md"
    elif adapter == "generated-legacy":
        agents, skill = "AGENTS.src.md", "docs/skills/github-work.src.md"
    else:
        agents, skill = "AGENTS.md", ".claude/skills/github-work/SKILL.md"
    return {
        "repo": "sample-space/sample-app",
        "checkout": str(checkout),
        "adapter": adapter,
        "classification": classification,
        "agents_source_path": agents,
        "skill_source_path": skill,
        "checks": ["true"],
    }


class RendererTests(unittest.TestCase):
    def test_merge_marker_preserves_outside_bytes(self):
        original = "before\n<!-- BEGIN github-work-standard -->old<!-- END github-work-standard -->\nafter\n"
        rendered = sync.merge_marker(original, "<!-- BEGIN github-work-standard -->new<!-- END github-work-standard -->")
        self.assertEqual(rendered, "before\n<!-- BEGIN github-work-standard -->new<!-- END github-work-standard -->\nafter\n")

    def test_merge_marker_rejects_partial_markers(self):
        with self.assertRaises(sync.RenderError):
            sync.merge_marker("<!-- BEGIN github-work-standard -->", "block")

    def test_target_digest_is_deterministic(self):
        left = sync.digest_target({"repo": "sample-space/sample-app", "adapter": "plain"})
        right = sync.digest_target({"adapter": "plain", "repo": "sample-space/sample-app"})
        self.assertEqual(left, right)

    def test_all_documented_adapters_validate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            targets = []
            for index, adapter in enumerate(("generated-modern", "generated-legacy", "plain")):
                item = target(root, adapter)
                item["repo"] = f"sample-space/sample-{index}"
                targets.append(item)
            self.assertEqual(len(sync.validate_targets({"targets": targets})), 3)

    def test_validate_targets_rejects_unknown_layout_and_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            item = target(Path(directory))
            item["adapter"] = "unknown"
            with self.assertRaises(sync.RenderError):
                sync.validate_targets({"targets": [item]})
            item = target(Path(directory))
            item["helper_path"] = "../escape.py"
            with self.assertRaises(sync.RenderError):
                sync.validate_targets({"targets": [item]})

    def test_safe_output_rejects_symlink_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            checkout = root / "checkout"
            outside = root / "outside"
            checkout.mkdir()
            outside.mkdir()
            (checkout / "link").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(sync.RenderError):
                sync.safe_output_path(checkout.resolve(), "link/file.md")

    def test_merge_form_adopts_inline_labels_and_removes_dispatch_label(self):
        existing = "name: Existing bug\ndescription: Keep me\nlabels: ['dispatch', 'triage']\nbody:\n  - type: textarea\n"
        rendered = sync.merge_form(existing, "bug", "native-type", "{}", ["dispatch"])
        self.assertIn("type: Bug", rendered)
        self.assertIn('  - "triage"', rendered)
        self.assertNotIn("dispatch", rendered)
        self.assertIn("name: Existing bug\ndescription: Keep me\nbody:", rendered)

    def test_merge_form_managed_mode_preserves_unrelated_label(self):
        existing = "name: Existing\nlabels:\n  - triage\nbody: []\n"
        rendered = sync.merge_form(existing, "task", "managed-label", "{}")
        self.assertIn('  - "triage"', rendered)
        self.assertIn('  - "type:task"', rendered)
        self.assertIn("body: []", rendered)

    def test_marked_helper_keeps_shebang_first(self):
        rendered = sync.marked_helper("#!/usr/bin/env python3\nprint('ok')\n", "1.0.0", "a" * 40, "b" * 64)
        self.assertTrue(rendered.startswith("#!/usr/bin/env python3\n# github-work-standard:"))

    def test_source_sha_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(sync.RenderError):
                sync.verify_source(Path(directory), "0" * 40, "missing-tag")

    def test_checkout_override_preserves_configured_target_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            worktree = Path(directory) / "worktree"
            worktree.mkdir()
            (worktree / "AGENTS.src.md").write_text("# Existing\n")
            skill = worktree / ".claude/skills/github-work/SKILL.src.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("# Existing skill\n")
            configured = target(Path("/configured/primary/checkout"))
            config = Path(directory) / "targets.yml"
            config.write_text(json.dumps({"targets": [configured]}))
            args = Namespace(
                source_root=str(ROOT), config=str(config), source_sha="a" * 40,
                source_tag="test-tag", repos="all", check=False, dry_run=False,
                checkout_override=[f"sample-space/sample-app={worktree}"],
            )
            with mock.patch.object(sync, "verify_source"):
                self.assertEqual(sync.sync(args), 0)
            rendered = (worktree / "AGENTS.src.md").read_text()
            self.assertIn(f"target={sync.digest_target(configured)}", rendered)
            self.assertFalse(Path("/configured/primary/checkout/AGENTS.src.md").exists())

    def test_checkout_override_rejects_unknown_or_relative_paths(self):
        configured = target(Path("/configured/primary/checkout"))
        with self.assertRaises(sync.RenderError):
            sync.parse_checkout_overrides(["other-space/other-app=/tmp/worktree"], [configured])
        with self.assertRaises(sync.RenderError):
            sync.parse_checkout_overrides(["sample-space/sample-app=relative/path"], [configured])

    def test_full_render_then_check_and_dry_run(self):
        with tempfile.TemporaryDirectory() as directory:
            checkout = Path(directory) / "checkout"
            checkout.mkdir()
            (checkout / "AGENTS.src.md").write_text("# Existing\n")
            skill = checkout / ".claude/skills/github-work/SKILL.src.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("# Existing skill\n")
            config = Path(directory) / "targets.yml"
            config.write_text(json.dumps({"targets": [target(checkout)]}))
            args = Namespace(source_root=str(ROOT), config=str(config), source_sha="a" * 40, source_tag="test-tag", repos="all", check=False, dry_run=True)
            with mock.patch.object(sync, "verify_source"):
                self.assertEqual(sync.sync(args), 0)
            self.assertEqual((checkout / "AGENTS.src.md").read_text(), "# Existing\n")
            args.dry_run = False
            with mock.patch.object(sync, "verify_source"):
                self.assertEqual(sync.sync(args), 0)
            generated_helper = checkout / "scripts" / "github_work.py"
            self.assertTrue(generated_helper.exists())
            helper_spec = importlib.util.spec_from_file_location("generated_github_work", generated_helper)
            assert helper_spec and helper_spec.loader
            helper_module = importlib.util.module_from_spec(helper_spec)
            sys.modules[helper_spec.name] = helper_module
            helper_spec.loader.exec_module(helper_module)
            helper_text = generated_helper.read_text()
            helper_module.verify_content(
                helper_text,
                helper_module.provenance_from_text(helper_text),
                managed_region=False,
            )
            generated_skill = skill.read_text()
            self.assertTrue(generated_skill.startswith("---\nname: github-work\n"))
            self.assertIn("description:", generated_skill.split("---", 2)[1])
            generated_form = (checkout / ".github/ISSUE_TEMPLATE/bug.yml").read_text()
            self.assertIn("name:", generated_form)
            self.assertIn("description:", generated_form)
            self.assertIn('title: "[Bug] "', generated_form)
            self.assertNotIn('title: ""', generated_form)
            self.assertIn("body:", generated_form)
            args.check = True
            with mock.patch.object(sync, "verify_source"):
                self.assertEqual(sync.sync(args), 0)


if __name__ == "__main__":
    unittest.main()
