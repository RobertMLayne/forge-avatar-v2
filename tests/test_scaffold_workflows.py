"""A fresh scaffold must preserve history without generating invalid Actions."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class ScaffoldWorkflowTests(unittest.TestCase):
    def test_empty_placeholders_are_archived_and_existing_content_is_preserved(self):
        script = Path(__file__).resolve().parents[1] / "scaffold_forgeavatar.py"
        with tempfile.TemporaryDirectory(prefix="forge-scaffold-") as temporary:
            root = Path(temporary) / "forgeavatar"
            command = [sys.executable, "-B", str(script)]
            subprocess.run(command, cwd=temporary, check=True, capture_output=True)
            self.assertFalse((root / ".github" / "workflows").exists())
            archive = root / "docs" / "legacy-workflow-placeholders"
            self.assertEqual(
                sorted(path.name for path in archive.iterdir()),
                ["gh-pages.yml.disabled", "python.yml.disabled"],
            )
            self.assertTrue(all(path.read_bytes() == b"" for path in archive.iterdir()))
            existing = root / "forgeavatar" / "config.py"
            existing.write_text("# existing user configuration\n", encoding="utf-8")
            subprocess.run(command, cwd=temporary, check=True, capture_output=True)
            self.assertEqual(existing.read_text(encoding="utf-8"), "# existing user configuration\n")
            self.assertFalse((root / ".github" / "workflows").exists())


if __name__ == "__main__":
    unittest.main()
