"""Configuration for output tests (response decoding tests)."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Literal, get_args

import pytest
from pytest import FixtureRequest

from mirascope import llm
from tests.e2e.conftest import SNAPSHOT_IMPORT_SYMBOLS
from tests.utils import Snapshot

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
"""The basic "call types" that all output tests should cover."""

CALL_TYPES: tuple[CallType, ...] = get_args(CallType)


def _parse_test_name(test_name: str) -> tuple[str, CallType]:
    """Parse test name following convention: test_{SCENARIO}_{CALL_TYPE}

    Examples:
        test_simple_call_sync -> ("simple_call", "sync")
        test_simple_call_async_stream -> ("simple_call", "async_stream")
        test_tool_call_sync_context -> ("tool_call", "sync_context")

    Raises:
        ValueError: If test name doesn't follow expected convention
    """
    name = test_name.split("[")[0]  # Remove parametrization
    if not name.startswith("test_"):
        raise ValueError(f"Test name must start with 'test_': {test_name}")

    # Special case for the test_prompt tests: they use the same snapshots and cassettes
    # as test_call.
    name = name.replace("test_prompt", "test_call")

    # Known call_types to look for at the end (order matters - check longer overlaps first)
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
        "Follow convention: test_{{scenario}}_{{call_suffix}}"
    )


@pytest.fixture
def vcr_cassette_name(
    request: FixtureRequest,
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
) -> str:
    """Generate VCR cassette name based on test name, model, and formatting_mode.

    Structure:
    - Without formatting_mode: {scenario}/{model_id}/{call_type}
    - With formatting_mode: {scenario}/{formatting_mode}/{model_id}/{call_type}
    """
    test_name = request.node.name
    scenario, call_type = _parse_test_name(test_name)

    model_id_str = (
        model_id.replace("-", "_").replace(".", "_").replace(":", "_").replace("/", "_")
    )

    # Context and non-context calls share the same cassettes.
    cassette_call_type = call_type.replace("_context", "")

    if formatting_mode is None:
        return f"{scenario}/{model_id_str}/{cassette_call_type}"
    else:
        return f"{scenario}/{formatting_mode}/{model_id_str}/{cassette_call_type}"


@pytest.fixture
def snapshot(
    request: FixtureRequest,
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
) -> Snapshot:
    """Get snapshot for current test configuration.

    Creates snapshot files with 4 snapshot variables:
    - sync_snapshot
    - async_snapshot
    - stream_snapshot
    - async_stream_snapshot

    Structure:
    - Without formatting_mode: snapshots/{scenario}/{model_id}_snapshots.py
    - With formatting_mode: snapshots/{scenario}/{formatting_mode}/{model_id}_snapshots.py
    """
    test_name = request.node.name
    scenario, call_type = _parse_test_name(test_name)
    model_id_str = (
        model_id.replace("-", "_").replace(".", "_").replace(":", "_").replace("/", "_")
    )

    file_name = f"{model_id_str}_snapshots"

    if formatting_mode is None:
        module_path = f"e2e.output.snapshots.{scenario}.{file_name}"
        snapshot_file = (
            Path(__file__).parent / "snapshots" / scenario / f"{file_name}.py"
        )
    else:
        module_path = f"e2e.output.snapshots.{scenario}.{formatting_mode}.{file_name}"
        snapshot_file = (
            Path(__file__).parent
            / "snapshots"
            / scenario
            / formatting_mode
            / f"{file_name}.py"
        )

    if not snapshot_file.exists():
        snapshot_file.parent.mkdir(parents=True, exist_ok=True)

        content = (
            "from inline_snapshot import snapshot\n\n"
            f"from mirascope.llm import {', '.join(SNAPSHOT_IMPORT_SYMBOLS)}\n\n"
            "sync_snapshot = snapshot()\n"
            "async_snapshot = snapshot()\n"
            "stream_snapshot = snapshot()\n"
            "async_stream_snapshot = snapshot()\n"
        )

        snapshot_file.write_text(content)

    module = importlib.import_module(module_path)
    snapshot_variable = call_type.removesuffix("_context") + "_snapshot"
    return getattr(module, snapshot_variable)
