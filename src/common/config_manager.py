import json
import os
from jsonschema import validate, ValidationError, SchemaError

# Получаем путь к директории конфигов из переменной окружения или используем "config/" по умолчанию
CONFIG_DIR = os.getenv("WRAPMAN_CONFIG_DIR", "config")


def add_config(wrapper_name: str, data: dict) -> bool:
    """
    Add a new JSON config file for a given wrapper, if it doesn't exist.

    :param wrapper_name: Название обёртки (без .json)
    :param data: Содержимое конфигурационного файла (словарь)
    :return: True, если успешно добавлен
    """
    if not isinstance(data, dict):
        raise TypeError("Parameter 'data' must be a dictionary.")

    config_filename = f"{wrapper_name}.json"
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


def delete_config(wrapper_name: str) -> bool:
    """
    Delete a JSON configuration file for a given wrapper.

    :param wrapper_name: Название обёртки (без .json)
    :return: True, если успешно удалён
    """
    config_filename = f"{wrapper_name}.json"
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


def rename_config(old_wrapper: str, new_wrapper: str) -> bool:
    """
    Rename a JSON config file for a given wrapper.

    :param old_wrapper: Текущее название обёртки (без .json)
    :param new_wrapper: Новое название обёртки (без .json)
    :return: True, если переименование успешно
    """
    old_filename = f"{old_wrapper}.json"
    new_filename = f"{new_wrapper}.json"

    old_path = os.path.join(CONFIG_DIR, old_filename)
    new_path = os.path.join(CONFIG_DIR, new_filename)

    if not os.path.isdir(CONFIG_DIR):
        raise FileNotFoundError(f"Directory '{CONFIG_DIR}' not found.")

    if not os.path.exists(old_path):
        raise FileNotFoundError(f"Config file '{old_filename}' not found in '{CONFIG_DIR}'.")

    if old_wrapper == new_wrapper:
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
    Return a list of wrapper names from the CONFIG_DIR (excluding .json extension).

    :return: Список названий обёрток (строки)
    """
    if not os.path.isdir(CONFIG_DIR):
        raise FileNotFoundError(f"Directory '{CONFIG_DIR}' not found.")

    try:
        return [
            filename.removesuffix(".json")
            for filename in os.listdir(CONFIG_DIR)
            if filename.endswith(".json") and os.path.isfile(os.path.join(CONFIG_DIR, filename))
        ]
    except PermissionError:
        raise PermissionError(f"Permission denied: cannot access '{CONFIG_DIR}'.")
    except OSError as e:
        raise OSError(f"Filesystem error while accessing '{CONFIG_DIR}': {e}")


def read_config(wrapper_name: str) -> dict:
    """
    Read a JSON config file for a given wrapper and return its content as a dictionary.

    :param wrapper_name: Название обёртки (без .json)
    :return: Содержимое конфигурационного файла (dict)
    """
    config_filename = f"{wrapper_name}.json"
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


# ------------------ Вспомогательные функции для валидации ------------------

def load_json_file(path: str) -> dict:
    """
    Load and return JSON data from a file.
    Вызывается внутри validate_config (и может использоваться отдельно).
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
    Raises ValueError if invalid data or schema.
    """
    try:
        validate(instance=data, schema=schema)
    except SchemaError as e:
        raise ValueError(f"Schema is invalid: {e}")
    except ValidationError as e:
        # Можно при желании собирать все ошибки, если это важно
        raise ValueError(f"Validation failed: {e.message}")


def validate_config(wrapper_name: str, schema_path: str) -> bool:
    """
    High-level function that validates the JSON config of a wrapper against a specified schema.

    :param wrapper_name: Название обёртки (без .json)
    :param schema_path: Путь к JSON-схеме, согласно которой валидируем
    :return: True, если валидация прошла успешно
    """
    config_path = os.path.join(CONFIG_DIR, f"{wrapper_name}.json")
    schema_data = load_json_file(schema_path)
    config_data = load_json_file(config_path)

    validate_json(config_data, schema_data)
    return True
