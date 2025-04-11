import os
import json
import shutil
import pytest
from jsonschema import ValidationError
from src.common import config_manager


@pytest.fixture(scope="function")
def config_dir(tmp_path, monkeypatch):
    """
    Creates a temporary config/ directory, overrides HARNMAN_CONFIG_DIR,
    recreates CONFIG_DIR in the config_manager module and deletes after tests.
    """
    config_path = tmp_path / "config"
    config_path.mkdir(parents=True, exist_ok=True)  # Creates directory

    # Updates environment variable
    monkeypatch.setenv("HARNMAN_CONFIG_DIR", str(config_path))

    # Reloads `config_manager`, so it updates CONFIG_DIR
    import importlib
    importlib.reload(config_manager)

    yield config_path  # Passes test path to tests

    # Deletes directory after tests
    if config_path.exists():
        shutil.rmtree(config_path, ignore_errors=True)


def test_add_config_success(config_dir):
    """Tests that we can successfully create a new config."""
    data = {"foo": "bar"}
    result = config_manager.add_config("test_harness", data)
    assert result is True

    config_path = config_dir / "test_harness.json"
    assert config_path.exists()

    with open(config_path, "r", encoding="utf-8") as f:
        content = json.load(f)
    assert content == data


def test_add_config_already_exists(config_dir):
    """If config already exists, add_config should raise FileExistsError."""
    config_manager.add_config("duplicate_harness", {"key": 123})

    with pytest.raises(FileExistsError):
        config_manager.add_config("duplicate_harness", {"foo": "bar"})


def test_delete_config_success(config_dir):
    """Tests deleting an existing file."""
    config_manager.add_config("removable_harness", {"need": "to_delete"})
    config_path = config_dir / "removable_harness.json"
    assert config_path.exists()

    result = config_manager.delete_config("removable_harness")
    assert result is True
    assert not config_path.exists()


def test_delete_config_not_found(config_dir):
    """If deleting a non-existent file, raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        config_manager.delete_config("nonexistent")


def test_rename_config_success(config_dir):
    """Tests successful renaming."""
    config_manager.add_config("old_harness", {"old": "data"})
    old_path = config_dir / "old_harness.json"
    new_path = config_dir / "new_harness.json"

    assert old_path.exists()
    assert not new_path.exists()

    result = config_manager.rename_config("old_harness", "new_harness")
    assert result is True
    assert not old_path.exists()
    assert new_path.exists()

    with open(new_path, "r", encoding="utf-8") as f:
        content = json.load(f)
    assert content == {"old": "data"}


def test_rename_config_same_name(config_dir):
    """If names are the same, rename_config simply returns True and does nothing."""
    config_manager.add_config("same_harness", {"key": 1})
    old_path = config_dir / "same_harness.json"

    result = config_manager.rename_config("same_harness", "same_harness")
    assert result is True
    assert old_path.exists()


def test_rename_config_not_found(config_dir):
    """If old file is not found, raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        config_manager.rename_config("no_such_harness", "does_not_matter")


def test_rename_config_new_already_exists(config_dir):
    """If new file already exists, raises FileExistsError."""
    config_manager.add_config("old_harness", {"data": 123})
    config_manager.add_config("already_exists", {"foo": "bar"})

    with pytest.raises(FileExistsError):
        config_manager.rename_config("old_harness", "already_exists")


def test_list_config(config_dir):
    """Tests that list_config gives a list without .json."""
    config_manager.add_config("first", {"a": 1})
    config_manager.add_config("second", {"b": 2})
    config_manager.add_config("third", {"c": 3})

    result = config_manager.list_config()
    assert set(result) == {"first", "second", "third"}


def test_read_config_success(config_dir):
    """Tests that read_config returns JSON content."""
    data = {"alpha": 100, "beta": 200}
    config_manager.add_config("reader_harness", data)

    read_data = config_manager.read_config("reader_harness")
    assert read_data == data


def test_read_config_not_found(config_dir):
    """If file is not found, should be FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        config_manager.read_config("missing_harness")


def test_read_config_invalid_json(config_dir):
    """Tests error handling for invalid JSON format."""
    bad_config = config_dir / "bad_harness.json"
    bad_config.write_text('{"invalid": ???}', encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid JSON format"):
        config_manager.read_config("bad_harness")


def test_validate_config_success(config_dir):
    """Tests validate_config with valid configuration."""
    schema_path = config_dir / "test_schema.json"
    schema = {
        "type": "object",
        "properties": {
            "foo": {"type": "string"}
        },
        "required": ["foo"]
    }
    schema_path.write_text(json.dumps(schema), encoding="utf-8")

    config_manager.add_config("valid_harness", {"foo": "hello"})

    result = config_manager.validate_config("valid_harness", str(schema_path))
    assert result is True


def test_validate_config_failure(config_dir):
    """Tests validate_config with invalid configuration."""
    schema_path = config_dir / "test_schema.json"
    schema = {
        "type": "object",
        "properties": {
            "must_be_int": {"type": "integer"}
        },
        "required": ["must_be_int"]
    }
    schema_path.write_text(json.dumps(schema), encoding="utf-8")

    config_manager.add_config("invalid_harness", {"must_be_int": "not_an_int"})

    with pytest.raises(ValueError, match="Validation failed"):
        config_manager.validate_config("invalid_harness", str(schema_path))


def test_add_config_invalid_data_type(config_dir):
    """Tests that add_config raises TypeError when data is not a dictionary."""
    invalid_data = ["not", "a", "dict"]
    with pytest.raises(TypeError, match="Parameter 'data' must be a dictionary"):
        config_manager.add_config("test_harness", invalid_data)


def test_add_config_invalid_filename(config_dir):
    """Tests handling of invalid characters in filename."""
    invalid_names = [
        "../invalid_path",
        "invalid/path",
        "invalid\\path",
        "",
        " ",
    ]
    for name in invalid_names:
        with pytest.raises(ValueError, match=r"Invalid harness name:.*Use only letters, numbers, underscore and hyphen"):
            config_manager.add_config(name, {"key": "value"})


def test_list_config_with_non_json_files(config_dir):
    """Tests that list_config ignores non-JSON files."""
    # Create JSON file
    config_manager.add_config("valid_config", {"key": "value"})
    
    # Create non-JSON files
    (config_dir / "not_json.txt").write_text("hello")
    (config_dir / "also_not.json.bak").write_text("{}")
    
    result = config_manager.list_config()
    assert result == ["valid_config"]


def test_list_config_with_subdirs(config_dir):
    """Tests that list_config works correctly with subdirectories."""
    # Create JSON file
    config_manager.add_config("valid_config", {"key": "value"})
    
    # Create subdirectory
    subdir = config_dir / "subdir"
    subdir.mkdir()
    (subdir / "config.json").write_text("{}")
    
    result = config_manager.list_config()
    assert result == ["valid_config"]


def test_validate_config_invalid_schema(config_dir):
    """Tests validate_config with invalid schema."""
    # Create test config
    config_manager.add_config("test_harness", {"foo": "bar"})
    
    # Create invalid schema
    schema_path = config_dir / "invalid_schema.json"
    schema_path.write_text('{"type": "invalid_type"}', encoding="utf-8")
    
    with pytest.raises(ValueError, match="Schema is invalid"):
        config_manager.validate_config("test_harness", str(schema_path))


def test_validate_config_schema_not_found(config_dir):
    """Tests validate_config when schema file is not found."""
    config_manager.add_config("test_harness", {"foo": "bar"})
    
    with pytest.raises(FileNotFoundError):
        config_manager.validate_config("test_harness", "nonexistent_schema.json")


def test_validate_config_various_errors(config_dir):
    """Tests various validation error cases."""
    # Create schema with different constraints
    schema = {
        "type": "object",
        "properties": {
            "number": {"type": "integer", "minimum": 0},
            "string": {"type": "string", "pattern": "^[A-Z]+$"},
            "required_field": {"type": "string"}
        },
        "required": ["required_field"]
    }
    schema_path = config_dir / "test_schema.json"
    schema_path.write_text(json.dumps(schema), encoding="utf-8")
    
    # Test 1: missing required field
    config_manager.add_config("missing_required", {"number": 42})
    with pytest.raises(ValueError, match="Validation failed"):
        config_manager.validate_config("missing_required", str(schema_path))
    
    # Test 2: wrong data type
    config_manager.add_config("wrong_type", {"number": "not_a_number", "required_field": "ok"})
    with pytest.raises(ValueError, match="Validation failed"):
        config_manager.validate_config("wrong_type", str(schema_path))
    
    # Test 3: pattern violation
    config_manager.add_config("invalid_pattern", {"string": "lowercase", "required_field": "ok"})
    with pytest.raises(ValueError, match="Validation failed"):
        config_manager.validate_config("invalid_pattern", str(schema_path))
    
    # Test 4: minimum value violation
    config_manager.add_config("invalid_minimum", {"number": -1, "required_field": "ok"})
    with pytest.raises(ValueError, match="Validation failed"):
        config_manager.validate_config("invalid_minimum", str(schema_path))


def test_validate_config_invalid_harness_name(config_dir):
    """Tests validate_config with invalid harness name."""
    invalid_names = [
        "../path",
        "invalid/path",
        "invalid\\path",
        "",
        " ",
        "имя_по_русски",
        "name with spaces",
        "name.with.dots"
    ]
    
    schema_path = config_dir / "schema.json"
    schema_path.write_text('{"type": "object"}', encoding="utf-8")
    
    for name in invalid_names:
        with pytest.raises(ValueError, match="Invalid harness name"):
            config_manager.validate_config(name, str(schema_path))


def test_validate_config_detailed_error_message(config_dir):
    """Tests that validation error messages include path to problematic field."""
    # Create schema with nested objects
    schema = {
        "type": "object",
        "properties": {
            "nested": {
                "type": "object",
                "properties": {
                    "array": {
                        "type": "array",
                        "items": {"type": "integer"}
                    }
                }
            }
        }
    }
    schema_path = config_dir / "nested_schema.json"
    schema_path.write_text(json.dumps(schema), encoding="utf-8")
    
    # Create config with error in nested field
    config_manager.add_config("nested_config", {
        "nested": {
            "array": [1, "not an integer", 3]
        }
    })
    
    with pytest.raises(ValueError, match=r"at 'nested -> array -> 1'"):
        config_manager.validate_config("nested_config", str(schema_path))


def test_list_config_filters_invalid_names(config_dir):
    """Tests that list_config filters files with invalid names."""
    # Create valid config
    config_manager.add_config("valid_name", {"key": "value"})
    
    # Create files with invalid names (directly, as add_config won't accept them)
    invalid_files = [
        "name.with.dots.json",
        "name with spaces.json",
        "имя_по_русски.json",
        ".hidden.json",
        "..invalid.json",
        "invalid/path.json"
    ]
    
    for filename in invalid_files:
        try:
            (config_dir / filename).write_text("{}", encoding="utf-8")
        except OSError:
            continue  # Skip if we can't create file with such name
    
    result = config_manager.list_config()
    assert result == ["valid_name"]
