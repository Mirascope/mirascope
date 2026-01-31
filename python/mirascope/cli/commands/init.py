"""Init command - Initialize Mirascope configuration."""

from __future__ import annotations

import json
from pathlib import Path


def run_init() -> int:
    """Initialize Mirascope configuration in the current project.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    config_path = Path.cwd() / "mirascope.json"

    if config_path.exists():
        print(f"Configuration already exists at {config_path}")
        return 0

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
        print("\nYou can now use `mirascope add <item>` to add registry items.")
    except OSError as e:
        print(f"Error: Failed to create config file: {e}")
        return 1

    return 0
