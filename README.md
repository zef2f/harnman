# Wrapman: CLI Utility for Fuzzing Wrappers Management

Wrapman is a CLI utility designed to manage various fuzzing wrappers. It eliminates the need to manually include compilation flags and fuzzing execution flags in scripts. Instead, all flags and commands for a wrapper `<wrapper>.c` are stored in the directory `WRAPMAN_CONFIG_DIR/<wrapper>.json`. Wrapman reads these JSON configuration files and extracts useful information, which is then passed to scripts that handle the wrappers.

## Requirements
- **Python 3.7+**
- **Module** `python3-module-jsonschema` for JSON file validation

## Project Structure
- `src/wrapman.py` → Main CLI executable file.
- `base.py` → Contains high-level methods for retrieving build, fuzz, and coverage commands for the basic Genesis JSON schema. This schema is universal and should be compatible with many fuzzers.
- `config_editor.py`, `config_manager.py` → Handle low-level reading and writing of JSON configurations.
- `schemas/` → JSON schemas for configuration validation.
  - Currently, a universal Genesis schema is used, which is quite basic. In the future, each fuzzer will have its own schema inherited from the Genesis schema, allowing for more flexible flag and command customization.

## Usage
Ensure that the environment variable `WRAPMAN_CONFIG_DIR` (or `config/` by default) contains the necessary JSON files.

### Options
```sh
wrapman -h
```
Displays a list of supported options:
- `-l, --list` — Show a list of available wrappers.
- `-fcmd` — Get the fuzzing command.
- `-bcmd` — Get the build command.
- `-ccmd` — Get the coverage command.

### Commands
```sh
wrapman -l
```
Displays all wrappers described in `config/`.

```sh
wrapman -bcmd array_array
```
Outputs the command used to compile the `array_array` project (e.g., `clang -fsanitize=... ...`).

```sh
wrapman -fcmd tar
```
Returns the fuzzing execution command, e.g., `-max_total_time=30 ...`.

```sh
wrapman -ccmd datetime_fromisoformat
```
Outputs the command for coverage collection (e.g., `echo 'Coverage step not implemented'`).

## Basic JSON Configuration Format for the Genesis Schema
Each wrapper is described in a JSON file in the following format:

```json
{
  "wrapper_id": "1001",
  "fuzzer": {
    "name": "libfuzzer"
  },
  "metadata": {
    "name": "array_array",
    "description": "Fuzzes array_array logic..."
  },
  "build": {
    "build_cmd": "clang -fsanitize=fuzzer,address ..."
  },
  "fuzz": {
    "fuzz_cmd": "-artifact_prefix=... -reload=..."
  },
  "coverage": {
    "coverage_cmd": "echo 'Coverage step not implemented'"
  }
}
```

### Explanation of Fields
- **wrapper_id** → Unique ID
- **fuzzer** → Property `name` (e.g., libFuzzer, AFL, etc.)
- **metadata** → Includes `name` and `description`
- **build_cmd** → Build command
- **fuzz_cmd** → Fuzzing execution command
- **coverage_cmd** → Coverage collection command

