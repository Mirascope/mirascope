"""Configuration for input tests (request encoding tests)."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from pytest import FixtureRequest

from mirascope import llm
from tests.e2e.conftest import SNAPSHOT_IMPORT_SYMBOLS
from tests.utils import Snapshot


def _extract_scenario_from_test_name(test_name: str) -> str:
    """Extract scenario name from test name.

    Unlike output tests, input tests don't follow a strict {scenario}_{call_type}
    convention. This function extracts everything after 'test_' and before any
    parametrization markers.

    Examples:
        test_call_with_params_sync[...] -> "call_with_params_sync"
        test_all_params_includes_every_param -> "all_params_includes_every_param"

    Args:
        test_name: The full test name from pytest

    Returns:
        The scenario portion of the test name
    """
    name = test_name.split("[")[0]  # Remove parametrization
    if not name.startswith("test_"):
        raise ValueError(f"Test name must start with 'test_': {test_name}")

    return name


def _get_extra_segments(request: FixtureRequest) -> list[str]:
    """Get additional path segments from optional parametrized fixtures.

    Returns path segments for formatting_mode and mime_type if present.
    """
    segments: list[str] = []
    for name in ("formatting_mode", "mime_type"):
        if name in request.fixturenames:
            value = request.getfixturevalue(name)
            if value is not None:
                segment = value.replace("/", "_") if "/" in value else value
                segments.append(segment)
    return segments


@pytest.fixture
def vcr_cassette_name(
    request: FixtureRequest,
    model_id: llm.ModelId,
) -> str:
    """Generate VCR cassette name based on test name, provider, model, and extra params.

    Input tests use a single cassette per test (no call type variants).

    Structure: {scenario}[/{extra_segment}...]/{model_id}
    """
    test_name = request.node.name
    scenario = _extract_scenario_from_test_name(test_name)

    model_id_str = (
        model_id.replace("-", "_").replace(".", "_").replace(":", "_").replace("/", "_")
    )

    segments = [scenario, *_get_extra_segments(request), model_id_str]
    return "/".join(segments)


@pytest.fixture
def snapshot(
    request: FixtureRequest,
    model_id: llm.ModelId,
) -> Snapshot:
    """Get snapshot for current test configuration.

    Creates snapshot files with a single 'test_snapshot' variable.

    Structure: snapshots/{scenario}[/{extra_segment}...]/{model_id}_snapshots.py
    """
    test_name = request.node.name
    scenario = _extract_scenario_from_test_name(test_name)
    model_id_str = (
        model_id.replace("-", "_").replace(".", "_").replace(":", "_").replace("/", "_")
    )
    file_name = f"{model_id_str}_snapshots"

    extra_segments = _get_extra_segments(request)

    if extra_segments:
        extra_path = "/".join(extra_segments)
        extra_dotpath = ".".join(extra_segments)
        module_path = f"e2e.input.snapshots.{scenario}.{extra_dotpath}.{file_name}"
        snapshot_file = (
            Path(__file__).parent
            / "snapshots"
            / scenario
            / extra_path
            / f"{file_name}.py"
        )
    else:
        module_path = f"e2e.input.snapshots.{scenario}.{file_name}"
        snapshot_file = (
            Path(__file__).parent / "snapshots" / scenario / f"{file_name}.py"
        )

    if not snapshot_file.exists():
        snapshot_file.parent.mkdir(parents=True, exist_ok=True)

        content = (
            "from inline_snapshot import snapshot\n\n"
            f"from mirascope.llm import {', '.join(SNAPSHOT_IMPORT_SYMBOLS)}\n\n"
            "test_snapshot = snapshot()\n"
        )

        snapshot_file.write_text(content)

    module = importlib.import_module(module_path)
    return module.test_snapshot
