import json
import os

CONFIG_DIR = os.getenv("HARNMAN_CONFIG_DIR", "assets/configs")


def _resolve_config_path(harness_name: str) -> str:
    """
    Build the configuration file path for the given harness.
    Check that the CONFIG_DIR directory exists.
    """
    if not os.path.isdir(CONFIG_DIR):
        raise FileNotFoundError(
            f"Configuration directory '{CONFIG_DIR}' not found. "
            "Please create it or set HARNMAN_CONFIG_DIR."
        )

    config_filename = f"{harness_name}.json"
    return os.path.join(CONFIG_DIR, config_filename)


def _load_config_data(harness_name: str) -> dict:
    """
    Load and return JSON data from the configuration file.
    """
    file_path = _resolve_config_path(harness_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Config file '{file_path}' not found.")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in '{file_path}': {e}")
    except PermissionError:
        raise PermissionError(f"Permission denied: cannot read '{file_path}'.")
    except OSError as e:
        raise OSError(f"Filesystem error while reading '{file_path}': {e}")


def _save_config_data(harness_name: str, config_data: dict) -> None:
    """
    Save JSON data to the configuration file (overwrites the file).
    """
    file_path = _resolve_config_path(harness_name)

    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(config_data, file, indent=4)
    except PermissionError:
        raise PermissionError(
            f"Permission denied: cannot write to '{file_path}'."
        )
    except OSError as e:
        raise OSError(f"Filesystem error while writing '{file_path}': {e}")


def read_config_field(harness_name: str, field_path: str):
    """
    Read a specific (possibly nested) field from the JSON configuration file.
    """
    config_data = _load_config_data(harness_name)

    keys = field_path.split(".")
    ref = config_data
    for key in keys:
        if key not in ref:
            raise KeyError(
                f"Key '{field_path}' not found in '{harness_name}.json'."
            )
        ref = ref[key]

    return ref


def update_config_field(harness_name: str, field_path: str, value) -> bool:
    """
    Add a new or update an existing field in the JSON configuration file.
    """
    config_data = _load_config_data(harness_name)

    keys = field_path.split(".")
    ref = config_data
    for key in keys[:-1]:
        if key not in ref or not isinstance(ref[key], dict):
            ref[key] = {}
        ref = ref[key]

    ref[keys[-1]] = value

    _save_config_data(harness_name, config_data)
    return True


def delete_config_field(harness_name: str, field_path: str) -> bool:
    """
    Delete a field from the JSON configuration file.
    """
    config_data = _load_config_data(harness_name)

    keys = field_path.split(".")
    ref = config_data
    for key in keys[:-1]:
        if key not in ref or not isinstance(ref[key], dict):
            raise KeyError(
                f"Key '{field_path}' not found in '{harness_name}.json'."
            )
        ref = ref[key]

    last_key = keys[-1]
    if last_key in ref:
        del ref[last_key]
    else:
        raise KeyError(
            f"Key '{field_path}' not found in '{harness_name}.json'."
        )

    _save_config_data(harness_name, config_data)
    return True
