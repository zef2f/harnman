# src/common/base.py

import re
import subprocess
import sys
from . import config_manager, config_editor


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
    raw_cmd = config_editor.read_config_field(
        harn_name, "coverage.coverage_cmd"
    )
    if not raw_cmd:
        return ""
    return raw_cmd


def get_build_cmd(harn_name: str) -> str:
    raw_cmd = config_editor.read_config_field(harn_name, "build.build_cmd")
    if not raw_cmd:
        return ""
    return raw_cmd
