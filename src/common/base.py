# src/common/base.py

import re
import subprocess
import sys
from . import config_manager, config_editor

def _expand_shell_substitutions(cmd: str) -> str:
    """
    Finds all occurrences of $(...) and executes them as shell commands,
    returning the substituted result.
    
    Args:
        cmd: Command string that may contain $(...) substitutions
        
    Returns:
        Command string with all $(...) replaced by their execution results
    """
    pattern = r'\$\(([^)]+)\)'  # Regex to find $(...)
    
    def _replace(match):
        # Extract command without parentheses
        command_inside = match.group(1).strip()
        try:
            # Execute command in shell and return result without extra newlines
            output = subprocess.check_output(command_inside, shell=True, text=True)
            return output.strip()
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Shell substitution failed for '{command_inside}': {e}", file=sys.stderr)
            return ""
    
    # Perform substitution by pattern
    return re.sub(pattern, _replace, cmd)

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
    Expands any $(...) shell substitutions in the command.
    """
    raw_cmd = config_editor.read_config_field(wrap_name, "fuzz.fuzz_cmd")
    if not raw_cmd:
        return ""
    return _expand_shell_substitutions(raw_cmd)

def get_cov_cmd(wrap_name: str) -> str:
    """
    Returns the coverage collection command (coverage_cmd) for the specified wrapper.
    Reads the "coverage.coverage_cmd" field using read_config_field().
    Expands any $(...) shell substitutions in the command.
    """
    raw_cmd = config_editor.read_config_field(wrap_name, "coverage.coverage_cmd")
    if not raw_cmd:
        return ""
    return _expand_shell_substitutions(raw_cmd)

def get_build_cmd(wrap_name: str) -> str:
    """
    Returns the build command (build_cmd) for the specified wrapper.
    Reads the "build.build_cmd" field using read_config_field().
    Expands any $(...) shell substitutions in the command.
    """
    raw_cmd = config_editor.read_config_field(wrap_name, "build.build_cmd")
    if not raw_cmd:
        return ""
    return _expand_shell_substitutions(raw_cmd)

