import unittest
from unittest.mock import patch
import sys
from io import StringIO
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src import harnman


class TestHarnman(unittest.TestCase):

    def setUp(self):
        """Redirect stdout and stderr for testing."""
        self.stdout_backup = sys.stdout
        self.stderr_backup = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()

    def tearDown(self):
        """Restore stdout and stderr after tests."""
        sys.stdout = self.stdout_backup
        sys.stderr = self.stderr_backup

    @patch("src.common.config_manager.list_config", return_value=["harness1", "harness2"])
    def test_list_harnesses(self, mock_list_config):
        """Test listing all harnesses."""
        sys.argv = ["harnman.py", "-l"]
        harnman.main()
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, "harness1\nharness2")

    @patch("src.common.config_manager.list_config", side_effect=FileNotFoundError)
    def test_list_harnesses_empty(self, mock_list_config):
        """Test listing when there are no harnesses."""
        sys.argv = ["harnman.py", "-l"]
        harnman.main()
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, "No harnesses found.")

    @patch("src.common.config_editor.read_config_field", return_value="./fuzz_harness1")
    def test_print_fuzz_cmd(self, mock_read_config_field):
        """Test retrieving the fuzzing command for a harness."""
        sys.argv = ["harnman.py", "-fcmd", "harness1"]
        harnman.main()
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, "./fuzz_harness1")

    @patch("src.common.config_editor.read_config_field", side_effect=KeyError)
    def test_print_fuzz_cmd_not_found(self, mock_read_config_field):
        """Test error handling when requesting a fuzz command for a nonexistent harness."""
        sys.argv = ["harnman.py", "-fcmd", "unknown_harness"]
        with self.assertRaises(SystemExit) as cm:
            harnman.main()
        self.assertEqual(cm.exception.code, 1)
        error_output = sys.stderr.getvalue().strip()
        self.assertEqual(error_output, "Error: Harness 'unknown_harness' not found or no fuzz command specified.")

    @patch("src.common.config_editor.read_config_field", return_value="clang -o harness1 harness1.c")
    def test_print_build_cmd(self, mock_read_config_field):
        """Test retrieving the build command for a harness."""
        sys.argv = ["harnman.py", "-bcmd", "harness1"]
        harnman.main()
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, "clang -o harness1 harness1.c")

    @patch("src.common.config_editor.read_config_field", side_effect=KeyError)
    def test_print_build_cmd_not_found(self, mock_read_config_field):
        """Test error handling when requesting a build command for a nonexistent harness."""
        sys.argv = ["harnman.py", "-bcmd", "unknown_harness"]
        with self.assertRaises(SystemExit) as cm:
            harnman.main()
        self.assertEqual(cm.exception.code, 1)
        error_output = sys.stderr.getvalue().strip()
        self.assertEqual(error_output, "Error: Harness 'unknown_harness' not found or no build command specified.")

    @patch("src.common.config_editor.read_config_field", return_value="llvm-cov harness1")
    def test_print_cov_cmd(self, mock_read_config_field):
        """Test retrieving the coverage collection command for a harness."""
        sys.argv = ["harnman.py", "-ccmd", "harness1"]
        harnman.main()
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, "llvm-cov harness1")

    @patch("src.common.config_editor.read_config_field", side_effect=KeyError)
    def test_print_cov_cmd_not_found(self, mock_read_config_field):
        """Test error handling when requesting a coverage command for a nonexistent harness."""
        sys.argv = ["harnman.py", "-ccmd", "unknown_harness"]
        with self.assertRaises(SystemExit) as cm:
            harnman.main()
        self.assertEqual(cm.exception.code, 1)
        error_output = sys.stderr.getvalue().strip()
        self.assertEqual(error_output, "Error: Harness 'unknown_harness' not found or no coverage command specified.")

    def test_no_args(self):
        """Test running without arguments."""
        sys.argv = ["harnman.py"]
        with self.assertRaises(SystemExit) as cm:
            harnman.main()
        self.assertEqual(cm.exception.code, 0)
        output = sys.stdout.getvalue()
        self.assertIn("CLI utility for managing fuzzing harnesses", output)


if __name__ == "__main__":
    unittest.main()
