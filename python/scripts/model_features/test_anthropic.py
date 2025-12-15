"""Anthropic model feature testing.

This script:
1. Discovers all models from the Anthropic API
2. Tests each model for various feature support
3. Saves results incrementally to a YAML file

The results are tracked incrementally - re-running the script will only test
new models or new features, not re-test existing combinations.

Usage:
    python -m model_features.test_anthropic [options]

Options:
    --discover-only     Only discover models, don't run tests
    --test-only         Only run tests, don't discover new models
    --features FEAT     Comma-separated list of features to test
    --models MODEL      Comma-separated list of models to test
    --retest-errors     Re-test combinations that previously errored
    --retest-all        Re-test all combinations (ignore existing results)
    --list-features     List available feature tests
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
from typing import Any, cast

from anthropic import Anthropic
from anthropic.types import ToolParam
from dotenv import load_dotenv

from .core import (
    FeatureTest,
    FeatureTestResult,
    FeatureTestRunner,
    ModelFeatureRegistry,
    ModelInfo,
    TestStatus,
)

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
# Feature Tests
# ============================================================================

# Type alias for Anthropic feature tests
AnthropicFeatureTest = FeatureTest[Anthropic]


class StrictStructuredOutputSupport(FeatureTest[Anthropic]):
    """Test if a model supports strict structured output (strict mode tools)."""

    name = "strict_structured_output"

    def test(self, model_id: str, client: Anthropic) -> FeatureTestResult:
        try:
            tool: ToolParam = cast(
                ToolParam,
                {
                    "name": "person_schema",
                    "description": "A person's information",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                        },
                        "required": ["name"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                },
            )
            client.messages.create(
                model=model_id,
                max_tokens=100,
                messages=[{"role": "user", "content": "Give me a person's name"}],
                tools=[tool],
                tool_choice={"type": "tool", "name": "person_schema"},
                extra_headers={"anthropic-beta": "structured-outputs-2025-11-13"},
            )
            return FeatureTestResult(status=TestStatus.SUPPORTED)
        except Exception as e:
            error_str = str(e).lower()
            error_code = getattr(e, "status_code", None)

            if error_code == 404 or "model_not_found" in error_str:
                return FeatureTestResult(
                    status=TestStatus.UNAVAILABLE, error_message=str(e)
                )

            if (
                "structured outputs are not supported" in error_str
                or "strict" in error_str
                or "not supported for this model" in error_str
            ):
                return FeatureTestResult(status=TestStatus.NOT_SUPPORTED)

            return FeatureTestResult(status=TestStatus.ERROR, error_message=str(e))


def get_all_anthropic_feature_tests() -> list[AnthropicFeatureTest]:
    """Get instances of all Anthropic feature tests."""
    return [
        StrictStructuredOutputSupport(),
    ]


# ============================================================================
# CLI
# ============================================================================


def _show_summary(registry: ModelFeatureRegistry) -> None:
    """Show a summary of current test results."""
    models = registry.registry.models
    features = sorted(registry.registry.known_features)

    if not models:
        print("No models in registry yet.")
        return

    print(f"Models: {len(models)}")
    print(f"Features: {len(features)}")
    print()

    # Count by feature
    if features:
        print("Feature support summary:")
        for feature in features:
            supported = 0
            not_supported = 0
            unavailable = 0
            errors = 0
            skipped = 0
            untested = 0

            for matrix in models.values():
                result = matrix.features.get(feature)
                if result is None:
                    untested += 1
                elif result.status == TestStatus.SUPPORTED:
                    supported += 1
                elif result.status == TestStatus.NOT_SUPPORTED:
                    not_supported += 1
                elif result.status == TestStatus.UNAVAILABLE:
                    unavailable += 1
                elif result.status == TestStatus.SKIPPED:
                    skipped += 1
                else:
                    errors += 1

            print(f"  {feature}:")
            print(f"    Supported: {supported}")
            print(f"    Not supported: {not_supported}")
            print(f"    Unavailable: {unavailable}")
            print(f"    Errors: {errors}")
            if skipped > 0:
                print(f"    Skipped: {skipped}")
            print(f"    Untested: {untested}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Test Anthropic model features incrementally"
    )
    parser.add_argument(
        "--discover-only", action="store_true", help="Only discover models"
    )
    parser.add_argument(
        "--test-only", action="store_true", help="Only run tests, skip discovery"
    )
    parser.add_argument(
        "--features", type=str, help="Comma-separated list of features to test"
    )
    parser.add_argument(
        "--models", type=str, help="Comma-separated list of models to test"
    )
    parser.add_argument(
        "--retest-errors",
        action="store_true",
        help="Re-test combinations that errored",
    )
    parser.add_argument(
        "--retest-all",
        action="store_true",
        help="Re-test all combinations",
    )
    parser.add_argument(
        "--list-features", action="store_true", help="List available feature tests"
    )
    parser.add_argument(
        "--list-models", action="store_true", help="List discovered models"
    )
    parser.add_argument(
        "--summary", action="store_true", help="Show summary of test results"
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
    if not api_key and not (args.list_features or args.list_models or args.summary):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set it in your .env file or environment")
        return 1

    # Initialize registry
    registry = ModelFeatureRegistry(output_path, ANTHROPIC_PROVIDER)

    # List features
    if args.list_features:
        print("Available feature tests:")
        for test in get_all_anthropic_feature_tests():
            print(f"  - {test.name}")
        return 0

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

    # Initialize client and runner
    client = Anthropic(api_key=api_key)
    runner = FeatureTestRunner(registry, client)

    # Register feature tests
    feature_tests = get_all_anthropic_feature_tests()

    # Filter to requested features if specified
    if args.features:
        requested = set(args.features.split(","))
        feature_tests = [t for t in feature_tests if t.name in requested]
        if not feature_tests:
            print(f"Error: No valid features in: {args.features}")
            print("Use --list-features to see available features")
            return 1

    for test in feature_tests:
        runner.register_feature_test(test)

    # Discover models
    if not args.test_only:
        print("Discovering models from Anthropic API...")
        new_count = runner.add_models(discover_anthropic_models(client))
        print(f"  Found {new_count} new models")
        total = len(registry.get_all_model_ids())
        print(f"  Total models in registry: {total}")

    if args.discover_only:
        return 0

    # Determine which tests to run
    model_filter = args.models.split(",") if args.models else None

    if args.retest_all:
        # Get all combinations
        all_models = model_filter or list(registry.get_all_model_ids())
        all_features = [t.name for t in feature_tests]
        pending = [(m, f) for m in all_models for f in all_features]
    else:
        pending = runner.get_pending_tests(
            features=[t.name for t in feature_tests],
            models=model_filter,
            include_errors=args.retest_errors,
        )

    if not pending:
        print("\nNo pending tests to run!")
        print("Use --retest-errors or --retest-all to re-run tests")
        return 0

    print(f"\nRunning {len(pending)} tests...")
    summary = runner.run_tests(pending)
    print(f"\n{summary}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
