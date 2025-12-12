"""Configuration for Mirascope end to end tests.

Includes setting up VCR for HTTP recording/playback.
"""

from __future__ import annotations

import asyncio
import sys
from collections.abc import Generator
from typing import TypedDict, get_args
from unittest.mock import patch

import httpx
import pytest
from google.auth.credentials import Credentials
from google.genai import Client as GoogleGenAIClient
from google.genai.client import DebugConfig
from google.genai.types import HttpOptions, HttpOptionsDict
from vcr.stubs import aiohttp_stubs

from mirascope import llm

_BASE_MODEL_IDS: list[llm.ModelId] = [
    "anthropic/claude-sonnet-4-0",
    "google/gemini-2.5-flash",
    "openai/gpt-4o:completions",
    "openai/gpt-4o:responses",
]
E2E_MODEL_IDS = _BASE_MODEL_IDS.copy()
E2E_ASYNC_STREAM_MODEL_IDS = _BASE_MODEL_IDS.copy()
E2E_IMAGE_URL_MODEL_IDS = _BASE_MODEL_IDS.copy()
E2E_TOOL_MODEL_IDS = _BASE_MODEL_IDS.copy()
E2E_TOOL_ASYNC_STREAM_MODEL_IDS = _BASE_MODEL_IDS.copy()
E2E_STRUCTURED_OUTPUT_WITH_TOOLS_MODEL_IDS = _BASE_MODEL_IDS.copy()

# NOTE: Together AI provider
E2E_MODEL_IDS.append("together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8")
# Llama 4 has a bug where it returns tool calls instead of text after receiving
# tool outputs, so we use DeepSeek for tool tests.
E2E_TOOL_MODEL_IDS.append("together/deepseek-ai/DeepSeek-V3.1")
# VCR.py's aiohttp stubs don't support async streaming with Together SDK,
# so Together is excluded from async stream tests.
# Together can't fetch images from URLs (returns "image could not be processed").
# DeepSeek returns garbage tokens in streaming mode for complex prompts,
# so Together is excluded from structured output with tools tests.

# NOTE: MLX is only available on macOS (Apple Silicon)
if sys.platform == "darwin":
    from .mlx_lm_cassette import (
        mlx_cassette_fixture,  # noqa: F401 # pyright: ignore[reportUnusedImport]
    )

    E2E_MODEL_IDS.append("mlx-community/Qwen3-0.6B-4bit-DWQ-053125")


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
]


def _patched_vcr_aiohttp_content(
    self: aiohttp_stubs.MockClientResponse,
) -> asyncio.StreamReader:
    """Patched content property that ensures body is bytes before feeding to stream."""
    s = aiohttp_stubs.MockStream()
    body: bytes | str | None = self._body  # pyright: ignore[reportPrivateUsage]
    if body is None:
        body = b""
    elif isinstance(body, str):
        body = body.encode("utf-8")
    s.feed_data(body)
    s.feed_eof()
    return s


@pytest.fixture(autouse=True)
def _vcr_aiohttp_fix() -> Generator[None, None, None]:  # pyright: ignore[reportUnusedFunction]
    """Fix VCR's aiohttp stubs to handle string bodies in YAML cassettes."""
    with patch.object(
        aiohttp_stubs.MockClientResponse,
        "content",
        property(_patched_vcr_aiohttp_content),
    ):
        yield


@pytest.fixture(scope="session", autouse=True)
def _google_force_httpx() -> Generator[None, None, None]:  # pyright: ignore[reportUnusedFunction]
    """Force Google GenAI SDK to use httpx for async operations.

    When aiohttp is installed, the Google GenAI SDK uses it for async HTTP requests.
    However, VCR.py's aiohttp stubs have compatibility issues where HTTP methods
    are recorded in lowercase (e.g., 'post') but cassettes expect uppercase ('POST').
    This causes cassette matching to fail during playback.

    This fixture patches the Google GenAI Client to always use httpx's AsyncHTTPTransport
    for async operations, ensuring consistent behavior with VCR.py.
    """
    original_init = GoogleGenAIClient.__init__

    def _patched_init(
        self: GoogleGenAIClient,
        *,
        vertexai: bool | None = None,
        api_key: str | None = None,
        credentials: Credentials | None = None,
        project: str | None = None,
        location: str | None = None,
        debug_config: DebugConfig | None = None,
        http_options: HttpOptions | HttpOptionsDict | None = None,
    ) -> None:
        if http_options is None:
            http_options = HttpOptions(
                async_client_args={"transport": httpx.AsyncHTTPTransport()}
            )
        elif isinstance(http_options, dict):
            async_args = http_options.get("async_client_args")
            if async_args is None:
                http_options["async_client_args"] = {
                    "transport": httpx.AsyncHTTPTransport()
                }
            elif "transport" not in async_args:
                async_args["transport"] = httpx.AsyncHTTPTransport()
        elif isinstance(http_options, HttpOptions):
            if http_options.async_client_args is None:
                http_options = HttpOptions(
                    api_version=http_options.api_version,
                    base_url=http_options.base_url,
                    headers=http_options.headers,
                    timeout=http_options.timeout,
                    client_args=http_options.client_args,
                    async_client_args={"transport": httpx.AsyncHTTPTransport()},
                )
            elif "transport" not in http_options.async_client_args:
                http_options.async_client_args["transport"] = httpx.AsyncHTTPTransport()

        original_init(
            self,
            vertexai=vertexai,
            api_key=api_key,
            credentials=credentials,
            project=project,
            location=location,
            debug_config=debug_config,
            http_options=http_options,
        )

    GoogleGenAIClient.__init__ = _patched_init
    try:
        yield
    finally:
        GoogleGenAIClient.__init__ = original_init
