"""End-to-end tests for LLM call with strict tool that has optional properties.

OpenAI strict mode requires ALL properties to be in the required array,
even if they have default values. This test verifies the fix works correctly.
"""

import pytest

from mirascope import llm
from tests.e2e.conftest import E2E_MODEL_IDS
from tests.utils import (
    Snapshot,
    snapshot_test,
)

# Include anthropic-beta/claude-sonnet-4-5 as it has strict support
E2E_MODEL_IDS = [*E2E_MODEL_IDS, "anthropic-beta/claude-sonnet-4-5"]


@llm.tool(strict=True)
def get_current_weather(location: str, unit: str = "fahrenheit") -> str:
    """Get the current weather in a given location.

    Args:
        location: The city and state, e.g. San Francisco, CA
        unit: The temperature unit to use (fahrenheit or celsius)
    """
    return f"The weather in {location} is 72°{unit[0].upper()}"


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_call_with_strict_tool_and_optional_properties(
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test a call with a strict tool that has optional properties.

    This validates that tools with default parameter values work correctly
    with OpenAI strict mode, which requires all properties to be required.
    """

    @llm.call(model_id, tools=[get_current_weather])
    def ask_weather() -> str:
        return "What's the weather like in San Francisco?"

    with snapshot_test(snapshot, caplog) as snap:
        response = ask_weather()
        snap.set_response(response)
