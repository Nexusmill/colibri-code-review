"""Connect the repo's script and pytest batteries to the native unittest gate."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RepositoryChecks(unittest.TestCase):
    def test_repository_batteries(self):
        commands = [
            [sys.executable, "-B", "tests/test_analyzer.py"],
            [sys.executable, "-B", "tests/test_sweep_fixes.py"],
            [sys.executable, "-B", "tests/test_scanner_ext.py"],
            [sys.executable, "-B", "-m", "pytest", "-q",
             "tests/test_agent_error_rates.py", "tests/test_review_remediation.py",
             "tests/test_console_remediation.py"],
        ]
        for command in commands:
            with self.subTest(command=command):
                result = subprocess.run(command, cwd=ROOT, text=True, encoding="utf-8",
                                        errors="replace", capture_output=True, timeout=180)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
