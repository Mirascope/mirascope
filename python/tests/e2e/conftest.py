"""Configuration for Mirascope end to end tests.

Includes setting up VCR for HTTP recording/playback.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from copy import deepcopy
from typing import Any, TypedDict, get_args

import pytest

from mirascope import llm
from mirascope.llm.clients import clear_all_client_caches

SENSITIVE_HEADERS = [
    # Common API authentication headers
    "api-key",
    "authorization",
    "x-api-key",
    "x-goog-api-key",
    "anthropic-organization-id",
    "cookie",
]

PROVIDER_MODEL_ID_PAIRS: list[tuple[llm.Provider, llm.ModelId]] = [
    ("anthropic", "claude-sonnet-4-0"),
    ("azure-openai:completions", "gpt-4o-mini"),
    ("azure-openai:responses", "gpt-4o-mini"),
    ("google", "gemini-2.5-flash"),
    ("openai:completions", "gpt-4o"),
    ("openai:responses", "gpt-4o"),
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

    if ".openai.azure.com" in request.uri:
        request.uri = re.sub(
            r"https://[^/]+\.openai\.azure\.com",
            "https://dummy.openai.azure.com",
            request.uri,
        )

    for header in SENSITIVE_HEADERS:
        header_lower = header.lower()
        for req_header in list(request.headers.keys()):
            if req_header.lower() == header_lower:
                if isinstance(request.headers[req_header], list):
                    request.headers[req_header] = ["<filtered>"]
                else:
                    request.headers[req_header] = "<filtered>"

    return request


@pytest.fixture(autouse=True)
def _clear_client_caches() -> None:
    """Ensure cached LLM client singletons do not bleed across e2e tests."""
    clear_all_client_caches()


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
