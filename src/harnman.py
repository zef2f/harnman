#!/usr/bin/env python3

import argparse
import sys
import json
import os

# Add path to project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.common.base import (
    get_harn_names,
    get_fuzz_cmd,
    get_build_cmd,
    get_cov_cmd,
)


def list_harnesses():
    """Prints a list of all available harnesses."""
    try:
        harnesses = get_harn_names()
        if harnesses:
            print("\n".join(harnesses))
        else:
            print("No harnesses found.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def list_harnesses_json():
    """Prints details of all available harnesses in JSON format."""
    try:
        harnesses = get_harn_names()
        print(json.dumps(harnesses))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def print_fuzz_cmd(harness_name):
    """Prints the fuzzing command for the specified harness."""
    try:
        cmd = get_fuzz_cmd(harness_name)
        print(cmd)
    except KeyError:
        print(
            f"Error: Harness '{harness_name}' not found or no fuzz command specified.",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def print_build_cmd(harness_name):
    """Prints the build command for the specified harness."""
    try:
        cmd = get_build_cmd(harness_name)
        print(cmd)
    except KeyError:
        print(
            f"Error: Harness '{harness_name}' not found or no build command specified.",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def print_coverage_cmd(harness_name):
    """Prints the coverage collection command for the specified harness."""
    try:
        cmd = get_cov_cmd(harness_name)
        print(cmd)
    except KeyError:
        print(
            f"Error: Harness '{harness_name}' not found or no coverage command specified.",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="CLI utility for managing fuzzing harnesses"
    )
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List all available harnesses",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output list in JSON format"
    )
    parser.add_argument(
        "-fcmd",
        metavar="NAME",
        help="Print the fuzzing command for the specified harness",
    )
    parser.add_argument(
        "-bcmd",
        metavar="NAME",
        help="Print the build command for the specified harness",
    )
    parser.add_argument(
        "-ccmd",
        metavar="NAME",
        help="Print the coverage collection command for the specified harness",
    )

    args = parser.parse_args()

    if args.list:
        if args.json:
            list_harnesses_json()
        else:
            list_harnesses()
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
