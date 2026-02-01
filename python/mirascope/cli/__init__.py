"""Mirascope CLI - Command-line interface for the Mirascope registry."""

from __future__ import annotations

import argparse
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    """Main entry point for the Mirascope CLI."""
    parser = argparse.ArgumentParser(
        prog="mirascope",
        description="Mirascope CLI - Install registry items into your project",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    add_parser = subparsers.add_parser(
        "add",
        help="Add a registry item to your project",
    )
    add_parser.add_argument(
        "items",
        nargs="+",
        help="Name(s) of the registry item(s) to add",
    )
    add_parser.add_argument(
        "--path",
        "-p",
        type=str,
        default=None,
        help="Custom path to install the item(s)",
    )
    add_parser.add_argument(
        "--overwrite",
        "-o",
        action="store_true",
        help="Overwrite existing files",
    )
    add_parser.add_argument(
        "--registry",
        "-r",
        type=str,
        default="https://mirascope.com/registry",
        help="Registry URL to fetch items from",
    )

    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List available registry items",
    )
    list_parser.add_argument(
        "--type",
        "-t",
        type=str,
        default=None,
        help="Filter by item type (tool, agent, prompt, integration)",
    )
    list_parser.add_argument(
        "--registry",
        "-r",
        type=str,
        default="https://mirascope.com/registry",
        help="Registry URL to list items from",
    )

    # Init command
    subparsers.add_parser(
        "init",
        help="Initialize Mirascope configuration in your project",
    )

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "add":
        from mirascope.cli.commands.add import run_add

        return run_add(
            items=args.items,
            path=args.path,
            overwrite=args.overwrite,
            registry_url=args.registry,
        )
    elif args.command == "list":
        from mirascope.cli.commands.list import run_list

        return run_list(
            item_type=args.type,
            registry_url=args.registry,
        )
    elif args.command == "init":
        from mirascope.cli.commands.init import run_init

        return run_init()

    return 0


if __name__ == "__main__":
    sys.exit(main())
