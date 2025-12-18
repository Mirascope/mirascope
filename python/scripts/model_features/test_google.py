"""Google model feature testing.

This script:
1. Discovers all models from the Google AI API
2. Tests each model for various feature support
3. Saves results incrementally to a YAML file

The results are tracked incrementally - re-running the script will only test
new models or new features, not re-test existing combinations.

Usage:
    python -m model_features.test_google [options]

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
    --output PATH       Output file path (default: scripts/model_features/data/google.yaml)

Requires GOOGLE_API_KEY environment variable (loaded from .env if present).
"""

import argparse
import os
import sys
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google.genai import Client, types as genai_types

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
# Google Provider Configuration
# ============================================================================

GOOGLE_PROVIDER = "google"


# ============================================================================
# Model Discovery
# ============================================================================


def discover_google_models(client: Client) -> Iterator[ModelInfo]:
    """Discover models from Google's Gemini API.

    Yields all models returned by the API.
    """
    for model in client.models.list():
        if not model.name:
            raise ValueError("unnamed model")

        yield ModelInfo(
            id=model.name.removeprefix("models/"),
            owned_by="google",
            created=None,  # Google doesn't provide creation timestamp
            discovered_at=datetime.now(),
            metadata={"display_name": model.display_name}
            if hasattr(model, "display_name")
            else {},
        )


# ============================================================================
# Feature Tests
# ============================================================================

# Type alias for Google feature tests
GoogleFeatureTest = FeatureTest[Client]


class ChatModelSupport(FeatureTest[Client]):
    """Test if a model supports basic chat functionality.

    This is a basic test to check if the model can respond to a simple prompt.
    Models that fail this test are not chat models and won't support other features.
    """

    name = "chat_model"

    def test(self, model_id: str, client: Client) -> FeatureTestResult:
        """Test if model can respond to a basic prompt.

        Args:
            model_id: The model ID to test (e.g., "gemini-2.5-flash")
            client: The Google GenAI client
        """
        try:
            response = client.models.generate_content(
                model=f"models/{model_id}",
                contents="Say hello",
            )

            # Check if we got a valid response with text
            if (
                hasattr(response, "text")
                and response.text
                and "hello" in response.text.lower()
            ):
                return FeatureTestResult(status=TestStatus.SUPPORTED)

            return FeatureTestResult(
                status=TestStatus.NOT_SUPPORTED,
                metadata={"reason": "no_valid_response"},
            )

        except Exception as e:
            error_str = str(e).lower()

            if "not found" in error_str or "invalid model" in error_str:
                return FeatureTestResult(
                    status=TestStatus.UNAVAILABLE, error_message=str(e)
                )

            if "not supported" in error_str or "does not support" in error_str:
                return FeatureTestResult(status=TestStatus.NOT_SUPPORTED)

            return FeatureTestResult(status=TestStatus.ERROR, error_message=str(e))


class StructuredOutputWithToolsSupport(FeatureTest[Client]):
    """Test if a model supports structured outputs when tools are present.

    This test checks whether a model can:
    1. Handle structured output requests (JSON schema)
    2. Use tools when structured output is requested

    Google does not support strict outputs when tools are present:
    - Gemini 2.5 will error
    - 2.0 and below will ignore tools

    Success means the model calls the tool.
    Failure means the model either errors or ignores the tool.
    """

    name = "structured_output_with_tools"
    dependencies = ["chat_model"]  # Requires basic chat functionality

    def test(self, model_id: str, client: Client) -> FeatureTestResult:
        """Test if model can use tools while respecting structured output.

        Args:
            model_id: The model ID to test (e.g., "gemini-2.5-flash")
            client: The Google GenAI client
        """
        try:
            # Define a tool that must be called to generate the structured output
            get_value_tool = genai_types.FunctionDeclarationDict(
                name="get_value",
                description="Gets a value needed for the response",
                parameters=genai_types.SchemaDict(
                    type=genai_types.Type.OBJECT,
                    properties={
                        "key": genai_types.SchemaDict(
                            type=genai_types.Type.STRING,
                            description="The key to look up",
                        )
                    },
                    required=["key"],
                ),
            )

            # Configure response schema for structured output
            response_schema = genai_types.SchemaDict(
                type=genai_types.Type.OBJECT,
                properties={
                    "result": genai_types.SchemaDict(type=genai_types.Type.STRING),
                },
                required=["result"],
            )

            # Create a prompt that requires calling the tool
            response = client.models.generate_content(
                model=f"models/{model_id}",
                contents="Call the get_value tool with key='test' to get the value you need, then return it in the result field",
                config=genai_types.GenerateContentConfigDict(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    tools=[
                        genai_types.ToolDict(function_declarations=[get_value_tool])
                    ],
                ),
            )

            # Check if the model made a tool call
            has_tool_call = False
            if hasattr(response, "candidates") and response.candidates:
                for candidate in response.candidates:
                    if (
                        hasattr(candidate, "content")
                        and candidate.content is not None
                        and hasattr(candidate.content, "parts")
                        and candidate.content.parts is not None
                    ):
                        for part in candidate.content.parts:
                            if hasattr(part, "function_call"):
                                has_tool_call = True
                                break

            if has_tool_call:
                # Model successfully called the tool with structured output
                return FeatureTestResult(
                    status=TestStatus.SUPPORTED,
                    metadata={"called_tool": True},
                )
            else:
                # Model ignored the tool and tried to generate structured output directly
                return FeatureTestResult(
                    status=TestStatus.NOT_SUPPORTED,
                    metadata={"called_tool": False, "reason": "tools_ignored"},
                )

        except Exception as e:
            error_str = str(e).lower()

            if "not found" in error_str or "invalid model" in error_str:
                return FeatureTestResult(
                    status=TestStatus.UNAVAILABLE, error_message=str(e)
                )

            if (
                "response_schema" in error_str
                or "tools" in error_str
                or "cannot be used with" in error_str
                or "not supported" in error_str
            ):
                return FeatureTestResult(
                    status=TestStatus.NOT_SUPPORTED,
                    error_message=str(e),
                )

            return FeatureTestResult(status=TestStatus.ERROR, error_message=str(e))


def get_all_google_feature_tests() -> list[GoogleFeatureTest]:
    """Get instances of all Google feature tests."""
    return [
        ChatModelSupport(),
        StructuredOutputWithToolsSupport(),
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
        description="Test Google model features incrementally"
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
        help="Output file path (default: scripts/model_features/data/google.yaml)",
    )

    args = parser.parse_args()

    # Setup paths
    script_dir = Path(__file__).parent
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = script_dir / "data" / "google.yaml"

    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key and not (args.list_features or args.list_models or args.summary):
        print("Error: GOOGLE_API_KEY environment variable not set")
        print("Please set it in your .env file or environment")
        return 1

    # Initialize registry
    registry = ModelFeatureRegistry(output_path, GOOGLE_PROVIDER)

    # List features
    if args.list_features:
        print("Available feature tests:")
        for test in get_all_google_feature_tests():
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
    client = Client(api_key=api_key)
    runner = FeatureTestRunner(registry, client)

    # Register feature tests
    feature_tests = get_all_google_feature_tests()

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
        print("Discovering models from Google AI API...")
        new_count = runner.add_models(discover_google_models(client))
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
