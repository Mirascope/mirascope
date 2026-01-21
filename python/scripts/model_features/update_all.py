"""Run all model feature tests and code generation for all providers.

This script runs the test and codegen scripts for all supported providers:
- Google
- OpenAI
- Anthropic

For each provider, it:
1. Runs the test script to discover models and test feature support
2. Runs the codegen script to generate model_info.py files

Usage:
    uv run python -m scripts.model_features.update_all [options]

Options:
    --test-only         Only run tests, skip code generation
    --codegen-only      Only run code generation, skip tests
    --providers NAMES   Comma-separated list of providers (default: all)
                        Valid providers: google, openai, anthropic

Requires API keys for each provider (loaded from .env if present):
- GOOGLE_API_KEY
- OPENAI_API_KEY
- ANTHROPIC_API_KEY
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return whether it succeeded.

    Args:
        cmd: Command to run as list of strings
        description: Description of what the command does

    Returns:
        True if command succeeded, False otherwise
    """
    print(f"\n{'=' * 80}")
    print(f"{description}")
    print(f"{'=' * 80}")
    print(f"Running: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent.parent)

    if result.returncode != 0:
        print(f"\n❌ Failed: {description}")
        return False

    print(f"\n✅ Success: {description}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run all model feature tests and code generation"
    )
    parser.add_argument(
        "--test-only", action="store_true", help="Only run tests, skip code generation"
    )
    parser.add_argument(
        "--codegen-only",
        action="store_true",
        help="Only run code generation, skip tests",
    )
    parser.add_argument(
        "--providers",
        type=str,
        default="google,openai,anthropic",
        help="Comma-separated list of providers (default: all)",
    )

    args = parser.parse_args()

    # Parse providers
    valid_providers = {"google", "openai", "anthropic"}
    providers = [p.strip().lower() for p in args.providers.split(",")]

    # Validate providers
    invalid = set(providers) - valid_providers
    if invalid:
        print(f"Error: Invalid providers: {', '.join(invalid)}")
        print(f"Valid providers: {', '.join(sorted(valid_providers))}")
        return 1

    # Track overall success
    all_succeeded = True

    # Run tests for each provider
    if not args.codegen_only:
        for provider in providers:
            success = run_command(
                [
                    "uv",
                    "run",
                    "python",
                    "-m",
                    f"scripts.model_features.test_{provider}",
                ],
                f"Testing {provider.upper()} models",
            )
            if not success:
                all_succeeded = False
                print(f"\n⚠️  Warning: Test for {provider} failed, continuing anyway...")

    # Run codegen for each provider
    if not args.test_only:
        for provider in providers:
            success = run_command(
                [
                    "uv",
                    "run",
                    "python",
                    "-m",
                    f"scripts.model_features.codegen_{provider}",
                ],
                f"Generating code for {provider.upper()}",
            )
            if not success:
                all_succeeded = False
                print(
                    f"\n⚠️  Warning: Codegen for {provider} failed, continuing anyway..."
                )

    # Print summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")

    if all_succeeded:
        print("✅ All operations completed successfully!")
        return 0
    else:
        print("⚠️  Some operations failed. See output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
