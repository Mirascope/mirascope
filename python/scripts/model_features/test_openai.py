"""OpenAI model feature testing.

This script:
1. Discovers all models from the OpenAI API
2. Filters to system/OpenAI-owned models
3. Tests each model for various feature support
4. Saves results incrementally to a YAML file

The results are tracked incrementally - re-running the script will only test
new models or new features, not re-test existing combinations.

Usage:
    python -m model_features.openai [options]

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

Requires OPENAI_API_KEY environment variable (loaded from .env if present).
"""

import argparse
import base64
import os
import sys
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

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
# OpenAI Provider Configuration
# ============================================================================

OPENAI_PROVIDER = "openai"


# ============================================================================
# Model Discovery
# ============================================================================


def discover_openai_models(client: OpenAI) -> Iterator[ModelInfo]:
    """Discover models from OpenAI's /v1/models endpoint.

    Only yields models owned by 'system', 'openai-internal', or 'openai'.
    This filters out user fine-tuned models and other non-standard models.
    """
    models = client.models.list()

    for model in models.data:
        # Filter to only system/openai-owned models
        if model.owned_by not in ("system", "openai-internal", "openai"):
            continue

        yield ModelInfo(
            id=model.id,
            owned_by=model.owned_by,
            created=datetime.fromtimestamp(model.created) if model.created else None,
            discovered_at=datetime.now(),
        )


# ============================================================================
# Feature Tests
# ============================================================================

# Type alias for OpenAI feature tests
OpenAIFeatureTest = FeatureTest[OpenAI]


def _try_completions_call(
    client: OpenAI,
    model_id: str,
    **kwargs: Any,  # noqa: ANN401
) -> FeatureTestResult | Exception:
    """Try a completions call, handling max_tokens vs max_completion_tokens.

    Returns FeatureTestResult on success or handled error, or Exception for unhandled errors.
    """
    try:
        client.chat.completions.create(model=model_id, **kwargs)
        return FeatureTestResult(status=TestStatus.SUPPORTED)
    except Exception as e:
        error_str = str(e).lower()
        error_code = getattr(e, "status_code", None)

        if error_code == 404 or "does not exist" in error_str:
            return FeatureTestResult(
                status=TestStatus.UNAVAILABLE, error_message=str(e)
            )

        # Reasoning models need max_completion_tokens instead of max_tokens
        if "max_tokens" in kwargs and "'max_tokens' is not supported" in error_str:
            new_kwargs = {k: v for k, v in kwargs.items() if k != "max_tokens"}
            new_kwargs["max_completion_tokens"] = kwargs["max_tokens"]
            return _try_completions_call(client, model_id, **new_kwargs)

        return e


class ResponsesAPISupport(FeatureTest[OpenAI]):
    """Test if a model supports the Responses API."""

    name = "responses_api"

    def test(self, model_id: str, client: OpenAI) -> FeatureTestResult:
        try:
            client.responses.create(
                model=model_id,
                input=[{"role": "user", "content": "Say hello"}],
            )
            return FeatureTestResult(status=TestStatus.SUPPORTED)
        except Exception as e:
            error_str = str(e).lower()

            if "does not exist" in error_str or "model not found" in error_str:
                return FeatureTestResult(
                    status=TestStatus.UNAVAILABLE, error_message=str(e)
                )

            if "is not supported with the responses api" in error_str:
                return FeatureTestResult(status=TestStatus.NOT_SUPPORTED)

            # Check for rate limit or auth errors - these are real errors
            if "rate limit" in error_str or "authentication" in error_str:
                return FeatureTestResult(status=TestStatus.ERROR, error_message=str(e))

            # Unknown error - could be unsupported
            return FeatureTestResult(status=TestStatus.ERROR, error_message=str(e))


class ReasoningSupport(FeatureTest[OpenAI]):
    """Test if a model supports the reasoning parameter in Responses API."""

    name = "reasoning"
    dependencies = ["responses_api"]  # Requires Responses API support

    def test(self, model_id: str, client: OpenAI) -> FeatureTestResult:
        try:
            client.responses.create(
                model=model_id,
                input=[{"role": "user", "content": "Say hello"}],
                reasoning={"effort": "medium"},
            )
            return FeatureTestResult(status=TestStatus.SUPPORTED)
        except Exception as e:
            error_str = str(e).lower()

            if "does not exist" in error_str or "model not found" in error_str:
                return FeatureTestResult(
                    status=TestStatus.UNAVAILABLE, error_message=str(e)
                )

            if "is not supported with the responses api" in error_str:
                return FeatureTestResult(
                    status=TestStatus.NOT_SUPPORTED,
                    metadata={"reason": "no_responses_api"},
                )

            if (
                "unsupported parameter: 'reasoning.effort' is not supported"
                in error_str
            ):
                return FeatureTestResult(status=TestStatus.NOT_SUPPORTED)

            return FeatureTestResult(status=TestStatus.ERROR, error_message=str(e))


class CompletionsAPISupport(FeatureTest[OpenAI]):
    """Test if a model supports the Chat Completions API."""

    name = "completions_api"

    def test(self, model_id: str, client: OpenAI) -> FeatureTestResult:
        result = _try_completions_call(
            client,
            model_id,
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=5,
        )
        if isinstance(result, FeatureTestResult):
            return result

        # result is an exception
        error_str = str(result).lower()

        # Some models don't support chat completions format
        if "is not supported" in error_str:
            return FeatureTestResult(status=TestStatus.NOT_SUPPORTED)

        return FeatureTestResult(status=TestStatus.ERROR, error_message=str(result))


class AudioInputSupport(FeatureTest[OpenAI]):
    """Test if a model supports audio input in Chat Completions."""

    name = "audio_input"
    dependencies = ["completions_api"]  # Requires Chat Completions API support

    def __init__(self, audio_file_path: Path | None = None) -> None:
        # Default to test asset if available
        if audio_file_path is None:
            script_dir = Path(__file__).parent
            # Navigate from scripts/model_features/ to tests/e2e/assets/audio/
            audio_file_path = (
                script_dir.parent.parent
                / "tests"
                / "e2e"
                / "assets"
                / "audio"
                / "tagline.mp3"
            )
        self.audio_file_path = audio_file_path
        self._audio_base64: str | None = None

    def _get_audio_base64(self) -> str:
        if self._audio_base64 is None:
            if not self.audio_file_path.exists():
                raise FileNotFoundError(
                    f"Audio file not found: {self.audio_file_path}. "
                    "Please provide a valid audio file path."
                )
            self._audio_base64 = base64.b64encode(
                self.audio_file_path.read_bytes()
            ).decode("utf-8")
        return self._audio_base64

    def test(self, model_id: str, client: OpenAI) -> FeatureTestResult:
        try:
            audio_base64 = self._get_audio_base64()
            client.chat.completions.create(
                model=model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_audio",
                                "input_audio": {"data": audio_base64, "format": "mp3"},
                            }
                        ],
                    }
                ],
            )
            return FeatureTestResult(status=TestStatus.SUPPORTED)
        except Exception as e:
            error_str = str(e).lower()
            error_code = getattr(e, "status_code", None)

            if error_code == 404:
                return FeatureTestResult(
                    status=TestStatus.UNAVAILABLE, error_message=str(e)
                )

            if (
                "content blocks are expected to be either text or image_url"
                in error_str
            ):
                return FeatureTestResult(status=TestStatus.NOT_SUPPORTED)

            return FeatureTestResult(status=TestStatus.ERROR, error_message=str(e))


class StructuredOutputSupport(FeatureTest[OpenAI]):
    """Test if a model supports structured output (JSON schema)."""

    name = "structured_output"
    dependencies = ["completions_api"]  # Requires Chat Completions API support

    def test(self, model_id: str, client: OpenAI) -> FeatureTestResult:
        result = _try_completions_call(
            client,
            model_id,
            messages=[{"role": "user", "content": "Give me a person's name"}],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "person",
                    "schema": {
                        "type": "object",
                        "properties": {"name": {"type": "string"}},
                        "required": ["name"],
                    },
                },
            },
            max_tokens=20,
        )
        if isinstance(result, FeatureTestResult):
            return result

        # result is an exception
        error_str = str(result).lower()

        if (
            "response_format" in error_str
            or "json_schema" in error_str
            or "structured" in error_str
        ):
            return FeatureTestResult(status=TestStatus.NOT_SUPPORTED)

        return FeatureTestResult(status=TestStatus.ERROR, error_message=str(result))


class JSONObjectSupport(FeatureTest[OpenAI]):
    """Test if a model supports JSON object mode (response_format type json_object)."""

    name = "json_object"
    dependencies = ["completions_api"]  # Requires Chat Completions API support

    def test(self, model_id: str, client: OpenAI) -> FeatureTestResult:
        result = _try_completions_call(
            client,
            model_id,
            messages=[{"role": "user", "content": "Give me a person's name in JSON"}],
            response_format={"type": "json_object"},
            max_tokens=20,
        )
        if isinstance(result, FeatureTestResult):
            return result

        # result is an exception
        error_str = str(result).lower()

        if "response_format" in error_str or "json_object" in error_str:
            return FeatureTestResult(status=TestStatus.NOT_SUPPORTED)

        return FeatureTestResult(status=TestStatus.ERROR, error_message=str(result))


def get_all_openai_feature_tests(
    audio_file_path: Path | None = None,
) -> list[OpenAIFeatureTest]:
    """Get instances of all OpenAI feature tests."""
    return [
        ResponsesAPISupport(),
        ReasoningSupport(),
        CompletionsAPISupport(),
        AudioInputSupport(audio_file_path),
        StructuredOutputSupport(),
        JSONObjectSupport(),
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
    # TODO(dandelion): Consider refactoring to use typer when we support more providers
    parser = argparse.ArgumentParser(
        description="Test OpenAI model features incrementally"
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
        help="Output file path (default: scripts/model_features/data/openai.yaml)",
    )

    args = parser.parse_args()

    # Setup paths
    script_dir = Path(__file__).parent
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = script_dir / "data" / "openai.yaml"

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key and not (args.list_features or args.list_models or args.summary):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it in your .env file or environment")
        return 1

    # Initialize registry
    registry = ModelFeatureRegistry(output_path, OPENAI_PROVIDER)

    # List features
    if args.list_features:
        print("Available feature tests:")
        for test in get_all_openai_feature_tests():
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
            if matrix and matrix.model.deprecated:
                print(f"  - {model_id} (deprecated)")
            else:
                print(f"  - {model_id}")
        return 0

    # Show summary
    if args.summary:
        _show_summary(registry)
        return 0

    # Initialize client and runner
    client = OpenAI(api_key=api_key)
    runner = FeatureTestRunner(registry, client)

    # Register feature tests
    feature_tests = get_all_openai_feature_tests()

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
        print("Discovering models from OpenAI API...")
        new_count = runner.add_models(discover_openai_models(client))
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
