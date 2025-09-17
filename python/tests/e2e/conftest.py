# tests/e2e/conftest.py
from __future__ import annotations

import importlib
import sys
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


def _fix_duplicate_snapshots(snapshot_file: Path) -> None:
    """Fix duplicate snapshot entries caused by parallel test runs.

    Explanation: We structure tests so that the context and non context call types of the
    test use the same cassettes and snapshot. However, when using the create or fix flags
    to inline-snapshot, it seemingly batches all the snapshot changes and then tries to apply
    them—with the result that if both tests failed due to a missing snapshot, they will
    both try to apply updates, and the result is an invalid snapshot that has two separate
    snapshot values. To avoid the needless duplication of snapshots, we instead have this
    simple helper which checks if a snapshot has duplicate values, and if so discards
    the extras before the snapshot is loaded from disk.
    """
    content = snapshot_file.read_text()
    lines = content.split("\n")

    result = []
    discard_this_section = False
    inside_string_literal = False
    for line in lines:
        if not discard_this_section:
            result.append(line)

        # Our duplicate snapshot detection logic depends on indentation, but may get a
        # false positive if we are inside a triple-quote multiline string literal.
        # So we disable it in that case.
        if line.endswith('="""\\'):
            inside_string_literal = True
        elif line == '"""':
            inside_string_literal = False

        if inside_string_literal:
            continue

        # With zero leading indentation, this always means we ended a snapshot.
        if line == ")" and discard_this_section:
            discard_this_section = False
            result.append(")")

        # With exactly four leading spaces, this only occurs when we are ending an
        # object being passed directly to the snapshot function. Include this closing brace
        # in the snapshot, but discard everything else we see until the snapshot call closes.
        if line == "    },":
            discard_this_section = True

    snapshot_file.write_text("\n".join(result))


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
    else:
        _fix_duplicate_snapshots(snapshot_file)
    if module_path in sys.modules:
        del sys.modules[module_path]

    e2e_dir = str(Path(__file__).parent.parent)
    if e2e_dir not in sys.path:
        sys.path.insert(0, e2e_dir)

    module = importlib.import_module(module_path)
    snapshot_variable = call_type.removesuffix("_context") + "_snapshot"
    return getattr(module, snapshot_variable)
