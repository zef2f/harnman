import json
import os

# Позволяем переопределить директорию через переменную окружения
CONFIG_DIR = os.getenv("WRAPMAN_CONFIG_DIR", "assets/configs")


def _resolve_config_path(wrapper_name: str) -> str:
    """
    Построить путь к файлу конфигурации для данной обёртки (wrapper_name).
    Проверить, что директория CONFIG_DIR существует.
    """
    if not os.path.isdir(CONFIG_DIR):
        raise FileNotFoundError(f"Configuration directory '{CONFIG_DIR}' not found. "
                                "Please create it or set WRAPMAN_CONFIG_DIR.")

    config_filename = f"{wrapper_name}.json"
    return os.path.join(CONFIG_DIR, config_filename)


def _load_config_data(wrapper_name: str) -> dict:
    """
    Загрузить и вернуть JSON-данные из файла конфигурации.
    """
    file_path = _resolve_config_path(wrapper_name)
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


def _save_config_data(wrapper_name: str, config_data: dict) -> None:
    """
    Сохранить JSON-данные в файл конфигурации (перезапись файла).
    """
    file_path = _resolve_config_path(wrapper_name)

    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(config_data, file, indent=4)
    except PermissionError:
        raise PermissionError(f"Permission denied: cannot write to '{file_path}'.")
    except OSError as e:
        raise OSError(f"Filesystem error while writing '{file_path}': {e}")


def read_config_field(wrapper_name: str, field_path: str):
    """
    Прочитать конкретное (возможно, вложенное) поле из JSON-файла конфигурации.

    :param wrapper_name: Название обёртки (без .json)
    :param field_path: Путь к полю (напр. "fuzz.options.max_runs")
    :return: Значение указанного поля
    """
    config_data = _load_config_data(wrapper_name)

    keys = field_path.split(".")
    ref = config_data
    for key in keys:
        if key not in ref:
            raise KeyError(f"Key '{field_path}' not found in '{wrapper_name}.json'.")
        ref = ref[key]

    return ref


def update_config_field(wrapper_name: str, field_path: str, value) -> bool:
    """
    Добавить новое или обновить существующее поле в JSON-файле конфигурации.

    :param wrapper_name: Название обёртки (без .json)
    :param field_path: Путь к полю (напр. "fuzz.options.max_runs")
    :param value: Значение, которое нужно установить
    :return: True, если обновление успешно
    """
    config_data = _load_config_data(wrapper_name)

    keys = field_path.split(".")
    ref = config_data
    for key in keys[:-1]:
        # Если ключ отсутствует или там не словарь — создаём пустой словарь
        if key not in ref or not isinstance(ref[key], dict):
            ref[key] = {}
        ref = ref[key]

    ref[keys[-1]] = value

    _save_config_data(wrapper_name, config_data)
    return True


def delete_config_field(wrapper_name: str, field_path: str) -> bool:
    """
    Удалить поле из JSON-файла конфигурации.

    :param wrapper_name: Название обёртки (без .json)
    :param field_path: Путь к полю (напр. "fuzz.options.max_runs")
    :return: True, если удаление успешно
    """
    config_data = _load_config_data(wrapper_name)

    keys = field_path.split(".")
    ref = config_data
    for key in keys[:-1]:
        if key not in ref or not isinstance(ref[key], dict):
            raise KeyError(f"Key '{field_path}' not found in '{wrapper_name}.json'.")
        ref = ref[key]

    last_key = keys[-1]
    if last_key in ref:
        del ref[last_key]
    else:
        raise KeyError(f"Key '{field_path}' not found in '{wrapper_name}.json'.")

    _save_config_data(wrapper_name, config_data)
    return True
