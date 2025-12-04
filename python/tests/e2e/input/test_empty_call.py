"""End-to-end tests for a LLM call with audio input."""

import pytest

from mirascope import llm
from tests.e2e.conftest import E2E_MODEL_IDS
from tests.utils import (
    Snapshot,
    snapshot_test,
)


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_call_with_empty_string(
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test a call with an empty string content."""

    @llm.call(model_id)
    def empty_string() -> str:
        return ""

    with snapshot_test(snapshot, caplog) as snap:
        response = empty_string()
        snap.set_response(response)


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_call_with_two_empty_string(
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test a call with an empty string content."""

    @llm.call(model_id)
    def empty_string() -> list[str]:
        return ["", ""]

    with snapshot_test(snapshot, caplog) as snap:
        response = empty_string()
        snap.set_response(response)


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_call_with_empty_array(
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test a call with an empty array output."""

    @llm.call(model_id)
    def empty_array() -> list[llm.Message]:
        return []

    with snapshot_test(snapshot, caplog, extra_exceptions=[ValueError]) as snap:
        response = empty_array()
        snap.set_response(response)
