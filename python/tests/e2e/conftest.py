"""Configuration for Mirascope end to end tests.

Includes setting up VCR for HTTP recording/playback.
"""

from __future__ import annotations

import sys
from collections.abc import Callable, Generator
from copy import deepcopy
from typing import Any, TypedDict, get_args

import pytest

from mirascope import llm
from mirascope.llm.providers.provider_registry import (
    PROVIDER_REGISTRY,
)

SENSITIVE_HEADERS = [
    "authorization",  # OpenAI Bearer tokens
    "x-api-key",  # Anthropic API keys
    "x-goog-api-key",  # Google/Gemini API keys
    "anthropic-organization-id",  # Anthropic org identifiers
    "cookie",  # Session cookies
]


@pytest.fixture(autouse=True)
def reset_provider_registry() -> Generator[None, None, None]:
    """Reset the provider registry before and after each test.

    Also ensures that the anthropic-beta provider is available.
    """
    PROVIDER_REGISTRY.clear()
    _anthropic_provider = llm.load_provider("anthropic")
    assert isinstance(_anthropic_provider, llm.providers.AnthropicProvider)
    _beta_provider = _anthropic_provider._beta_provider  # pyright: ignore[reportPrivateUsage]
    llm.register_provider(_beta_provider, "anthropic-beta/")
    yield
    PROVIDER_REGISTRY.clear()


E2E_MODEL_IDS: list[llm.ModelId] = [
    "anthropic/claude-sonnet-4-0",
    "anthropic-beta/claude-sonnet-4-0",
    "google/gemini-2.5-flash",
    "openai/gpt-4o:completions",
    "openai/gpt-4o:responses",
]

# NOTE: MLX is only available on macOS (Apple Silicon)
if sys.platform == "darwin":
    from .mlx_lm_cassette import (
        mlx_cassette_fixture,  # noqa: F401 # pyright: ignore[reportUnusedImport]
    )

    E2E_MODEL_IDS.append("mlx-community/Qwen3-0.6B-4bit-DWQ-053125")

STRUCTURED_OUTPUT_MODEL_IDS = [*E2E_MODEL_IDS, "anthropic/claude-sonnet-4-5"]

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

    before_record_request: Callable[[Any], Any]
    """Callback to sanitize requests before saving to cassette.

    This function is called AFTER the real HTTP request is sent (with valid auth),
    but BEFORE it's written to the cassette file. Use this to sanitize sensitive
    headers without affecting the actual HTTP requests.
    """


def sanitize_request(request: Any) -> Any:  # noqa: ANN401
    """Sanitize sensitive headers in VCR request before recording to cassette.

    This hook is called AFTER the real HTTP request is sent (with valid auth),
    but BEFORE it's written to the cassette file. We deep copy the request
    and replace sensitive headers with placeholders.

    Also normalizes Azure OpenAI URLs to use a dummy endpoint so that
    cassettes work in CI without real Azure credentials.

    Args:
        request: VCR request object to sanitize (Any type since VCR doesn't
            provide typed request objects)

    Returns:
        Sanitized copy of the request safe for cassette storage
    """
    request = deepcopy(request)

    headers_to_filter = {header.lower() for header in SENSITIVE_HEADERS}
    for req_header in request.headers:
        if req_header.lower() in headers_to_filter:
            if isinstance(request.headers[req_header], list):
                request.headers[req_header] = ["<filtered>"]
            else:
                request.headers[req_header] = "<filtered>"

    return request


@pytest.fixture(scope="session")
def vcr_config() -> VCRConfig:
    """VCR configuration for all API tests.

    Uses session scope since VCR configuration is static and can be shared
    across all test modules in a session. This covers all major LLM providers:
    - OpenAI (authorization header)
    - Google/Gemini (x-goog-api-key header)
    - Anthropic (x-api-key, anthropic-organization-id headers)

    Note:
        We use before_record_request hook for sanitizing sensitive headers.
        This ensures the real HTTP requests (with valid auth) are sent
        successfully, but sensitive headers are replaced with placeholders
        in the cassette files.

    Returns:
        VCRConfig: Dictionary with VCR.py configuration settings
    """
    return {
        "record_mode": "once",
        "match_on": ["method", "uri", "body"],
        "before_record_request": sanitize_request,
    }


class ProviderRequest(pytest.FixtureRequest):
    """Request for the `provider` fixture parameter."""

    param: llm.ProviderId


@pytest.fixture
def provider(request: ProviderRequest) -> llm.ProviderId:
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
    "Usage",
]
