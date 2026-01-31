"""File operations for the Mirascope CLI."""

from __future__ import annotations

from pathlib import Path


def write_file(path: Path, content: str) -> None:
    """Write content to a file, creating directories if needed.

    Args:
        path: Path to write to.
        content: Content to write.
    """
    # Create parent directories if they don't exist
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write the file
    path.write_text(content)


def ensure_directory(path: Path) -> None:
    """Ensure a directory exists.

    Args:
        path: Directory path to ensure exists.
    """
    path.mkdir(parents=True, exist_ok=True)
