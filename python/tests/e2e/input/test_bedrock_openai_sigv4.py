"""End-to-end test for Bedrock OpenAI SigV4 authentication."""

import pytest

from mirascope import llm
from mirascope.llm.providers.bedrock.openai import BedrockOpenAIProvider

BEDROCK_OPENAI_SIGV4_MODEL_IDS: list[llm.ModelId] = [
    "bedrock/openai.gpt-oss-20b-1:0",
]


@pytest.mark.parametrize("model_id", BEDROCK_OPENAI_SIGV4_MODEL_IDS)
@pytest.mark.vcr
def test_bedrock_openai_sigv4_call(
    model_id: llm.ModelId,
    reset_provider_registry: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test Bedrock OpenAI call with SigV4 authentication."""
    monkeypatch.delenv("AWS_BEARER_TOKEN_BEDROCK", raising=False)
    provider = BedrockOpenAIProvider(aws_region="us-east-1")
    llm.register_provider(provider)

    @llm.call(model_id)
    def simple_call() -> str:
        return "Say hello in one word."

    response = simple_call()
    assert response.content is not None
    assert len(response.content) > 0
