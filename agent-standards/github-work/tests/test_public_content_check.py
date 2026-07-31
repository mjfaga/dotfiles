from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("public_check", ROOT / "scripts" / "public_content_check.py")
assert SPEC and SPEC.loader
check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check)


class PublicContentTests(unittest.TestCase):
    def test_private_values_cover_repo_parts_paths_keys_areas_and_logins(self):
        values = check.private_values(
            {"targets": [{"repo": "sample-space/private-app", "checkout": "/runtime/private-app", "ownership_key": "private-area"}]},
            {"mappings": [{"repo": "sample-space/private-app", "area": "private-area", "logins": ["private-user"]}]},
        )
        for value in ("sample-space/private-app", "sample-space", "private-app", "/runtime/private-app", "private-area", "private-user"):
            self.assertIn(value, values)

    def test_scan_finds_runtime_private_value_with_boundaries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("sample-space/private-app\n")
            violations = check.scan(root, {"sample-space/private-app"})
            self.assertEqual(violations[0]["kind"], "private-value")

    def test_scan_does_not_match_login_inside_ordinary_word(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("preprivate-userpost\n")
            self.assertEqual(check.scan(root, {"private-user"}), [])

    def test_scan_finds_secret_pattern(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            token = "github_" + "pat_" + "abcdefghijklmnopqrstuvwxyz123456"
            (root / "value.txt").write_text(token + "\n")
            self.assertTrue(check.scan(root, set()))

    def test_scan_finds_structural_receipt_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "evidence.json").write_text(json.dumps({"receipt_id": "sample", "operations": []}))
            violations = check.scan(root, set())
            self.assertEqual(violations[0]["kind"], "rollout-receipt")

    def test_scan_ignores_synthetic_public_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("sample-space/sample-app and /runtime/path\n")
            self.assertEqual(check.scan(root, {"different-space/private-app"}), [])


if __name__ == "__main__":
    unittest.main()
