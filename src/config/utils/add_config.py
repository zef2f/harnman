# 24.02 написать тесты для add_config

import json
import os

def add_config(name: str, data: dict):
    """Add new JSON-file to ./config/, if it doesn't exist."""
    
    if not name.endswith(".json"):
        raise ValueError(f"Config file must have .json extension: {name}")
    
    file_path = os.path.join("config", name)

    try:
        with open(file_path, "x", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except FileExistsError:
        raise FileExistsError(f"Config file '{name}' already exists.")
    except FileNotFoundError:
        raise FileNotFoundError(f"Directory '{os.path.dirname(file_path)}' not found.")
    except PermissionError:
        raise PermissionError(f"Permission denied: cannot write to {file_path}")
    except IsADirectoryError:
        raise IsADirectoryError(f"Cannot create '{file_path}': A directory with this name exists.")
    except TypeError as e:
        raise TypeError(f"Invalid data type in JSON: {e}")
    except OSError as e:
        raise OSError(f"Filesystem error while creating '{name}': {e}")

    return True
