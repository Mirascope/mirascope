"""Main CLI entrypoint for Lilypad."""

import importlib.metadata

from rich import print
from typer import Typer

from .commands import stubs_command

app = Typer()

app.command(name="version", help="Show the Lilypad version.")(
    lambda: print(importlib.metadata.version("python-lilypad"))
)
app.command(
    "stubs",
    help="Scan the specified module directory and generate stub files for version assignments.",
)(stubs_command)
