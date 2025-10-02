"""Test Google-specific behavior around max tokens and automatic thinking.

Gemini 2.5 automatically thinks about the prompt before responding, and if the max_tokens
is low, then thinking may fully exhaust the token budget, resulting in no output.

In this case, it's we ensure that the MAX_TOKENS finish reason is set, as otherwise the
empty response may be confusing.
"""

import pytest

from mirascope import llm


@pytest.mark.parametrize(
    "provider,model_id",
    [("google", "gemini-2.5-flash")],
)
@pytest.mark.vcr
def test_google_max_tokens_edge_case_sync(
    provider: llm.Provider, model_id: llm.ModelId
) -> None:
    """Test synchronous call where Google emits no output due to max tokens."""

    @llm.call(provider=provider, model_id=model_id, max_tokens=50)
    def max_tokens() -> str:
        return "List all U.S. states, sorted by the number of consonants in their name, ascending."

    @llm.call(provider="google", model_id="gemini-2.5-flash")
    def no_output() -> str:
        return "EMIT NO OUTPUT WHATSOEVER."

    max_tokens_response = max_tokens()
    no_output_response = no_output()

    assert not max_tokens_response.content
    assert max_tokens_response.finish_reason == llm.FinishReason.MAX_TOKENS

    assert not no_output_response.content
    assert no_output_response.finish_reason is None


@pytest.mark.parametrize(
    "provider,model_id",
    [("google", "gemini-2.5-flash")],
)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_google_max_tokens_edge_case_async(
    provider: llm.Provider, model_id: llm.ModelId
) -> None:
    """Test asynchronous call where Google emits no output due to max tokens."""

    @llm.call(provider=provider, model_id=model_id, max_tokens=50)
    async def max_tokens() -> str:
        return "List all U.S. states, sorted by the number of consonants in their name, ascending."

    @llm.call(provider="google", model_id="gemini-2.5-flash")
    async def no_output() -> str:
        return "EMIT NO OUTPUT WHATSOEVER."

    max_tokens_response = await max_tokens()
    no_output_response = await no_output()

    assert not max_tokens_response.content
    assert max_tokens_response.finish_reason == llm.FinishReason.MAX_TOKENS

    assert not no_output_response.content
    assert no_output_response.finish_reason is None


@pytest.mark.parametrize(
    "provider,model_id",
    [("google", "gemini-2.5-flash")],
)
@pytest.mark.vcr
def test_google_max_tokens_edge_case_stream(
    provider: llm.Provider, model_id: llm.ModelId
) -> None:
    """Test streaming call where Google emits no output due to max tokens."""

    @llm.call(provider=provider, model_id=model_id, max_tokens=50)
    def max_tokens() -> str:
        return "List all U.S. states, sorted by the number of consonants in their name, ascending."

    @llm.call(provider="google", model_id="gemini-2.5-flash")
    def no_output() -> str:
        return "EMIT NO OUTPUT WHATSOEVER."

    max_tokens_response = max_tokens.stream().finish()
    no_output_response = no_output.stream().finish()

    assert not max_tokens_response.content
    assert max_tokens_response.finish_reason == llm.FinishReason.MAX_TOKENS

    assert not no_output_response.content
    # Known false positive: In the sync stream case we mis-classify the empty response
    # as being limited due to MAX_TOKENS
    assert no_output_response.finish_reason == llm.FinishReason.MAX_TOKENS


@pytest.mark.parametrize(
    "provider,model_id",
    [("google", "gemini-2.5-flash")],
)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_google_max_tokens_edge_case_async_stream(
    provider: llm.Provider, model_id: llm.ModelId
) -> None:
    """Test async streaming call where Google emits no output due to max tokens."""

    @llm.call(provider=provider, model_id=model_id, max_tokens=50)
    async def max_tokens() -> str:
        return "List all U.S. states, sorted by the number of consonants in their name, ascending."

    @llm.call(provider="google", model_id="gemini-2.5-flash")
    async def no_output() -> str:
        return "EMIT NO OUTPUT WHATSOEVER."

    max_tokens_response = await max_tokens.stream()
    await max_tokens_response.finish()
    no_output_response = await no_output.stream()
    await no_output_response.finish()

    assert not max_tokens_response.content
    assert max_tokens_response.finish_reason == llm.FinishReason.MAX_TOKENS

    assert not no_output_response.content
    # In the async stream case, Google emits an empty block so we can classify the finish
    # reason correctly.
    assert no_output_response.finish_reason is None
