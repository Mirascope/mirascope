"""End-to-end tests for NotFoundError when using nonexistent model IDs."""

import pytest

from mirascope import llm
from tests.e2e.conftest import E2E_MODEL_IDS


def get_nonexistent_model_id(model_id: llm.ModelId) -> llm.ModelId:
    """Generate a nonexistent model ID based on the provider."""
    # Extract model scope and preserve any suffix like :completions or :responses
    if "/" in model_id:
        parts = model_id.split("/")
        # Handle azure/openai/ prefix specially (two-level scope)
        if model_id.startswith("azure/openai/"):
            model_scope = "azure/openai"
            model_part = parts[2] if len(parts) > 2 else parts[1]
        else:
            model_scope = parts[0]
            model_part = parts[1]
        provider_model = model_part.split(":", 1)[0]
        bedrock_prefix = (
            "openai.nonexistent-model-12345"
            if provider_model.startswith("openai.")
            else "us.anthropic.nonexistent-model-12345-v1"
        )
        # Check if there's a suffix after the model name (like :completions or :responses)
        if ":" in model_part:
            _, suffix = model_part.rsplit(":", 1)
            if model_scope == "bedrock":
                return f"{model_scope}/{bedrock_prefix}:{suffix}"
            return f"{model_scope}/this-model-does-not-exist-12345:{suffix}"
        if model_scope == "bedrock":
            return f"{model_scope}/{bedrock_prefix}:0"
        return f"{model_scope}/this-model-does-not-exist-12345"
    return "nonexistent-model-12345"


def _is_azure_model(model_id: llm.ModelId) -> bool:
    return model_id.startswith("azure/openai/")


def _is_bedrock_model(model_id: llm.ModelId) -> bool:
    return model_id.startswith("bedrock/")


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_model_not_found(model_id: llm.ModelId) -> None:
    """Test that calling with a nonexistent model raises NotFoundError."""
    nonexistent_model = get_nonexistent_model_id(model_id)
    # Azure and Bedrock return BadRequestError for invalid model identifiers
    expected_error = (
        llm.BadRequestError
        if _is_azure_model(model_id) or _is_bedrock_model(model_id)
        else llm.NotFoundError
    )

    @llm.call(nonexistent_model)
    def test_call() -> str:
        return "This should fail with NotFoundError"

    with pytest.raises(expected_error):
        test_call()


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_model_not_found_stream(model_id: llm.ModelId) -> None:
    """Test that streaming with a nonexistent model raises NotFoundError."""
    nonexistent_model = get_nonexistent_model_id(model_id)
    # Azure and Bedrock return BadRequestError for invalid model identifiers
    expected_error = (
        llm.BadRequestError
        if _is_azure_model(model_id) or _is_bedrock_model(model_id)
        else llm.NotFoundError
    )

    @llm.call(nonexistent_model)
    def test_stream() -> str:
        return "This should fail with NotFoundError"

    with pytest.raises(expected_error):
        stream = test_stream.stream()
        stream.finish()
