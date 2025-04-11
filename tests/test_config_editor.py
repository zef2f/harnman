import os
import json
import shutil
import pytest
from src.common import config_editor
import importlib


@pytest.fixture(scope="function")
def config_dir(tmp_path, monkeypatch):
    """
    Creates a temporary config/ directory, sets HARNMAN_CONFIG_DIR environment variable,
    reloads CONFIG_DIR in config_editor module and cleans up after tests.
    """
    config_path = tmp_path / "config"
    config_path.mkdir(parents=True, exist_ok=True)  # Create directory

    # Update environment variable
    monkeypatch.setenv("HARNMAN_CONFIG_DIR", str(config_path))

    # Reload config_editor to update CONFIG_DIR
    importlib.reload(config_editor)

    yield config_path  # Pass path to tests

    # Clean up directory after tests
    if config_path.exists():
        shutil.rmtree(config_path, ignore_errors=True)


def test_resolve_config_path_success(config_dir):
    """Tests correct path resolution for configuration file."""
    harness_name = "test_harness"
    expected_path = os.path.join(str(config_dir), f"{harness_name}.json")
    assert config_editor._resolve_config_path(harness_name) == expected_path


def test_resolve_config_path_no_dir(tmp_path, monkeypatch):
    """Tests error handling when configuration directory is missing."""
    nonexistent_dir = tmp_path / "nonexistent"
    monkeypatch.setenv("HARNMAN_CONFIG_DIR", str(nonexistent_dir))
    importlib.reload(config_editor)

    with pytest.raises(FileNotFoundError, match=f"Configuration directory '{nonexistent_dir}' not found"):
        config_editor._resolve_config_path("test_harness")


def test_load_config_data_success(config_dir):
    """Tests successful loading of configuration data."""
    config_name = "test_harness"
    test_data = {"test": "data"}
    
    config_path = config_dir / f"{config_name}.json"
    config_path.write_text(json.dumps(test_data), encoding="utf-8")

    loaded_data = config_editor._load_config_data(config_name)
    assert loaded_data == test_data


def test_load_config_data_file_not_found(config_dir):
    """Tests error handling when configuration file is missing."""
    with pytest.raises(FileNotFoundError, match="Config file .* not found"):
        config_editor._load_config_data("nonexistent_harness")


def test_load_config_data_invalid_json(config_dir):
    """Tests error handling for invalid JSON format."""
    config_name = "test_harness"
    config_path = config_dir / f"{config_name}.json"
    config_path.write_text("invalid json", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid JSON format"):
        config_editor._load_config_data(config_name)


def test_save_config_data_success(config_dir):
    """Tests successful saving of configuration data."""
    config_name = "test_harness"
    test_data = {"test": "data"}
    
    config_editor._save_config_data(config_name, test_data)
    
    config_path = config_dir / f"{config_name}.json"
    assert json.loads(config_path.read_text(encoding="utf-8")) == test_data


def test_read_config_field_success(config_dir):
    """Tests that read_config_field returns correct value."""
    config_name = "test_harness"
    initial_data = {"fuzz": {"options": {"max_runs": 100}}}

    config_path = config_dir / f"{config_name}.json"
    config_path.write_text(json.dumps(initial_data), encoding="utf-8")

    value = config_editor.read_config_field(config_name, "fuzz.options.max_runs")
    assert value == 100


def test_read_config_field_not_found(config_dir):
    """Tests that KeyError is raised when requested key doesn't exist."""
    config_name = "test_harness"
    initial_data = {"fuzz": {"options": {}}}

    config_path = config_dir / f"{config_name}.json"
    config_path.write_text(json.dumps(initial_data), encoding="utf-8")

    with pytest.raises(KeyError, match="Key 'fuzz.options.max_runs' not found"):
        config_editor.read_config_field(config_name, "fuzz.options.max_runs")


def test_read_config_field_invalid_path(config_dir):
    """Tests error handling for invalid field path."""
    config_name = "test_harness"
    initial_data = {"fuzz": "not_a_dict"}

    config_path = config_dir / f"{config_name}.json"
    config_path.write_text(json.dumps(initial_data), encoding="utf-8")

    with pytest.raises(KeyError, match=r"Key 'fuzz\.options\.max_runs' not found in 'test_harness\.json'"):
        config_editor.read_config_field(config_name, "fuzz.options.max_runs")


def test_update_config_field_new_field(config_dir):
    """Tests adding a new field to JSON."""
    config_name = "test_harness"
    initial_data = {"fuzz": {}}

    config_path = config_dir / f"{config_name}.json"
    config_path.write_text(json.dumps(initial_data), encoding="utf-8")

    result = config_editor.update_config_field(config_name, "fuzz.options.max_runs", 200)
    assert result is True

    with open(config_path, "r", encoding="utf-8") as f:
        updated_data = json.load(f)

    assert updated_data["fuzz"]["options"]["max_runs"] == 200


def test_update_config_field_existing_field(config_dir):
    """Tests updating an existing field in JSON."""
    config_name = "test_harness"
    initial_data = {"fuzz": {"options": {"max_runs": 100}}}

    config_path = config_dir / f"{config_name}.json"
    config_path.write_text(json.dumps(initial_data), encoding="utf-8")

    result = config_editor.update_config_field(config_name, "fuzz.options.max_runs", 300)
    assert result is True

    with open(config_path, "r", encoding="utf-8") as f:
        updated_data = json.load(f)

    assert updated_data["fuzz"]["options"]["max_runs"] == 300


def test_update_config_field_nested_creation(config_dir):
    """Tests creation of nested structure during update."""
    config_name = "test_harness"
    initial_data = {}

    config_path = config_dir / f"{config_name}.json"
    config_path.write_text(json.dumps(initial_data), encoding="utf-8")

    result = config_editor.update_config_field(config_name, "fuzz.options.depth.level", "deep_value")
    assert result is True

    with open(config_path, "r", encoding="utf-8") as f:
        updated_data = json.load(f)

    assert updated_data["fuzz"]["options"]["depth"]["level"] == "deep_value"


def test_update_config_field_overwrite_non_dict(config_dir):
    """Tests overwriting non-dictionary with dictionary during update."""
    config_name = "test_harness"
    initial_data = {"fuzz": "not_a_dict"}

    config_path = config_dir / f"{config_name}.json"
    config_path.write_text(json.dumps(initial_data), encoding="utf-8")

    result = config_editor.update_config_field(config_name, "fuzz.options.max_runs", 100)
    assert result is True

    with open(config_path, "r", encoding="utf-8") as f:
        updated_data = json.load(f)

    assert updated_data["fuzz"]["options"]["max_runs"] == 100


def test_delete_config_field_success(config_dir):
    """Tests successful deletion of an existing field."""
    config_name = "test_harness"
    initial_data = {"fuzz": {"options": {"max_runs": 100}}}

    config_path = config_dir / f"{config_name}.json"
    config_path.write_text(json.dumps(initial_data), encoding="utf-8")

    result = config_editor.delete_config_field(config_name, "fuzz.options.max_runs")
    assert result is True

    with open(config_path, "r", encoding="utf-8") as f:
        updated_data = json.load(f)

    assert "max_runs" not in updated_data["fuzz"]["options"]


def test_delete_config_field_not_found(config_dir):
    """Tests that attempting to delete non-existent field raises KeyError."""
    config_name = "test_harness"
    initial_data = {"fuzz": {"options": {}}}

    config_path = config_dir / f"{config_name}.json"
    config_path.write_text(json.dumps(initial_data), encoding="utf-8")

    with pytest.raises(KeyError, match="Key 'fuzz.options.max_runs' not found"):
        config_editor.delete_config_field(config_name, "fuzz.options.max_runs")


def test_delete_config_field_invalid_path(config_dir):
    """Tests error handling when attempting to delete field with invalid path."""
    config_name = "test_harness"
    initial_data = {"fuzz": "not_a_dict"}

    config_path = config_dir / f"{config_name}.json"
    config_path.write_text(json.dumps(initial_data), encoding="utf-8")

    with pytest.raises(KeyError, match="Key 'fuzz.options.max_runs' not found"):
        config_editor.delete_config_field(config_name, "fuzz.options.max_runs")
