"""End-to-end tests for a LLM call with all params set."""

from collections.abc import Sequence

import pytest

from mirascope import llm
from tests.e2e.conftest import E2E_MODEL_IDS
from tests.utils import Snapshot, snapshot_test


@llm.tool
def passphrase_test_tool(passphrase: str) -> str:
    """A tool that must be called with a passphrase."""
    if passphrase != "cake":
        raise ValueError(
            "Incorrect passhrase: The correct passphrase is 'cake'. Try again."
        )
    return "The cake is a lie."


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_call_with_tool_error(
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test synchronous call with all parameters to verify param handling and logging."""

    @llm.call(model_id, tools=[passphrase_test_tool])
    def use_test_tool() -> str:
        return (
            "Use the test tool to retrieve the secret phrase. The passphrase is 'portal"
        )

    outputs: Sequence[Sequence[llm.ToolOutput]] = []
    with snapshot_test(snapshot, caplog) as snap:
        response = use_test_tool()

        while response.tool_calls:
            tool_output = response.execute_tools()
            outputs.append(tool_output)
            response = response.resume(tool_output)

        snap.set_response(response)
        snap["tool_outputs"] = outputs
