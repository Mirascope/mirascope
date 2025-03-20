#!/usr/bin/env python
"""
Script to run a faster version of mkdocs serve for local documentation development.
This creates a temporary modified mkdocs config that disables slow plugins.
"""

import os
import re
import subprocess
from pathlib import Path

# Define paths
root_dir = Path(__file__).parent.parent
original_file = root_dir / "mkdocs.yml"
dev_config_file = root_dir / "mkdocs.dev.yml"


def comment_out_plugin(lines: list[str], plugin_name: str) -> list[str]:
    """Comment out a plugin and its configuration block in the mkdocs.yml file."""
    # We process the mkdocs.yml file line-by-line rather than trying to parse the YAML
    # because mkdocs.yml is difficult to parse correctly.
    in_plugin_block = False
    modified_lines = lines.copy()

    for i, line in enumerate(modified_lines):
        stripped_line = line.strip()
        if stripped_line.startswith("-") and plugin_name in stripped_line:
            in_plugin_block = True
            modified_lines[i] = f"# {line}"
        elif in_plugin_block:
            if stripped_line.startswith("-") or not stripped_line:
                in_plugin_block = False
            else:
                modified_lines[i] = f"# {line}"

    return modified_lines


def main() -> None:
    print("📚 Setting up fast documentation development server...")  # noqa: T201

    # Read the original mkdocs.yml
    with open(original_file) as f:
        lines = f.readlines()

    # Comment out slow plugins
    lines = comment_out_plugin(lines, "social")
    lines = comment_out_plugin(lines, "mkdocs-jupyter")

    # Set strict to false for faster builds
    content = "".join(lines)
    if "strict:" in content:
        content = re.sub(r"strict:\s*true", "strict: false", content)
    else:
        # If strict isn't found, raise a helpful error
        raise ValueError(
            "Could not find 'strict:' setting in mkdocs.yml. "
            "Please ensure mkdocs.yml contains this setting."
        )

    # Write the modified configuration to mkdocs.dev.yml
    with open(dev_config_file, "w") as f:
        f.write(content)

    print("📝 Created development config at mkdocs.dev.yml")  # noqa: T201
    print("🚀 Starting mkdocs development server with fast configuration...")  # noqa: T201

    # Run mkdocs serve with the development config
    try:
        subprocess.run(["mkdocs", "serve", "-f", str(dev_config_file)])
    except KeyboardInterrupt:
        print("\n🛑 Development server stopped")  # noqa: T201
    finally:
        # Clean up the temporary file
        if dev_config_file.exists():
            os.remove(dev_config_file)
            print("🧹 Removed temporary config file")  # noqa: T201


if __name__ == "__main__":
    main()
