"""Anthropic model feature testing.

This script:
1. Discovers all models from the Anthropic API
2. Saves model information to a YAML file

The results are tracked incrementally - re-running the script will only discover
new models, not re-discover existing ones.

Usage:
    python -m model_features.test_anthropic [options]

Options:
    --discover-only     Only discover models, don't run tests
    --list-models       List discovered models
    --summary           Show summary of current test results
    --output PATH       Output file path (default: scripts/model_features/data/anthropic.yaml)

Requires ANTHROPIC_API_KEY environment variable (loaded from .env if present).
"""

import argparse
import os
import sys
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv

from .core import ModelFeatureRegistry, ModelInfo

load_dotenv()

# ============================================================================
# Anthropic Provider Configuration
# ============================================================================

ANTHROPIC_PROVIDER = "anthropic"


# ============================================================================
# Model Discovery
# ============================================================================


def discover_anthropic_models(client: Anthropic) -> Iterator[ModelInfo]:
    """Discover models from Anthropic's /v1/models endpoint.

    Yields all models returned by the API with pagination support.
    """
    # Fetch all models using pagination
    has_more = True
    after_id = None

    while has_more:
        if after_id:
            response = client.models.list(after_id=after_id, limit=100)
        else:
            response = client.models.list(limit=100)

        for model in response.data:
            # Parse created_at timestamp
            created = None
            if model.created_at:
                try:
                    # Parse RFC 3339 datetime string
                    created_str = str(model.created_at)
                    if created_str.endswith("Z"):
                        created_str = created_str[:-1] + "+00:00"
                    created = datetime.fromisoformat(created_str)
                except (ValueError, AttributeError):
                    pass

            metadata: dict[str, Any] = {}
            display_name = getattr(model, "display_name", None)
            if display_name:
                metadata["display_name"] = display_name

            yield ModelInfo(
                id=model.id,
                owned_by="anthropic",  # All models are owned by Anthropic
                created=created,
                discovered_at=datetime.now(),
                metadata=metadata,
            )

        has_more = response.has_more
        if has_more:
            after_id = response.last_id


# ============================================================================
# CLI
# ============================================================================


def _show_summary(registry: ModelFeatureRegistry) -> None:
    """Show a summary of current test results."""
    models = registry.registry.models

    if not models:
        print("No models in registry yet.")
        return

    print(f"Models: {len(models)}")
    print()

    # Show model details
    print("Discovered models:")
    for model_id in sorted(models.keys()):
        matrix = registry.registry.get_model(model_id)
        if matrix:
            info = matrix.model
            display_name = info.metadata.get("display_name")
            if display_name:
                print(f"  {model_id} ({display_name})")
            else:
                print(f"  {model_id}")
            if info.deprecated:
                print("    Status: DEPRECATED")
            if info.created:
                print(f"    Created: {info.created.strftime('%Y-%m-%d')}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Discover Anthropic models incrementally"
    )
    parser.add_argument(
        "--discover-only", action="store_true", help="Only discover models"
    )
    parser.add_argument(
        "--list-models", action="store_true", help="List discovered models"
    )
    parser.add_argument(
        "--summary", action="store_true", help="Show summary of discovered models"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (default: scripts/model_features/data/anthropic.yaml)",
    )

    args = parser.parse_args()

    # Setup paths
    script_dir = Path(__file__).parent
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = script_dir / "data" / "anthropic.yaml"

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key and not (args.list_models or args.summary):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set it in your .env file or environment")
        return 1

    # Initialize registry
    registry = ModelFeatureRegistry(output_path, ANTHROPIC_PROVIDER)

    # List models
    if args.list_models:
        models = sorted(registry.get_all_model_ids())
        if not models:
            print("No models discovered yet. Run without --list-models first.")
            return 0
        print(f"Discovered models ({len(models)}):")
        for model_id in models:
            matrix = registry.registry.get_model(model_id)
            if matrix:
                display_name = matrix.model.metadata.get("display_name")
                if display_name:
                    print(f"  - {model_id} ({display_name})")
                else:
                    print(f"  - {model_id}")
                if matrix.model.deprecated:
                    print("    (deprecated)")
        return 0

    # Show summary
    if args.summary:
        _show_summary(registry)
        return 0

    # Initialize client
    client = Anthropic(api_key=api_key)

    # Discover models
    print("Discovering models from Anthropic API...")
    discovered_models = list(discover_anthropic_models(client))

    # Add models to registry
    new_count = 0
    for model_info in discovered_models:
        if registry.add_model(model_info):
            new_count += 1
            print(f"  + {model_info.id}")

    print(f"\nDiscovered {new_count} new models")
    total = len(registry.get_all_model_ids())
    print(f"Total models in registry: {total}")

    # Save registry
    registry.save()
    print(f"\nSaved to: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
