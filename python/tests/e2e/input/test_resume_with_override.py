"""End-to-end tests for resuming a LLM call with a different model and provider."""

from typing import TypedDict

import pytest

from mirascope import llm
from tests.e2e.conftest import (
    PROVIDER_MODEL_ID_PAIRS,
)
from tests.utils import Snapshot, snapshot_test


class ProviderAndModelId(TypedDict, total=True):
    provider: llm.Provider
    model_id: llm.ModelId


def default_model(
    provider: llm.Provider,
) -> llm.ModelId:
    """Default provider and model that are distinct from the provider being tested.

    Used to ensure that we can test having the provider under test resume
    from a response that was created by a different provider.
    """
    if provider == "google":
        return "anthropic/claude-sonnet-4-0"
    else:
        return "google/gemini-2.5-flash"


@pytest.mark.parametrize(
    "provider,model_id",
    PROVIDER_MODEL_ID_PAIRS,
)
@pytest.mark.vcr
def test_resume_with_override(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test call without context."""

    @llm.call(model_id=default_model(provider))
    def who_made_you() -> str:
        return "Who created you?"

    with snapshot_test(snapshot) as snap:
        response = who_made_you()

        with llm.model(model_id=model_id):
            response = response.resume("Can you double-check that?")

        snap.set_response(response)
