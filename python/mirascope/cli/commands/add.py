"""Add command - Install registry items into a project."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from collections.abc import Sequence


def _load_local_item(item_path: str) -> dict[str, Any] | None:
    """Load a registry item from a local file path.

    Args:
        item_path: Path to a local JSON file.

    Returns:
        The registry item as a dictionary, or None if not found.
    """
    path = Path(item_path)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def run_add(
    items: Sequence[str],
    path: str | None,
    overwrite: bool,
    registry_url: str,
) -> int:
    """Add registry items to the current project.

    Args:
        items: Names of the registry items to add.
        path: Custom path to install the items.
        overwrite: Whether to overwrite existing files.
        registry_url: URL of the registry to fetch items from.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    from mirascope.cli.registry.client import RegistryClient
    from mirascope.cli.utils.config import load_config
    from mirascope.cli.utils.file_ops import write_file

    # Load project config if it exists
    config = load_config()
    base_path = Path(path) if path else Path.cwd()

    client = RegistryClient(registry_url)

    all_dependencies: dict[str, list[str]] = {"pip": [], "npm": []}
    files_written: list[str] = []

    for item_name in items:
        print(f"Adding {item_name}...")

        item: dict[str, Any] | None = None

        # Check if it's a local file path (starts with ./ or / or ends with .json)
        if (
            item_name.startswith("./")
            or item_name.startswith("/")
            or item_name.endswith(".json")
        ):
            item = _load_local_item(item_name)
            if item is None:
                print(f"Error: Local file '{item_name}' not found.", file=sys.stderr)
                return 1
        else:
            # Fetch from registry
            try:
                item = client.fetch_item(item_name, language="python")
            except Exception as e:
                print(f"Error: Failed to fetch '{item_name}': {e}", file=sys.stderr)
                return 1

            if item is None:
                print(
                    f"Error: Item '{item_name}' not found in registry.",
                    file=sys.stderr,
                )
                return 1

        # Write each file from the registry item
        for file_info in item.get("files", []):
            target = file_info.get("target", file_info.get("path", ""))
            content = file_info.get("content", "")

            # Determine the target path
            if config:
                # Use configured paths based on item type
                item_type = str(item.get("type", "")).replace("registry:", "")
                paths_config = config.get("paths")
                type_key = f"{item_type}s"
                type_path_value = ""
                if isinstance(paths_config, dict) and type_key in paths_config:
                    path_value = cast(Any, paths_config[type_key])
                    if isinstance(path_value, str):
                        type_path_value = path_value
                if type_path_value:
                    # Replace the first directory component with the configured path
                    target_parts = Path(target).parts
                    if len(target_parts) > 1:
                        target = str(Path(type_path_value) / Path(*target_parts[1:]))
                    elif target_parts:
                        target = str(Path(type_path_value) / target_parts[0])

            target_path = base_path / target

            # Check if file exists
            if target_path.exists() and not overwrite:
                print(
                    f"Warning: {target_path} already exists. Use --overwrite to replace.",
                    file=sys.stderr,
                )
                continue

            # Write the file
            try:
                write_file(target_path, content)
                files_written.append(str(target_path))
                print(f"  Created {target_path}")
            except Exception as e:
                print(f"Error: Failed to write {target_path}: {e}", file=sys.stderr)
                return 1

        # Collect dependencies
        deps = item.get("dependencies", {})
        for pip_dep in deps.get("pip", []):
            if pip_dep not in all_dependencies["pip"]:
                all_dependencies["pip"].append(pip_dep)
        for npm_dep in deps.get("npm", []):
            if npm_dep not in all_dependencies["npm"]:
                all_dependencies["npm"].append(npm_dep)

    # Print summary
    if files_written:
        print(f"\nSuccessfully added {len(files_written)} file(s).")

    # Print dependencies to install
    if all_dependencies["pip"]:
        print("\nInstall required Python dependencies:")
        print(f"  uv add {' '.join(all_dependencies['pip'])}")

    return 0
