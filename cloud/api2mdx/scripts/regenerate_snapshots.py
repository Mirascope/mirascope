#!/usr/bin/env python3
"""Script to regenerate all test snapshots."""

import subprocess
import sys
from pathlib import Path

REPO_URL = "https://github.com/mirascope/mirascope.git"
SNAPSHOT_COMMIT = "d98c01edcafa65bfe339d3795396e77fd8217413" # first mono-repo commit
CACHE_DIR = Path(__file__).parent.parent.parent / ".build-cache" / "mirascope-snapshots"


def run_command(cmd: list[str], description: str, cwd: Path | None = None) -> bool:
    """Run a command and report success/failure."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True, cwd=cwd
        )
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(e.stderr)
        return False


def setup_mirascope_repo() -> bool:
    """Clone or update the mirascope repository to the snapshot commit."""
    if CACHE_DIR.exists():
        print(f"\n📂 Updating existing repository at {CACHE_DIR}...")
        if not run_command(
            ["git", "fetch", "origin"], "Fetching latest changes", cwd=CACHE_DIR
        ):
            return False
        if not run_command(
            ["git", "checkout", SNAPSHOT_COMMIT],
            f"Checking out commit {SNAPSHOT_COMMIT}",
            cwd=CACHE_DIR,
        ):
            return False
    else:
        print(f"\n📂 Cloning repository to {CACHE_DIR}...")
        CACHE_DIR.parent.mkdir(parents=True, exist_ok=True)
        if not run_command(
            ["git", "clone", REPO_URL, str(CACHE_DIR)], "Cloning mirascope repository"
        ):
            return False
        if not run_command(
            ["git", "checkout", SNAPSHOT_COMMIT],
            f"Checking out commit {SNAPSHOT_COMMIT}",
            cwd=CACHE_DIR,
        ):
            return False

    return True


def main() -> int:
    """Regenerate all snapshots."""
    print("🚀 Regenerating all api2mdx snapshots...")

    # Setup the mirascope repository
    if not setup_mirascope_repo():
        print("\n💥 Failed to setup mirascope repository")
        return 1

    # Path to python directory in the cloned repo
    python_path = CACHE_DIR / "python"

    if not python_path.exists():
        print(f"\n💥 Could not find python directory at {python_path}")
        return 1

    commands = [
        # Regenerate mirascope v2 llm example
        (
            [
                "uv",
                "run",
                "-m",
                "api2mdx.main",
                "--source-path",
                str(python_path),
                "--package",
                "mirascope.llm",
                "--output",
                "./snapshots/mdx",
                "--api-root",
                "/docs/mirascope/v2/api",
                "--output-directives",
                "./snapshots/directives",
            ],
            "Regenerating mirascope_v2_llm snapshot",
        ),
    ]

    success_count = 0
    for cmd, description in commands:
        if run_command(cmd, description):
            success_count += 1

    total = len(commands)
    if success_count == total:
        print(f"\n🎉 All {total} snapshots regenerated successfully!")
        print("\n💡 Use 'git diff' to see what changed")
        return 0
    else:
        print(f"\n💥 {total - success_count}/{total} snapshots failed to regenerate")
        return 1


if __name__ == "__main__":
    sys.exit(main())
