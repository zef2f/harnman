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
    
    return re.sub(pattern, _replace, cmd)

def get_harn_names() -> list:
    try:
        return config_manager.list_config()
    except FileNotFoundError:
        return []

def get_fuzz_cmd(harn_name: str) -> str:
    raw_cmd = config_editor.read_config_field(harn_name, "fuzz.fuzz_cmd")
    if not raw_cmd:
        return ""
    return raw_cmd

def get_cov_cmd(harn_name: str) -> str:
    raw_cmd = config_editor.read_config_field(harn_name, "coverage.coverage_cmd")
    if not raw_cmd:
        return ""
    return raw_cmd

def get_build_cmd(harn_name: str) -> str:
    raw_cmd = config_editor.read_config_field(harn_name, "build.build_cmd")
    if not raw_cmd:
        return ""
    return raw_cmd
