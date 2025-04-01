#!/usr/bin/env python3

import argparse
import sys
import json
import os

# Добавляем путь к корневой директории проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from utils.wrapman.src.common.base import get_wrap_names, get_fuzz_cmd, get_build_cmd, get_cov_cmd

def list_wrappers():
    """Prints a list of all available wrappers."""
    try:
        wrappers = get_wrap_names()

        if wrappers:
            print("\n".join(wrappers))
        else:
            print("No wrappers found.")
    except (FileNotFoundError, PermissionError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

def list_wrappers_json():
    """Prints details of all available wrappers, optionally in JSON format."""
    try:
        wrappers = get_wrap_names()

        if wrappers:
            print(json.dumps(wrappers))
        else:
            print("No wrappers found.")

    except (FileNotFoundError, PermissionError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

def print_fuzz_cmd(wrap_name):
    """Prints the fuzzing command for the specified wrapper."""
    try:
        cmd = get_fuzz_cmd(wrap_name)
        print(cmd)
    except KeyError:
        print(f"Error: Wrapper '{wrap_name}' not found or no fuzz command specified.", file=sys.stderr)
        sys.exit(1)
    except (FileNotFoundError, PermissionError, OSError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

def print_build_cmd(wrap_name):
    """Prints the build command for the specified wrapper."""
    try:
        cmd = get_build_cmd(wrap_name)
        print(cmd)
    except KeyError:
        print(f"Error: Wrapper '{wrap_name}' not found or no build command specified.", file=sys.stderr)
        sys.exit(1)
    except (FileNotFoundError, PermissionError, OSError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

def print_coverage_cmd(wrap_name):
    """Prints the coverage collection command for the specified wrapper."""
    try:
        cmd = get_cov_cmd(wrap_name)
        print(cmd)
    except KeyError:
        print(f"Error: Wrapper '{wrap_name}' not found or no coverage command specified.", file=sys.stderr)
        sys.exit(1)
    except (FileNotFoundError, PermissionError, OSError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="CLI utility for managing fuzzing wrappers")
    parser.add_argument("-l", "--list", action="store_true", help="List all available wrappers")
    parser.add_argument("--json", action="store_true", help="Output list in JSON format")
    parser.add_argument("-fcmd", metavar="NAME", help="Print the fuzzing command for the specified wrapper")
    parser.add_argument("-bcmd", metavar="NAME", help="Print the build command for the specified wrapper")
    parser.add_argument("-ccmd", metavar="NAME", help="Print the coverage collection command for the specified wrapper")

    args = parser.parse_args()

    if args.list:
        if args.json:
            list_wrappers_json()
        else:
            list_wrappers()
    elif args.fcmd:
        print_fuzz_cmd(args.fcmd)
    elif args.bcmd:
        print_build_cmd(args.bcmd)
    elif args.ccmd:
        print_coverage_cmd(args.ccmd)
    else:
        parser.print_help()
        sys.exit(0)

if __name__ == "__main__":
    main()
