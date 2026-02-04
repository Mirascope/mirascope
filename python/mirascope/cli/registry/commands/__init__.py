"""Registry commands for Mirascope CLI."""

from mirascope.cli.registry.commands.add import add_command
from mirascope.cli.registry.commands.init import init_command
from mirascope.cli.registry.commands.list import list_command

__all__ = ["add_command", "init_command", "list_command"]
