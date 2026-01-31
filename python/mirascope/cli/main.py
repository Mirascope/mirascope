"""Mirascope CLI - Command-line interface."""

from __future__ import annotations

from typing import Annotated

import typer

from mirascope.cli.registry.app import app as registry_app

app = typer.Typer(
    name="mirascope",
    help="Mirascope CLI",
    no_args_is_help=True,
)

app.add_typer(registry_app, name="registry")


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        print("mirascope 2.1.1")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show version number",
        ),
    ] = False,
) -> None:
    """Mirascope CLI."""


if __name__ == "__main__":
    app()
