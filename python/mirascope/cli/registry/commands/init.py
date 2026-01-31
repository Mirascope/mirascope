"""Init command - Initialize Mirascope configuration."""

from __future__ import annotations

import json
from pathlib import Path

import typer


def init_command() -> None:
    """Initialize Mirascope configuration in the current project."""
    config_path = Path.cwd() / "mirascope.json"

    if config_path.exists():
        print(f"Configuration already exists at {config_path}")
        return

    config: dict[str, str | dict[str, str]] = {
        "$schema": "https://mirascope.com/registry/schema/config.json",
        "language": "python",
        "registry": "https://mirascope.com/registry",
        "paths": {
            "tools": "ai/tools",
            "agents": "ai/agents",
            "prompts": "ai/prompts",
            "integrations": "ai/integrations",
        },
    }

    try:
        config_path.write_text(json.dumps(config, indent=2) + "\n")
        print(f"Created {config_path}")
        print(
            "\nYou can now use `mirascope registry add <item>` to add registry items."
        )
    except OSError as e:
        typer.echo(f"Error: Failed to create config file: {e}", err=True)
        raise typer.Exit(1)
