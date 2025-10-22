"""Configuration for Mirascope end to end tests.

Includes setting up VCR for HTTP recording/playback.
"""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from typing import TypedDict, cast, get_args

import pytest

from mirascope import llm

from .mlx_lm_cassette import RecordMode, record_mlx_lm

E2E_MODEL_IDS: list[llm.ModelId] = [
    "anthropic/claude-sonnet-4-0",
    "google/gemini-2.5-flash",
    "openai/gpt-4o",
    "openai:responses/gpt-4o",
    "mlx/mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
]


FORMATTING_MODES: tuple[llm.FormattingMode | None] = get_args(llm.FormattingMode) + (
    None,
)


class VCRConfig(TypedDict):
    """Configuration for VCR.py HTTP recording and playback.

    VCR.py is used to record HTTP interactions during tests and replay them
    in subsequent test runs, making tests faster and more reliable.
    """

    record_mode: str
    """How VCR should handle recording. 'once' means record once then replay.

    Options:
    - 'once': Record interactions once, then always replay from cassette
    - 'new_episodes': Record new interactions, replay existing ones
    - 'all': Always record, overwriting existing cassettes
    - 'none': Never record, only replay (will fail if cassette missing)
    """

    match_on: list[str]
    """HTTP request attributes to match when finding recorded interactions.

    Common options:
    - 'method': HTTP method (GET, POST, etc.)
    - 'uri': Request URI/URL
    - 'body': Request body content
    - 'headers': Request headers
    """

    filter_headers: list[str]
    """Headers to filter out from recordings for security/privacy.

    These headers will be removed from both recorded cassettes and
    when matching requests during playback. Commonly used for:
    - Authentication tokens
    - API keys
    - Organization identifiers
    """

    filter_post_data_parameters: list[str]
    """POST data parameters to filter out from recordings.

    Similar to filter_headers but for form data and request body parameters.
    Useful for removing sensitive data from request bodies.
    """


@pytest.fixture(scope="session")
def vcr_config() -> VCRConfig:
    """VCR configuration for all API tests.

    Uses session scope since VCR configuration is static and can be shared
    across all test modules in a session. This covers all major LLM providers:
    - OpenAI (authorization header)
    - Google/Gemini (x-goog-api-key header)
    - Anthropic (x-api-key, anthropic-organization-id headers)

    Returns:
        VCRConfig: Dictionary with VCR.py configuration settings
    """
    return {
        "record_mode": "once",
        "match_on": ["method", "uri", "body"],
        "filter_headers": [
            "authorization",  # OpenAI Bearer tokens
            "x-api-key",  # Anthropic API keys
            "x-goog-api-key",  # Google/Gemini API keys
            "anthropic-organization-id",  # Anthropic org identifiers
            "cookie",
        ],
        "filter_post_data_parameters": [],
    }


class ProviderRequest(pytest.FixtureRequest):
    """Request for the `provider` fixture parameter."""

    param: llm.Provider


@pytest.fixture
def provider(request: ProviderRequest) -> llm.Provider:
    """Get provider from test parameters."""
    return request.param


class ModelIdRequest(pytest.FixtureRequest):
    """Request for the `model_id` fixture parameter."""

    param: llm.ModelId


@pytest.fixture
def model_id(request: ModelIdRequest) -> llm.ModelId:
    """Get model_id from test parameters."""
    return request.param


class FormattingModeRequest(pytest.FixtureRequest):
    """Request for the `formatting_mode` fixture parameter.

    If `formatting_mode` is `None`, then accessing param will raise `AttributeError`.
    """

    param: llm.FormattingMode


@pytest.fixture
def formatting_mode(
    request: FormattingModeRequest,
) -> llm.FormattingMode | None:
    """Get formatting_mode from test parameters."""
    if hasattr(request, "param"):
        return request.param
    else:
        return None


# Symbols to automatically import from mirascope.llm so that snapshots are valid
# python. (Ruff --fix will clean out unused symbols)
SNAPSHOT_IMPORT_SYMBOLS = [
    "AssistantMessage",
    "Audio",
    "Base64ImageSource",
    "Base64AudioSource",
    "FinishReason",
    "Format",
    "Image",
    "SystemMessage",
    "Text",
    "TextChunk",
    "TextEndChunk",
    "TextStartChunk",
    "Thought",
    "ToolCall",
    "ToolCallChunk",
    "ToolCallEndChunk",
    "ToolCallStartChunk",
    "ToolOutput",
    "URLImageSource",
    "UserMessage",
]


def _is_mlx_provider(request: pytest.FixtureRequest) -> bool:
    """Check if the current test is using the MLX provider.

    Args:
        request: The pytest fixture request object.

    Returns:
        True if the test is using the MLX provider, False otherwise.
    """
    model_id_param: llm.ModelId | None = None
    if "model_id" in request.fixturenames:
        try:
            model_id_fixture = request.getfixturevalue("model_id")
            if isinstance(model_id_fixture, str):
                model_id_param = model_id_fixture
        except Exception:
            pass

    if model_id_param is None:
        return False

    return model_id_param.startswith("mlx/")


def _get_mlx_cassette_path(request: pytest.FixtureRequest) -> Path:
    test_file_path = Path(request.node.fspath)
    sanitized_test_name = (
        request.node.name.replace("/", "_")
        .replace(" ", "_")
        .replace("[", "_")
        .replace("]", "_")
        .replace(",", "_")
    )
    return test_file_path.parent / "mlx_lm_cassettes" / f"{sanitized_test_name}.yaml"


@pytest.fixture(autouse=True)
def mlx_cassette_fixture(
    request: pytest.FixtureRequest,
) -> Generator[None, None, None]:
    """Automatically mock MLX operations when testing MLX provider.

    TODO: Currently we have a dedicated cassette fixture for MLX because
      inference results can't be cached with VCR.py (as inference runs locally).
      In the future, we may want to generalize this solution to support new
      providers that require similar treatment, such as Grok which uses gRPC.

    This fixture:
    - Detects when a test is using the MLX provider
    - Mocks mlx_lm.load() to avoid downloading models
    - Patches MLX generation methods to use cassettes
    - Manages cassette lifecycle (load, record, save)
    """
    if not _is_mlx_provider(request):
        # If not using MLX provider, return an empty generator
        yield
        return

    cassette_path = _get_mlx_cassette_path(request)
    record_mode = request.config.getoption("--vcr-record-mode")
    record_mode = request.config.getoption("--vcr-record") or record_mode
    record_mode = record_mode or "none"

    if record_mode not in ["once", "new_episodes", "all", "none"]:
        raise ValueError(f"Invalid VCR record_mode: {record_mode}")

    with record_mlx_lm(cassette_path, cast(RecordMode, record_mode)):
        yield
