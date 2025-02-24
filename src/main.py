import argparse
import sys

class config:
    @staticmethod
    def print_arg(args):
        print("[DEBUG] Called config.print_arg() with args:", args)

class flow:
    @staticmethod
    def print_arg(args):
        print("[DEBUG] Called cjnfig.print_arg() with args:", args)

def main():
    parser = argparse.ArgumentParser(
        prog="whelp",
    )

    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    config_parser = subparsers.add_parser(
        "config"
    )

    scan_parser = subparsers.add_parser(
        "flow"
    )

    args = parser.parse_args()

    if args.command == "config":
        config.print_arg(args)
    elif args.command == "flow":
        config.print_arg(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
