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
    subprocess.run(["bun", "install"], cwd=docs_config_dir, check=True)
    subprocess.run(["bun", "run", "dev"], cwd=docs_config_dir, check=True)


def docs_build() -> None:
    """Build the docs for production."""
    check_bun()
    docs_config_dir = os.path.dirname(__file__)
    subprocess.run(["bun", "install"], cwd=docs_config_dir, check=True)
    subprocess.run(["bun", "run", "build"], cwd=docs_config_dir, check=True)
    # NOTE: this is to prevent any crawling of the v2 docs site, which we may always want
    with open(os.path.join(docs_config_dir, "dist", "robots.txt"), "w") as f:
        f.write("User-agent: *\nDisallow: /")
    with open(os.path.join(docs_config_dir, "dist", "public", "robots.txt"), "w") as f:
        f.write("User-agent: *\nDisallow: /")
