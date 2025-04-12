# tests/test_base.py

import pytest
from unittest.mock import patch
from src.common import base
import subprocess


@pytest.fixture
def mock_harn_names():
    return ["harness1", "harness2"]


@pytest.fixture
def mock_fuzz_cmds():
    return {"harness1": "./fuzz_harness1", "harness2": "./fuzz_harness2"}


@pytest.fixture
def mock_cov_cmds():
    return {"harness1": "llvm-cov harness1", "harness2": "llvm-cov harness2"}


@pytest.fixture
def mock_build_cmds():
    return {
        "harness1": "clang -o harness1 harness1.c",
        "harness2": "clang -o harness2 harness2.c",
    }


def test_expand_shell_substitutions():
    """Test shell command substitution functionality."""
    assert base._expand_shell_substitutions("echo test") == "echo test"

    # Test command with substitution
    with patch("subprocess.check_output", return_value="test_output\n"):
        assert (
            base._expand_shell_substitutions("prefix $(echo test) suffix")
            == "prefix test_output suffix"
        )

    # Test multiple substitutions
    with patch("subprocess.check_output", side_effect=["one\n", "two\n"]):
        assert (
            base._expand_shell_substitutions("$(echo one) middle $(echo two)")
            == "one middle two"
        )

    # Test command execution error
    with patch(
        "subprocess.check_output",
        side_effect=subprocess.CalledProcessError(1, "cmd"),
    ):
        assert base._expand_shell_substitutions("$(invalid_command)") == ""


@patch("src.common.config_manager.list_config")
def test_get_harn_names(mock_list_config, mock_harn_names):
    """
    Tests retrieving the list of harnesses via get_harn_names().
    """
    # Test successful list retrieval
    mock_list_config.return_value = mock_harn_names
    assert base.get_harn_names() == mock_harn_names
    mock_list_config.assert_called_once()

    # Test with missing config directory
    mock_list_config.side_effect = FileNotFoundError
    assert base.get_harn_names() == []


@patch("src.common.config_editor.read_config_field")
def test_get_fuzz_cmd(mock_read_config_field, mock_fuzz_cmds):
    """
    Tests retrieving fuzzing command via get_fuzz_cmd().
    """
    # Test successful command retrieval
    for harn_name, expected_cmd in mock_fuzz_cmds.items():
        mock_read_config_field.return_value = expected_cmd
        assert base.get_fuzz_cmd(harn_name) == expected_cmd
        mock_read_config_field.assert_called_with(harn_name, "fuzz.fuzz_cmd")

    # Test with non-existent harness
    mock_read_config_field.side_effect = KeyError
    with pytest.raises(KeyError):
        base.get_fuzz_cmd("nonexistent")


@patch("src.common.config_editor.read_config_field")
def test_get_cov_cmd(mock_read_config_field, mock_cov_cmds):
    """
    Tests retrieving coverage command via get_cov_cmd().
    """
    # Test successful command retrieval
    for harn_name, expected_cmd in mock_cov_cmds.items():
        mock_read_config_field.return_value = expected_cmd
        assert base.get_cov_cmd(harn_name) == expected_cmd
        mock_read_config_field.assert_called_with(
            harn_name, "coverage.coverage_cmd"
        )

    # Test with non-existent harness
    mock_read_config_field.side_effect = KeyError
    with pytest.raises(KeyError):
        base.get_cov_cmd("nonexistent")


@patch("src.common.config_editor.read_config_field")
def test_get_build_cmd(mock_read_config_field, mock_build_cmds):
    """
    Tests retrieving build command via get_build_cmd().
    """
    # Test successful command retrieval
    for harn_name, expected_cmd in mock_build_cmds.items():
        mock_read_config_field.return_value = expected_cmd
        assert base.get_build_cmd(harn_name) == expected_cmd
        mock_read_config_field.assert_called_with(harn_name, "build.build_cmd")

    # Test with non-existent harness
    mock_read_config_field.side_effect = KeyError
    with pytest.raises(KeyError):
        base.get_build_cmd("nonexistent")
