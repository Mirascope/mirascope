"""Configuration for Mirascope end to end tests.

Includes setting up VCR for HTTP recording/playback.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Literal, TypeAlias, TypedDict, get_args

import pytest
from pytest import FixtureRequest

from mirascope import llm

PROVIDER_MODEL_ID_PAIRS: list[tuple[llm.Provider, llm.ModelId]] = [
    ("anthropic", "claude-sonnet-4-0"),
    ("google", "gemini-2.5-flash"),
    ("openai:completions", "gpt-4o"),
    ("openai:responses", "gpt-4o"),
]


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
        ],
        "filter_post_data_parameters": [],
    }


CallType = Literal[
    "sync",
    "async",
    "stream",
    "async_stream",
    "sync_context",
    "async_context",
    "stream_context",
    "async_stream_context",
]
"""The basic "call types" that all tests should cover."""

CALL_TYPES: tuple[CallType] = get_args(CallType)


FORMATTING_MODES: tuple[llm.FormattingMode | None] = get_args(llm.FormattingMode) + (
    None,
)

Snapshot: TypeAlias = Any  # Alias to avoid Ruff lint errors


class ProviderRequest(pytest.FixtureRequest):
    """Request for the `provider` fixture parameter."""

    param: llm.Provider


@pytest.fixture
def provider(request: ProviderRequest) -> llm.Provider:
    """Get provider from test parameters."""
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


def _parse_test_name(test_name: str) -> tuple[str, CallType]:
    """Parse test name following convention: test_{SCENARIO}_{CALL_TYPE}

    Examples:
        test_simple_call_sync -> ("simple_call", "sync")
        test_simple_call_async_stream -> ("simple_call", "async_stream")
        test_tool_call_sync_context -> ("tool_call", "sync_context")

    Raises:
        ValueError: If test name doesn't follow expected convention
    """
    name = test_name.split("[")[0]
    if not name.startswith("test_"):
        raise ValueError(f"Test name must start with 'test_': {test_name}")

    name = name[5:]  # Remove 'test_' prefix

    # Known call_types to look for at the end (order matters due to potential overlap - check longer overlaps first)
    call_suffixes: list[CallType] = [
        "async_stream_context",
        "async_stream",
        "stream_context",
        "async_context",
        "sync_context",
        "stream",
        "async",
        "sync",
    ]

    for call_suffix in call_suffixes:
        if name.endswith(f"_{call_suffix}"):
            scenario = name[: -len(f"_{call_suffix}")]
            if not scenario:
                raise ValueError(f"No scenario found in test name: {test_name}")
            return scenario, call_suffix

    raise ValueError(
        f"Test name '{test_name}' doesn't end with a known call suffix. "
        f"Expected one of: {', '.join(CALL_TYPES)}. "
        "Follow convention: test_{scenario}_{call_suffix}"
    )


@pytest.fixture
def vcr_cassette_name(
    request: FixtureRequest,
    provider: llm.Provider,
    formatting_mode: llm.FormattingMode | None,
) -> str:
    """Generate VCR cassette name based on test name and provider."""
    test_name = request.node.name
    scenario, call_type = _parse_test_name(test_name)

    provider_dir = provider.replace(":", "_")

    # Context and non-context calls share the same cassettes.
    cassette_call_type = call_type.replace("_context", "")

    return (
        f"{scenario}/{provider_dir}/{cassette_call_type}"
        if formatting_mode is None
        else f"{scenario}/{provider_dir}/{formatting_mode}_{cassette_call_type}"
    )


@pytest.fixture
def snapshot(
    request: FixtureRequest,
    provider: llm.Provider,
    formatting_mode: llm.FormattingMode | None,
) -> Snapshot:
    """Get snapshot for current test configuration."""
    test_name = request.node.name
    scenario, call_type = _parse_test_name(test_name)
    provider_dir = provider.replace(":", "_")

    file_name = (
        f"{provider_dir}_snapshots"
        if formatting_mode is None
        else f"{formatting_mode}_{provider_dir}_snapshots"
    )
    module_path = f"e2e.snapshots.{scenario}.{file_name}"
    snapshot_file = Path(__file__).parent / "snapshots" / scenario / f"{file_name}.py"

    # Symbols to automatically import from mirascope.llm so that snapshots are valid
    # python. (Ruff --fix will clean out unused symbols)
    snapshot_import_symbols = [
        "AssistantMessage",
        "FinishReason",
        "Format",
        "SystemMessage",
        "Text",
        "TextChunk",
        "TextEndChunk",
        "TextStartChunk",
        "Thought",
        "ToolCall",
        "ToolCall",
        "ToolCallChunk",
        "ToolCallEndChunk",
        "ToolCallStartChunk",
        "ToolOutput",
        "UserMessage",
    ]

    if not snapshot_file.exists():
        snapshot_file.parent.mkdir(parents=True, exist_ok=True)

        content = (
            "from inline_snapshot import snapshot\n\n"
            f"from mirascope.llm import {','.join(snapshot_import_symbols)}\n"
            "sync_snapshot = snapshot()\n"
            "async_snapshot = snapshot()\n"
            "stream_snapshot = snapshot()\n"
            "async_stream_snapshot = snapshot()\n"
        )

        snapshot_file.write_text(content)

    module = importlib.import_module(module_path)
    snapshot_variable = call_type.removesuffix("_context") + "_snapshot"
    return getattr(module, snapshot_variable)
