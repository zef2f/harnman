import os
import json
import shutil
import pytest
from src.common import config_editor


@pytest.fixture(scope="function")
def config_dir(tmp_path, monkeypatch):
    """
    Создаёт временную директорию config/, подменяет WRAPMAN_CONFIG_DIR,
    пересоздаёт CONFIG_DIR в модуле config_editor и удаляет после тестов.
    """
    config_path = tmp_path / "config"
    config_path.mkdir(parents=True, exist_ok=True)  # Создаём директорию

    # Обновляем переменную окружения
    monkeypatch.setenv("WRAPMAN_CONFIG_DIR", str(config_path))

    # Перегружаем `config_editor`, чтобы он обновил CONFIG_DIR
    import importlib
    importlib.reload(config_editor)

    yield config_path  # Передаём путь тестам

    # Удаляем директорию после тестов
    if config_path.exists():
        shutil.rmtree(config_path, ignore_errors=True)


def test_read_config_field_success(config_dir):
    """Проверяем, что read_config_field возвращает корректное значение."""
    config_name = "test_wrapper"
    initial_data = {"fuzz": {"options": {"max_runs": 100}}}

    config_path = config_dir / f"{config_name}.json"
    config_path.write_text(json.dumps(initial_data), encoding="utf-8")

    value = config_editor.read_config_field(config_name, "fuzz.options.max_runs")
    assert value == 100


def test_read_config_field_not_found(config_dir):
    """Если запрашиваемого ключа нет, должно выбрасываться KeyError."""
    config_name = "test_wrapper"
    initial_data = {"fuzz": {"options": {}}}

    config_path = config_dir / f"{config_name}.json"
    config_path.write_text(json.dumps(initial_data), encoding="utf-8")

    with pytest.raises(KeyError, match="Key 'fuzz.options.max_runs' not found"):
        config_editor.read_config_field(config_name, "fuzz.options.max_runs")


def test_update_config_field_new_field(config_dir):
    """Добавление нового поля в JSON."""
    config_name = "test_wrapper"
    initial_data = {"fuzz": {}}

    config_path = config_dir / f"{config_name}.json"
    config_path.write_text(json.dumps(initial_data), encoding="utf-8")

    result = config_editor.update_config_field(config_name, "fuzz.options.max_runs", 200)
    assert result is True

    with open(config_path, "r", encoding="utf-8") as f:
        updated_data = json.load(f)

    assert updated_data["fuzz"]["options"]["max_runs"] == 200


def test_update_config_field_existing_field(config_dir):
    """Обновление уже существующего поля в JSON."""
    config_name = "test_wrapper"
    initial_data = {"fuzz": {"options": {"max_runs": 100}}}

    config_path = config_dir / f"{config_name}.json"
    config_path.write_text(json.dumps(initial_data), encoding="utf-8")

    result = config_editor.update_config_field(config_name, "fuzz.options.max_runs", 300)
    assert result is True

    with open(config_path, "r", encoding="utf-8") as f:
        updated_data = json.load(f)

    assert updated_data["fuzz"]["options"]["max_runs"] == 300


def test_delete_config_field_success(config_dir):
    """Удаление существующего поля."""
    config_name = "test_wrapper"
    initial_data = {"fuzz": {"options": {"max_runs": 100}}}

    config_path = config_dir / f"{config_name}.json"
    config_path.write_text(json.dumps(initial_data), encoding="utf-8")

    result = config_editor.delete_config_field(config_name, "fuzz.options.max_runs")
    assert result is True

    with open(config_path, "r", encoding="utf-8") as f:
        updated_data = json.load(f)

    assert "max_runs" not in updated_data["fuzz"]["options"]


def test_delete_config_field_not_found(config_dir):
    """Попытка удалить несуществующее поле должна вызвать KeyError."""
    config_name = "test_wrapper"
    initial_data = {"fuzz": {"options": {}}}

    config_path = config_dir / f"{config_name}.json"
    config_path.write_text(json.dumps(initial_data), encoding="utf-8")

    with pytest.raises(KeyError, match="Key 'fuzz.options.max_runs' not found"):
        config_editor.delete_config_field(config_name, "fuzz.options.max_runs")


def test_update_config_field_nested_creation(config_dir):
    """Создание вложенной структуры при обновлении."""
    config_name = "test_wrapper"
    initial_data = {}

    config_path = config_dir / f"{config_name}.json"
    config_path.write_text(json.dumps(initial_data), encoding="utf-8")

    result = config_editor.update_config_field(config_name, "fuzz.options.depth.level", "deep_value")
    assert result is True

    with open(config_path, "r", encoding="utf-8") as f:
        updated_data = json.load(f)

    assert updated_data["fuzz"]["options"]["depth"]["level"] == "deep_value"
