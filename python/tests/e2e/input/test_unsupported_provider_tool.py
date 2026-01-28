"""End-to-end tests for prompt caching."""

import pytest

from mirascope import llm
from tests.e2e.conftest import E2E_MODEL_IDS
from tests.utils import Snapshot, snapshot_test


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_unsupported_provider_tool(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test handling of a provider tool that is not supported by the provider."""

    tool = llm.ProviderTool(name="Unsupported Test Tool")

    @llm.call(model_id, tools=[tool])
    def say_hi() -> str:
        return "Say hi back"

    with snapshot_test(snapshot) as snap:
        snap.set_response(say_hi())
