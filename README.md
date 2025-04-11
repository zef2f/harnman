# Harnman

A command-line utility for managing fuzzing harness configurations.

## Overview

Harnman (Harness Manager) is a Python-based tool that helps manage JSON configuration files for fuzzing harnesses. It provides a simple interface for viewing and manipulating harness configurations, including build, fuzzing, and coverage collection commands.

## Features

- List available fuzzing harnesses
- View and modify harness configurations
- Get build commands for harnesses
- Get fuzzing commands for harnesses
- Get coverage collection commands for harnesses
- JSON output support for automation

## Usage

```bash
# List all available harnesses
harnman -l

# List harnesses in JSON format
harnman --json

# Get fuzzing command for a specific harness
harnman -fcmd HARNESS_NAME

# Get build command for a specific harness
harnman -bcmd HARNESS_NAME

# Get coverage collection command for a specific harness
harnman -ccmd HARNESS_NAME
```

## Configuration

Harness configurations are stored as JSON files in the directory specified by the `HARNMAN_CONFIG_DIR` environment variable.

Each configuration file should follow this basic structure:
```json
{
    "fuzz": {
        "fuzz_cmd": "...",
        ...
    },
    "build": {
        "build_cmd": "...",
        ...
    },
    "coverage": {
        "coverage_cmd": "...",
        ...
    }
}
```

## Requirements

- Python 3.6 or higher
- Environment variable `HARNMAN_CONFIG_DIR` set to the configuration directory path
