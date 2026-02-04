"""Registry CLI - Manage registry items."""

from __future__ import annotations

from typing import Annotated

import typer

from mirascope.cli.registry.commands import add_command, init_command, list_command

app = typer.Typer(
    name="registry",
    help="Manage registry items",
    no_args_is_help=True,
)

DEFAULT_REGISTRY = "https://mirascope.com/registry"


@app.command("add")
def add(
    items: Annotated[
        list[str], typer.Argument(help="Name(s) of the registry item(s) to add")
    ],
    path: Annotated[
        str | None,
        typer.Option("--path", "-p", help="Custom path to install the item(s)"),
    ] = None,
    overwrite: Annotated[
        bool, typer.Option("--overwrite", "-o", help="Overwrite existing files")
    ] = False,
    registry: Annotated[
        str, typer.Option("--registry", "-r", help="Registry URL to fetch items from")
    ] = DEFAULT_REGISTRY,
) -> None:
    """Add a registry item to your project."""
    add_command(items=items, path=path, overwrite=overwrite, registry_url=registry)


@app.command("list")
def list_(
    item_type: Annotated[
        str | None,
        typer.Option(
            "--type",
            "-t",
            help="Filter by item type (tool, agent, prompt, integration)",
        ),
    ] = None,
    registry: Annotated[
        str, typer.Option("--registry", "-r", help="Registry URL to list items from")
    ] = DEFAULT_REGISTRY,
) -> None:
    """List available registry items."""
    list_command(item_type=item_type, registry_url=registry)


@app.command("init")
def init() -> None:
    """Initialize Mirascope configuration in your project."""
    init_command()
