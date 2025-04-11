import unittest
from unittest.mock import patch
import sys
from io import StringIO
import src.wrapman as wrapman


class TestWrapmanCLI(unittest.TestCase):

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

    @patch("wrapman.base.get_wrap_names", return_value=["wrapper1", "wrapper2"])
    def test_list_wrappers(self, mock_get_wrap_names):
        """Test listing all wrappers."""
        sys.argv = ["wrapman.py", "-l"]
        wrapman.main()
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, "wrapper1\nwrapper2")

    @patch("wrapman.base.get_wrap_names", return_value=[])
    def test_list_wrappers_empty(self, mock_get_wrap_names):
        """Test listing when there are no wrappers."""
        sys.argv = ["wrapman.py", "-l"]
        wrapman.main()
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, "No wrappers found.")

    @patch("wrapman.base.get_fuzz_cmd", return_value="./fuzz_wrapper1")
    def test_fuzz_cmd(self, mock_get_fuzz_cmd):
        """Test retrieving the fuzzing command for a wrapper."""
        sys.argv = ["wrapman.py", "-fcmd", "wrapper1"]
        wrapman.main()
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, "./fuzz_wrapper1")

    @patch("wrapman.base.get_fuzz_cmd", side_effect=KeyError)
    def test_fuzz_cmd_not_found(self, mock_get_fuzz_cmd):
        """Test error handling when requesting a fuzz command for a nonexistent wrapper."""
        sys.argv = ["wrapman.py", "-fcmd", "unknown_wrapper"]
        with self.assertRaises(SystemExit) as cm:
            wrapman.main()
        self.assertEqual(cm.exception.code, 1)
        error_output = sys.stderr.getvalue().strip()
        print(error_output)
        self.assertEqual(error_output, "Error: Wrapper 'unknown_wrapper' not found or no fuzz command specified.")

    @patch("wrapman.base.get_build_cmd", return_value="clang -o wrapper1 wrapper1.c")
    def test_build_cmd(self, mock_get_build_cmd):
        """Test retrieving the build command for a wrapper."""
        sys.argv = ["wrapman.py", "-bcmd", "wrapper1"]
        wrapman.main()
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, "clang -o wrapper1 wrapper1.c")

    @patch("wrapman.base.get_build_cmd", side_effect=KeyError)
    def test_build_cmd_not_found(self, mock_get_build_cmd):
        """Test error handling when requesting a build command for a nonexistent wrapper."""
        sys.argv = ["wrapman.py", "-bcmd", "unknown_wrapper"]
        with self.assertRaises(SystemExit) as cm:
            wrapman.main()
        self.assertEqual(cm.exception.code, 1)
        error_output = sys.stderr.getvalue().strip()
        self.assertEqual(error_output, "Error: Wrapper 'unknown_wrapper' not found or no build command specified.")

    @patch("wrapman.base.get_cov_cmd", return_value="llvm-cov wrapper1")
    def test_coverage_cmd(self, mock_get_cov_cmd):
        """Test retrieving the coverage collection command for a wrapper."""
        sys.argv = ["wrapman.py", "-ccmd", "wrapper1"]
        wrapman.main()
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, "llvm-cov wrapper1")

    @patch("wrapman.base.get_cov_cmd", side_effect=KeyError)
    def test_coverage_cmd_not_found(self, mock_get_cov_cmd):
        """Test error handling when requesting a coverage command for a nonexistent wrapper."""
        sys.argv = ["wrapman.py", "-ccmd", "unknown_wrapper"]
        with self.assertRaises(SystemExit) as cm:
            wrapman.main()
        self.assertEqual(cm.exception.code, 1)
        error_output = sys.stderr.getvalue().strip()
        self.assertEqual(error_output, "Error: Wrapper 'unknown_wrapper' not found or no coverage command specified.")

    def test_help_message(self):
        """Test displaying the help message."""
        sys.argv = ["wrapman.py"]
        with self.assertRaises(SystemExit) as cm:
            wrapman.main()
        self.assertEqual(cm.exception.code, 0)
        output = sys.stdout.getvalue()
        self.assertIn("CLI utility for managing fuzzing wrappers", output)


if __name__ == "__main__":
    unittest.main()
