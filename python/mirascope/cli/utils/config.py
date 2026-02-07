"""Configuration management for the Mirascope CLI."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


def load_config() -> dict[str, Any] | None:
    """Load the Mirascope configuration from the current project.

    Looks for mirascope.json in the current directory.

    Returns:
        The configuration as a dictionary, or None if not found.
    """
    config_path = Path.cwd() / "mirascope.json"

    if config_path.exists():
        try:
            return json.loads(config_path.read_text())
        except (json.JSONDecodeError, OSError):
            return None

    return None


def get_project_info() -> dict[str, Any]:
    """Get project information from pyproject.toml.

    Returns:
        A dictionary with project information.
    """
    pyproject_path = Path.cwd() / "pyproject.toml"

    if not pyproject_path.exists() or tomllib is None:
        return {}

    try:
        content = pyproject_path.read_bytes()
        data = tomllib.loads(content.decode("utf-8"))
        return data.get("project", {})
    except OSError:
        return {}
    except Exception:  # noqa: BLE001
        # Catch tomllib.TOMLDecodeError or similar parsing errors
        return {}
