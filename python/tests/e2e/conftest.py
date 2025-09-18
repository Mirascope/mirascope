# tests/e2e/conftest.py
from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Literal, TypeAlias, get_args

import pytest
from pytest import FixtureRequest

from mirascope import llm

PROVIDER_MODEL_ID_PAIRS: list[tuple[llm.clients.Provider, llm.clients.ModelId]] = [
    ("anthropic", "claude-sonnet-4-0"),
    ("google", "gemini-2.0-flash"),
    ("openai", "gpt-4o"),
]

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


FORMATTING_MODES: tuple[llm.formatting.ConcreteFormattingMode] = get_args(
    llm.formatting.ConcreteFormattingMode
)

Snapshot: TypeAlias = Any  # Alias to avoid Ruff lint errors


class ProviderRequest(pytest.FixtureRequest):
    """Request for the `provider` fixture parameter."""

    param: llm.clients.Provider


@pytest.fixture
def provider(request: ProviderRequest) -> llm.clients.Provider:
    """Get provider from test parameters."""
    return request.param


class FormattingModeRequest(pytest.FixtureRequest):
    """Request for the `formatting_mode` fixture parameter.

    If `formatting_mode` is `None`, then accessing param will raise `AttributeError`.
    """

    param: llm.formatting.ConcreteFormattingMode


@pytest.fixture
def formatting_mode(
    request: FormattingModeRequest,
) -> llm.formatting.ConcreteFormattingMode | None:
    """Get formatting_mode from test parameters."""
    try:
        return request.param
    except AttributeError:
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

    # Known call_types to look for at the end (order matters - check longest first)
    call_types: list[CallType] = [
        "async_stream_context",
        "async_stream",
        "stream_context",
        "async_context",
        "sync_context",
        "stream",
        "async",
        "sync",
    ]

    for call_type in call_types:
        if name.endswith(f"_{call_type}"):
            scenario = name[: -len(f"_{call_type}")]
            if not scenario:
                raise ValueError(f"No scenario found in test name: {test_name}")
            return scenario, call_type

    raise ValueError(
        f"Test name '{test_name}' doesn't end with a known call type. "
        f"Expected one of: {', '.join(call_types)}. "
        "Follow convention: test_{scenario}_{call_type}"
    )


@pytest.fixture
def vcr_cassette_name(
    request: FixtureRequest,
    provider: llm.clients.Provider,
    formatting_mode: llm.formatting.ConcreteFormattingMode | None,
) -> str:
    """Generate VCR cassette name based on test name and provider."""
    test_name = request.node.name
    scenario, call_type = _parse_test_name(test_name)

    # Context and non-context calls share the same cassettes.
    cassette_call_type = call_type.replace("_context", "")

    return (
        f"{scenario}/{provider}/{cassette_call_type}"
        if formatting_mode is None
        else f"{scenario}/{provider}/{formatting_mode}_{cassette_call_type}"
    )


@pytest.fixture
def snapshot(
    request: FixtureRequest,
    provider: llm.clients.Provider,
    formatting_mode: llm.formatting.FormattingMode | None,
) -> Snapshot:
    """Get snapshot for current test configuration."""
    test_name = request.node.name
    scenario, call_type = _parse_test_name(test_name)

    file_name = (
        f"{provider}_snapshots"
        if formatting_mode is None
        else f"{formatting_mode}_{provider}_snapshots"
    )
    module_path = f"e2e.snapshots.{scenario}.{file_name}"
    snapshot_file = Path(__file__).parent / "snapshots" / scenario / f"{file_name}.py"

    # Symbols to automatically import from mirascope.llm so that snapshots are valid
    # python. (Ruff --fix will clean out unused symbols)
    snapshot_import_symbols = [
        "AssistantMessage",
        "FinishReason",
        "SystemMessage",
        "Text",
        "TextChunk",
        "TextEndChunk",
        "TextStartChunk",
        "Thinking",
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
        snapshot_file.write_text(
            "from inline_snapshot import snapshot\n\n"
            f"from mirascope.llm import {','.join(snapshot_import_symbols)}\n"
            "sync_snapshot = snapshot()\n"
            "async_snapshot = snapshot()\n"
            "stream_snapshot = snapshot()\n"
            "async_stream_snapshot = snapshot()\n"
        )

    module = importlib.import_module(module_path)
    snapshot_variable = call_type.removesuffix("_context") + "_snapshot"
    return getattr(module, snapshot_variable)
