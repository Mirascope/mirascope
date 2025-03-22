"""Utils for the CLI commands."""

import json
import os
from typing import Any


def get_and_create_config(config_path: str) -> dict[str, Any]:
    """Get the configuration data and create the config file if it doesn't exist."""
    if not os.path.exists(".lilypad"):
        os.mkdir(".lilypad")
    data = {}
    try:
        with open(config_path) as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(config_path, "w") as f:
            json.dump(data, f)
    return data
