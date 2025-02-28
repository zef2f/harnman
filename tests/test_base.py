# tests/test_base.py

import pytest
from unittest.mock import patch
from src.common import base

@pytest.fixture
def mock_wrap_names():
    return ["datetime_fromisoformat", "array_array", "tar", "zip"]

@pytest.fixture
def mock_fuzz_cmds():
    return {
        "datetime_fromisoformat": "./datetime_fromisoformat base-corpus/ -merge=0 -artifact_prefix=artifacts/ -reload=10 -max_total_time=10",
        "array_array": "./array_array -artifact_prefix=artifacts/ -reload=10 -max_total_time=10",
        "tar": "PYTHONMALLOC=malloc ./tar base-corpus/tar -artifact_prefix=artifacts/ -max_total_time=30 -rss_limit_mb=6000 > ~/tmp.txt",
        "zip": "PYTHONMALLOC=malloc ./zip base-corpus/zip -artifact_prefix=artifacts/ -max_total_time=30 -rss_limit_mb=6000 > ~/tmp.txt",
    }

@pytest.fixture
def mock_cov_cmds():
    return {
        "datetime_fromisoformat": "llvm-profdata merge -sparse default.profraw -o default.profdata",
        "array_array": "llvm-profdata merge -sparse default.profraw -o default.profdata",
        "tar": "llvm-profdata merge -sparse tar.profraw -o tar.profdata",
        "zip": "llvm-profdata merge -sparse zip.profraw -o zip.profdata",
    }

@pytest.fixture
def mock_build_cmds():
    return {
        "datetime_fromisoformat": "clang -fsanitize=fuzzer,address $(python3-config --includes) -lpython3.9 -o datetime_fromisoformat datetime_fromisoformat.c $(python3-config --ldflags)",
        "array_array": "clang -fsanitize=fuzzer,address $(python3-config --includes) -lpython3.9 -o array_array array_array.c $(python3-config --ldflags)",
        "tar": "clang -fsanitize=fuzzer,address $(python3-config --includes) -lpython3.9 -o tar tar.c $(python3-config --ldflags)",
        "zip": "clang -fsanitize=fuzzer,address $(python3-config --includes) -lpython3.9 -o zip zip.c $(python3-config --ldflags)",
    }

@patch("src.common.config_manager.list_config")
def test_get_wrap_names(mock_list_config, mock_wrap_names):
    """
    Тестирует получение списка обёрток через get_wrap_names().
    """
    mock_list_config.return_value = mock_wrap_names
    assert base.get_wrap_names() == mock_wrap_names
    mock_list_config.assert_called_once()

@patch("src.common.config_editor.read_config_field")
def test_get_fuzz_cmd(mock_read_config_field, mock_fuzz_cmds):
    """
    Тестирует получение команды для фаззинга через get_fuzz_cmd().
    """
    for wrap_name, expected_cmd in mock_fuzz_cmds.items():
        mock_read_config_field.return_value = expected_cmd
        assert base.get_fuzz_cmd(wrap_name) == expected_cmd
        mock_read_config_field.assert_called_with(wrap_name, "fuzz.fuzz_cmd")

@patch("src.common.config_editor.read_config_field")
def test_get_cov_cmd(mock_read_config_field, mock_cov_cmds):
    """
    Тестирует получение команды для покрытия через get_cov_cmd().
    """
    for wrap_name, expected_cmd in mock_cov_cmds.items():
        mock_read_config_field.return_value = expected_cmd
        assert base.get_cov_cmd(wrap_name) == expected_cmd
        mock_read_config_field.assert_called_with(wrap_name, "coverage.coverage_cmd")

@patch("src.common.config_editor.read_config_field")
def test_get_build_cmd(mock_read_config_field, mock_build_cmds):
    """
    Тестирует получение команды для сборки через get_build_cmd().
    """
    for wrap_name, expected_cmd in mock_build_cmds.items():
        mock_read_config_field.return_value = expected_cmd
        assert base.get_build_cmd(wrap_name) == expected_cmd
        mock_read_config_field.assert_called_with(wrap_name, "build.build_cmd")

