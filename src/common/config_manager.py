import json
import os
import re
from jsonschema import validate, ValidationError, SchemaError

CONFIG_DIR = os.getenv("HARNMAN_CONFIG_DIR", "assets/configs")

VALID_FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')


def add_config(harness_name: str, data: dict) -> bool:
    """
    Add a new JSON config file for a given harness, if it doesn't exist.
    """
    if not isinstance(data, dict):
        raise TypeError("Parameter 'data' must be a dictionary.")

    if not harness_name or not VALID_FILENAME_PATTERN.match(harness_name):
        raise ValueError(f"Invalid harness name: '{harness_name}'. Use only letters, numbers, underscore and hyphen.")

    config_filename = f"{harness_name}.json"
    file_path = os.path.join(CONFIG_DIR, config_filename)

    if not os.path.isdir(CONFIG_DIR):
        raise FileNotFoundError(f"Directory '{CONFIG_DIR}' not found.")

    try:
        with open(file_path, "x", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except FileExistsError:
        raise FileExistsError(f"Config file '{config_filename}' already exists in '{CONFIG_DIR}'.")
    except PermissionError:
        raise PermissionError(f"Permission denied: cannot write to '{file_path}'.")
    except IsADirectoryError:
        raise IsADirectoryError(f"Cannot create '{file_path}': A directory with this name exists.")
    except TypeError as e:
        raise TypeError(f"Invalid data type in JSON: {e}")
    except OSError as e:
        raise OSError(f"Filesystem error while creating '{config_filename}': {e}")

    return True


def delete_config(harness_name: str) -> bool:
    """
    Delete a JSON configuration file for a given harness.
    """
    config_filename = f"{harness_name}.json"
    file_path = os.path.join(CONFIG_DIR, config_filename)

    if not os.path.isdir(CONFIG_DIR):
        raise FileNotFoundError(f"Directory '{CONFIG_DIR}' not found.")

    try:
        os.remove(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file '{config_filename}' not found in '{CONFIG_DIR}'.")
    except PermissionError:
        raise PermissionError(f"Permission denied: cannot delete '{file_path}'.")
    except IsADirectoryError:
        raise IsADirectoryError(f"'{file_path}' is a directory, not a file.")
    except OSError as e:
        raise OSError(f"Filesystem error while deleting '{config_filename}': {e}")

    return True


def rename_config(old_harness: str, new_harness: str) -> bool:
    """
    Rename a JSON config file for a given harness.
    """
    old_filename = f"{old_harness}.json"
    new_filename = f"{new_harness}.json"

    old_path = os.path.join(CONFIG_DIR, old_filename)
    new_path = os.path.join(CONFIG_DIR, new_filename)

    if not os.path.isdir(CONFIG_DIR):
        raise FileNotFoundError(f"Directory '{CONFIG_DIR}' not found.")

    if not os.path.exists(old_path):
        raise FileNotFoundError(f"Config file '{old_filename}' not found in '{CONFIG_DIR}'.")

    if old_harness == new_harness:
        return True

    if os.path.exists(new_path):
        raise FileExistsError(f"A config file with the name '{new_filename}' already exists in '{CONFIG_DIR}'.")

    try:
        os.rename(old_path, new_path)
    except PermissionError:
        raise PermissionError(
            f"Permission denied: cannot rename '{old_path}' to '{new_path}'."
        )
    except OSError as e:
        raise OSError(
            f"Filesystem error while renaming '{old_path}' to '{new_path}': {e}"
        )

    return True


def list_config() -> list:
    """
    Return a list of harness names from the CONFIG_DIR (excluding .json extension).
    Only includes files with valid names (letters, numbers, underscore, hyphen).
    """
    if not os.path.isdir(CONFIG_DIR):
        raise FileNotFoundError(f"Directory '{CONFIG_DIR}' not found.")

    try:
        return [
            filename.removesuffix(".json")
            for filename in os.listdir(CONFIG_DIR)
            if filename.endswith(".json") and 
            os.path.isfile(os.path.join(CONFIG_DIR, filename)) and
            VALID_FILENAME_PATTERN.match(filename.removesuffix(".json"))
        ]
    except PermissionError:
        raise PermissionError(f"Permission denied: cannot access '{CONFIG_DIR}'.")
    except OSError as e:
        raise OSError(f"Filesystem error while accessing '{CONFIG_DIR}': {e}")


def read_config(harness_name: str) -> dict:
    """
    Read a JSON config file for a given harness and return its content as a dictionary.
    """
    config_filename = f"{harness_name}.json"
    file_path = os.path.join(CONFIG_DIR, config_filename)

    if not os.path.isdir(CONFIG_DIR):
        raise FileNotFoundError(f"Directory '{CONFIG_DIR}' not found.")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Config file '{config_filename}' not found in '{CONFIG_DIR}'.")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in '{config_filename}'.")
    except PermissionError:
        raise PermissionError(f"Permission denied: cannot read '{file_path}'.")
    except OSError as e:
        raise OSError(f"Filesystem error while reading '{file_path}': {e}")


def load_json_file(path: str) -> dict:
    """
    Load and return JSON data from a file.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File '{path}' not found.")
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in '{path}': {e}")
    except PermissionError:
        raise PermissionError(f"Permission denied: cannot read '{path}'.")
    except OSError as e:
        raise OSError(f"Filesystem error while reading '{path}': {e}")


def validate_json(data: dict, schema: dict) -> None:
    """
    Validate JSON data against a given schema.
    """
    try:
        validate(instance=data, schema=schema)
    except SchemaError as e:
        raise ValueError(f"Schema is invalid: {e.message}")
    except ValidationError as e:
        path = " -> ".join(str(p) for p in e.absolute_path)
        message = f"at '{path}': {e.message}" if path else e.message
        raise ValueError(f"Validation failed: {message}")


def validate_config(harness_name: str, schema_path: str) -> bool:
    """
    High-level function that validates the JSON config of a harness against a specified schema.
    """
    if not harness_name or not VALID_FILENAME_PATTERN.match(harness_name):
        raise ValueError(f"Invalid harness name: '{harness_name}'")

    schema_data = load_json_file(schema_path)
    config_data = load_json_file(os.path.join(CONFIG_DIR, f"{harness_name}.json"))

    validate_json(config_data, schema_data)
    return True
