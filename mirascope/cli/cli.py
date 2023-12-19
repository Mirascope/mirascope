"""The Mirascope CLI prompt management tool."""
import argparse

from .commands import add, init, status, use


def main():
    """The runner for Mirascope CLI tool"""
    parser = argparse.ArgumentParser(description="Mirascope CLI Tool")

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    # Adding 'add' command
    parser_add = subparsers.add_parser("add", help="Add an item")
    parser_add.add_argument("file", help="File to add, without extension (.py)")
    parser_add.set_defaults(func=add)

    # Adding 'status' command
    parser_status = subparsers.add_parser("status", help="Check status of prompts")
    parser_status.add_argument(
        "file", nargs="?", default=None, help="Prompt to check status on"
    )
    parser_status.set_defaults(func=status)

    # Adding 'use' command
    parser_use = subparsers.add_parser("use", help="Use a prompt")
    parser_use.add_argument("prompt_directory", help="Prompt directory to use")
    parser_use.add_argument("version", help="Version of prompt to use")
    parser_use.set_defaults(func=use)

    # Adding 'init' command
    parser_init = subparsers.add_parser("init", help="Initialize mirascope project")
    parser_init.add_argument("directory", help="Main mirascope directory")
    parser_init.set_defaults(func=init)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
