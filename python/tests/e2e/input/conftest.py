"""Configuration for input tests (request encoding tests)."""

from __future__ import annotations

import importlib
from collections.abc import Generator
from contextlib import nullcontext
from pathlib import Path
from typing import Any

import pytest
import vcr
from pytest import FixtureRequest

from mirascope import llm
from tests.e2e.conftest import SNAPSHOT_IMPORT_SYMBOLS, VCRConfig
from tests.utils import Snapshot


@pytest.fixture(scope="session")
def vcr_config(vcr_config: VCRConfig) -> VCRConfig:
    """Override VCR config to set cassette directory for input tests.

    Inherits the base VCR configuration from tests/e2e/conftest.py and adds
    the cassette_library_dir to point to the input/cassettes directory.
    """
    vcr_config["cassette_library_dir"] = str(Path(__file__).parent / "cassettes")
    return vcr_config


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


@pytest.fixture
def vcr_cassette_name(
    request: FixtureRequest,
    provider: llm.Provider,
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
) -> str | None:
    """Generate VCR cassette name based on test name, provider, model, and formatting_mode.

    Input tests use a single cassette per test (no call type variants).

    Structure:
    - Without formatting_mode: {scenario}/{provider}_{model_id}
    - With formatting_mode: {scenario}/{formatting_mode}/{provider}_{model_id}

    Returns None for xAI provider to skip VCR (xAI tests run with --use-real-grok flag).
    """
    # xAI uses gRPC, so skip VCR cassettes (requires --use-real-grok to run)
    if provider == "xai":
        return None

    test_name = request.node.name
    scenario = _extract_scenario_from_test_name(test_name)

    provider_str = provider.replace(":", "_")
    model_id_str = model_id.replace("-", "_").replace(".", "_")

    if formatting_mode is None:
        return f"{scenario}/{provider_str}_{model_id_str}.yaml"
    else:
        return f"{scenario}/{formatting_mode}/{provider_str}_{model_id_str}.yaml"


@pytest.fixture
def snapshot(
    request: FixtureRequest,
    provider: llm.Provider,
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
) -> Snapshot:
    """Get snapshot for current test configuration.

    Creates snapshot files with a single 'test_snapshot' variable.

    Structure:
    - Without formatting_mode: snapshots/{scenario}/{provider}_{model_id}_snapshots.py
    - With formatting_mode: snapshots/{scenario}/{formatting_mode}/{provider}_{model_id}_snapshots.py
    """
    test_name = request.node.name
    scenario = _extract_scenario_from_test_name(test_name)
    provider_str = provider.replace(":", "_")
    model_id_str = model_id.replace("-", "_").replace(".", "_")

    file_name = f"{provider_str}_{model_id_str}_snapshots"

    if formatting_mode is None:
        module_path = f"e2e.input.snapshots.{scenario}.{file_name}"
        snapshot_file = (
            Path(__file__).parent / "snapshots" / scenario / f"{file_name}.py"
        )
    else:
        module_path = f"e2e.input.snapshots.{scenario}.{formatting_mode}.{file_name}"
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
            "test_snapshot = snapshot()\n"
        )

        snapshot_file.write_text(content)

    module = importlib.import_module(module_path)
    return module.test_snapshot


@pytest.fixture
def vcr_cassette(
    request: FixtureRequest, vcr_cassette_name: str | None, vcr_config: dict[str, Any]
) -> Generator[Any, None, None]:
    """Override pytest-vcr's vcr_cassette to handle None cassette_name for xAI.

    When vcr_cassette_name is None (e.g., for xAI provider which uses gRPC and
    cannot be recorded with VCR), this fixture returns a no-op context manager.

    Args:
        request: Pytest fixture request.
        vcr_cassette_name: Cassette name or None to skip VCR.
        vcr_config: VCR configuration dict.

    Yields:
        VCR cassette or None if skipped.
    """
    if vcr_cassette_name is None:
        # xAI uses gRPC and cannot be recorded with VCR, skip VCR
        with nullcontext() as cassette:
            yield cassette
    else:
        # Use normal VCR for HTTP-based providers
        with vcr.VCR(**vcr_config).use_cassette(vcr_cassette_name) as cassette:
            yield cassette
