"""End-to-end tests for resuming a LLM call with a different model and provider."""

from typing import TypedDict

import pytest

from mirascope import llm
from tests.e2e.conftest import (
    PROVIDER_MODEL_ID_PAIRS,
    Snapshot,
)
from tests.utils import exception_snapshot_dict, response_snapshot_dict


class ProviderAndModelId(TypedDict, total=True):
    provider: llm.Provider
    model_id: llm.ModelId


def default_provider_and_model(
    provider: llm.Provider,
) -> ProviderAndModelId:
    """Default provider and model that are distinct from the provider being tested.

    Used to ensure that we can test having the provider under test resume
    from a response that was created by a different provider.
    """
    if provider == "anthropic":
        return {"provider": "google", "model_id": "gemini-2.5-flash"}
    else:
        return {"provider": "anthropic", "model_id": "claude-sonnet-4-0"}


@pytest.mark.parametrize(
    "provider,model_id",
    PROVIDER_MODEL_ID_PAIRS,
)
@pytest.mark.vcr
def test_resume_with_override(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test call without context."""

    @llm.call(**default_provider_and_model(provider))
    def who_made_you() -> str:
        return "Who created you?"

    snapshot_data = {}
    try:
        response = who_made_you()

        with llm.model(provider=provider, model_id=model_id):
            response = response.resume("Can you double-check that?")

        snapshot_data["response"] = response_snapshot_dict(response)
    except Exception as e:
        snapshot_data["exception"] = exception_snapshot_dict(e)

    assert snapshot_data == snapshot


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_resume_with_override_context(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test call with context."""

    @llm.call(**default_provider_and_model(provider))
    def who_made_you(ctx: llm.Context[str]) -> str:
        return "Who created you?"

    snapshot_data = {}
    try:
        ctx = llm.Context(deps="Who created you?")
        response = who_made_you(ctx)

        with llm.model(provider=provider, model_id=model_id):
            response = response.resume(ctx, "Can you double-check that?")

        snapshot_data["response"] = response_snapshot_dict(response)
    except Exception as e:
        snapshot_data["exception"] = exception_snapshot_dict(e)

    assert snapshot_data == snapshot
