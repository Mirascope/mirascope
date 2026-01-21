"""End-to-end tests for NotFoundError when using nonexistent model IDs."""

import pytest

from mirascope import llm
from tests.e2e.conftest import E2E_MODEL_IDS


def get_nonexistent_model_id(model_id: llm.ModelId) -> llm.ModelId:
    """Generate a nonexistent model ID based on the provider."""
    # Extract model scope and preserve any suffix like :completions or :responses
    if "/" in model_id:
        parts = model_id.split("/")
        model_scope = parts[0]
        # Check if there's a suffix after the model name (like :completions or :responses)
        if ":" in parts[1]:
            _, suffix = parts[1].rsplit(":", 1)
            return f"{model_scope}/this-model-does-not-exist-12345:{suffix}"
        return f"{model_scope}/this-model-does-not-exist-12345"
    return "nonexistent-model-12345"


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_model_not_found(model_id: llm.ModelId) -> None:
    """Test that calling with a nonexistent model raises NotFoundError."""
    nonexistent_model = get_nonexistent_model_id(model_id)

    @llm.call(nonexistent_model)
    def test_call() -> str:
        return "This should fail with NotFoundError"

    with pytest.raises(llm.NotFoundError):
        test_call()


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_model_not_found_stream(model_id: llm.ModelId) -> None:
    """Test that streaming with a nonexistent model raises NotFoundError."""
    nonexistent_model = get_nonexistent_model_id(model_id)

    @llm.call(nonexistent_model)
    def test_stream() -> str:
        return "This should fail with NotFoundError"

    with pytest.raises(llm.NotFoundError):
        stream = test_stream.stream()
        stream.finish()
