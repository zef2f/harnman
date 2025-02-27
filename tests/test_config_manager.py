import os
import json
import shutil
import pytest
from jsonschema import ValidationError
from src.common import config_manager


@pytest.fixture(scope="function")
def config_dir(tmp_path, monkeypatch):
    """
    Создаёт временную директорию config/, подменяет WRAPMAN_CONFIG_DIR,
    пересоздаёт CONFIG_DIR в модуле config_manager и удаляет после тестов.
    """
    config_path = tmp_path / "config"
    config_path.mkdir(parents=True, exist_ok=True)  # Создаём директорию

    # Обновляем переменную окружения
    monkeypatch.setenv("WRAPMAN_CONFIG_DIR", str(config_path))

    # Перегружаем `config_manager`, чтобы он обновил CONFIG_DIR
    import importlib
    importlib.reload(config_manager)

    yield config_path  # Передаём путь тестам

    # Удаляем директорию после тестов
    if config_path.exists():
        shutil.rmtree(config_path, ignore_errors=True)


def test_add_config_success(config_dir):
    """Проверяем, что можем успешно создать новый конфиг."""
    data = {"foo": "bar"}
    result = config_manager.add_config("test_wrapper", data)
    assert result is True

    config_path = config_dir / "test_wrapper.json"
    assert config_path.exists()

    with open(config_path, "r", encoding="utf-8") as f:
        content = json.load(f)
    assert content == data


def test_add_config_already_exists(config_dir):
    """Если конфиг уже есть, add_config должен кинуть FileExistsError."""
    config_manager.add_config("duplicate_wrapper", {"key": 123})

    with pytest.raises(FileExistsError):
        config_manager.add_config("duplicate_wrapper", {"foo": "bar"})


def test_delete_config_success(config_dir):
    """Проверяем удаление существующего файла."""
    config_manager.add_config("removable_wrapper", {"need": "to_delete"})
    config_path = config_dir / "removable_wrapper.json"
    assert config_path.exists()

    result = config_manager.delete_config("removable_wrapper")
    assert result is True
    assert not config_path.exists()


def test_delete_config_not_found(config_dir):
    """Если удаляем несуществующий файл, выбрасываем FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        config_manager.delete_config("nonexistent")


def test_rename_config_success(config_dir):
    """Проверяем успешное переименование."""
    config_manager.add_config("old_wrapper", {"old": "data"})
    old_path = config_dir / "old_wrapper.json"
    new_path = config_dir / "new_wrapper.json"

    assert old_path.exists()
    assert not new_path.exists()

    result = config_manager.rename_config("old_wrapper", "new_wrapper")
    assert result is True
    assert not old_path.exists()
    assert new_path.exists()

    with open(new_path, "r", encoding="utf-8") as f:
        content = json.load(f)
    assert content == {"old": "data"}


def test_rename_config_same_name(config_dir):
    """Если названия совпадают, rename_config просто вернёт True и ничего не сделает."""
    config_manager.add_config("same_wrapper", {"key": 1})
    old_path = config_dir / "same_wrapper.json"

    result = config_manager.rename_config("same_wrapper", "same_wrapper")
    assert result is True
    assert old_path.exists()


def test_rename_config_not_found(config_dir):
    """Если старого файла нет, выбрасываем FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        config_manager.rename_config("no_such_wrapper", "does_not_matter")


def test_rename_config_new_already_exists(config_dir):
    """Если новый файл уже существует, выбрасываем FileExistsError."""
    config_manager.add_config("old_wrapper", {"data": 123})
    config_manager.add_config("already_exists", {"other": 456})

    with pytest.raises(FileExistsError):
        config_manager.rename_config("old_wrapper", "already_exists")


def test_list_config(config_dir):
    """Проверяем, что list_config даёт список без .json."""
    config_manager.add_config("first", {"a": 1})
    config_manager.add_config("second", {"b": 2})
    config_manager.add_config("third", {"c": 3})

    result = config_manager.list_config()
    assert set(result) == {"first", "second", "third"}


def test_read_config_success(config_dir):
    """Проверяем, что read_config возвращает содержимое JSON."""
    data = {"alpha": 100, "beta": 200}
    config_manager.add_config("reader_wrapper", data)

    read_data = config_manager.read_config("reader_wrapper")
    assert read_data == data


def test_read_config_not_found(config_dir):
    """Если файл не найден, должно быть FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        config_manager.read_config("missing_wrapper")


def test_read_config_invalid_json(config_dir):
    """Если JSON невалидный, ждём ValueError."""
    bad_config = config_dir / "bad_wrapper.json"
    bad_config.write_text('{"invalid": ???}', encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid JSON format"):
        config_manager.read_config("bad_wrapper")


def test_validate_config_success(config_dir):
    """Проверяем validate_config на валидном конфиге."""
    schema_path = config_dir / "test_schema.json"
    schema = {
        "type": "object",
        "properties": {
            "foo": {"type": "string"}
        },
        "required": ["foo"]
    }
    schema_path.write_text(json.dumps(schema), encoding="utf-8")

    config_manager.add_config("valid_wrapper", {"foo": "hello"})

    result = config_manager.validate_config("valid_wrapper", str(schema_path))
    assert result is True


def test_validate_config_failure(config_dir):
    """Проверяем validate_config на невалидном конфиге."""
    schema_path = config_dir / "test_schema.json"
    schema = {
        "type": "object",
        "properties": {
            "must_be_int": {"type": "integer"}
        },
        "required": ["must_be_int"]
    }
    schema_path.write_text(json.dumps(schema), encoding="utf-8")

    config_manager.add_config("invalid_wrapper", {"must_be_int": "not_an_int"})

    with pytest.raises(ValueError, match="Validation failed"):
        config_manager.validate_config("invalid_wrapper", str(schema_path))
