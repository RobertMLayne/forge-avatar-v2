"""A fresh scaffold must preserve history without generating invalid Actions."""

import io
import os
import runpy
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


class ScaffoldWorkflowTests(unittest.TestCase):
    def test_empty_placeholders_are_archived_and_existing_content_is_preserved(self):
        script = Path(__file__).resolve().parents[1] / "scaffold_forgeavatar.py"
        with tempfile.TemporaryDirectory(prefix="forge-scaffold-") as temporary:
            root = Path(temporary) / "forgeavatar"
            # Run the repository's entry point with Windows' redirected-output
            # encoding, without a subprocess boundary or caller-supplied code.
            original_directory = Path.cwd()
            with io.TextIOWrapper(io.BytesIO(), encoding="cp1252") as output:
                try:
                    os.chdir(temporary)
                    with redirect_stdout(output):
                        runpy.run_path(str(script), run_name="__main__")
                finally:
                    os.chdir(original_directory)
            self.assertFalse((root / ".github" / "workflows").exists())
            archive = root / "docs" / "legacy-workflow-placeholders"
            self.assertEqual(
                sorted(path.name for path in archive.iterdir()),
                ["gh-pages.yml.disabled", "python.yml.disabled"],
            )
            self.assertTrue(all(path.read_bytes() == b"" for path in archive.iterdir()))
            existing = root / "forgeavatar" / "config.py"
            existing.write_text("# existing user configuration\n", encoding="utf-8")
            with io.TextIOWrapper(io.BytesIO(), encoding="cp1252") as output:
                try:
                    os.chdir(temporary)
                    with redirect_stdout(output):
                        runpy.run_path(str(script), run_name="__main__")
                finally:
                    os.chdir(original_directory)
            self.assertEqual(existing.read_text(encoding="utf-8"), "# existing user configuration\n")
            self.assertFalse((root / ".github" / "workflows").exists())


if __name__ == "__main__":
    unittest.main()
