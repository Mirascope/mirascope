"""Scripts for development tasks."""

import os
import shutil
import subprocess
import sys


def check_bun() -> None:
    """Check if bun is installed and available in PATH."""
    if not shutil.which("bun"):
        print("Error: bun is not installed or not in PATH")
        print("Please install bun: https://bun.sh/docs/installation")
        sys.exit(1)


def docs_dev() -> None:
    """Run the docs development server."""
    check_bun()
    docs_config_dir = os.path.dirname(__file__)
    subprocess.run(["bun", "run", "dev"], cwd=docs_config_dir, check=True)


def docs_build() -> None:
    """Build the docs for production."""
    check_bun()
    docs_config_dir = os.path.dirname(__file__)
    subprocess.run(["bun", "run", "build"], cwd=docs_config_dir, check=True)
