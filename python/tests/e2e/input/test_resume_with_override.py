"""End-to-end tests for resuming a LLM call with a different model and provider."""

import pytest

from mirascope import llm
from tests.e2e.conftest import (
    E2E_MODEL_IDS,
)
from tests.utils import Snapshot, snapshot_test


def default_model(
    model_id: llm.ModelId,
) -> llm.ModelId:
    """Default model from a different provider than the one being tested.

    Used to ensure that we can test having the provider under test resume
    from a response that was created by a different provider.
    """
    if model_id.startswith("google/"):
        return "anthropic/claude-sonnet-4-0"
    else:
        return "google/gemini-2.5-flash"


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_resume_with_override(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test call without context."""

    @llm.call(default_model(model_id))
    def who_made_you() -> str:
        return "Who created you?"

    with snapshot_test(snapshot) as snap:
        response = who_made_you()

        with llm.model(model_id):
            response = response.resume("Can you double-check that?")

        snap.set_response(response)
