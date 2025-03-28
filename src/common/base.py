# src/common/base.py

from . import config_manager, config_editor

def get_wrap_names() -> list:
    """
    Returns a list of all available wrappers (configs).
    Uses list_config() from config_manager.
    """
    return config_manager.list_config()

def get_fuzz_cmd(wrap_name: str) -> str:
    """
    Returns the fuzzing command (fuzz_cmd) for the specified wrapper.
    Reads the "fuzz.fuzz_cmd" field using read_config_field() from config_editor.
    """
    return config_editor.read_config_field(wrap_name, "fuzz.fuzz_cmd")

def get_cov_cmd(wrap_name: str) -> str:
    """
    Returns the coverage collection command (coverage_cmd) for the specified wrapper.
    Reads the "coverage.coverage_cmd" field using read_config_field().
    """
    return config_editor.read_config_field(wrap_name, "coverage.coverage_cmd")

def get_build_cmd(wrap_name: str) -> str:
    """
    Returns the build command (build_cmd) for the specified wrapper.
    Reads the "build.build_cmd" field using read_config_field().
    """
    return config_editor.read_config_field(wrap_name, "build.build_cmd")

