"""Tests the `fallback` module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from anthropic import RateLimitError as AnthropicRateLimitError
from httpx import Request, Response
from openai import RateLimitError as OpenAIRateLimitError

from mirascope import llm
from mirascope.retries.fallback import FallbackError, fallback


@patch(
    "anthropic.resources.messages.Messages.create",
    new_callable=MagicMock,
    side_effect=AnthropicRateLimitError(
        message="",
        response=Response(429, request=Request(method="", url="")),
        body=None,
    ),
)
@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
    side_effect=OpenAIRateLimitError(
        message="",
        response=Response(429, request=Request(method="", url="")),
        body=None,
    ),
)
def test_fallback(mock_openai_create: MagicMock, mock_anthropic_create: MagicMock):
    @fallback(
        OpenAIRateLimitError,
        [
            {
                "catch": AnthropicRateLimitError,
                "provider": "anthropic",
                "model": "claude-3-5-sonnet-latest",
            }
        ],
    )
    @llm.call("openai", "gpt-4o-mini")
    def answer_question(question: str) -> str:
        return question

    with pytest.raises(FallbackError):
        answer_question("What is the meaning of life?")


@patch(
    "mirascope.llm.override",
    new_callable=MagicMock,
    return_value=MagicMock(),
)
@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
    side_effect=OpenAIRateLimitError(
        message="",
        response=Response(429, request=Request(method="", url="")),
        body=None,
    ),
)
def test_fallback_success(mock_openai_create: MagicMock, mock_llm_override: MagicMock):
    @fallback(
        OpenAIRateLimitError,
        [
            {
                "catch": AnthropicRateLimitError,
                "provider": "anthropic",
                "model": "claude-3-5-sonnet-latest",
            }
        ],
    )
    @llm.call("openai", "gpt-4o-mini")
    def answer_question(question: str) -> str:
        return question

    response = answer_question("What is the meaning of life?")
    assert hasattr(response, "_caught")
    assert isinstance(response._caught[0], OpenAIRateLimitError)


@patch(
    "anthropic.resources.messages.AsyncMessages.create",
    new_callable=MagicMock,
    side_effect=AnthropicRateLimitError(
        message="",
        response=Response(429, request=Request(method="", url="")),
        body=None,
    ),
)
@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=MagicMock,
    side_effect=OpenAIRateLimitError(
        message="",
        response=Response(429, request=Request(method="", url="")),
        body=None,
    ),
)
@pytest.mark.asyncio
async def test_fallback_async(
    mock_openai_create: MagicMock, mock_anthropic_create: MagicMock
):
    @fallback(
        OpenAIRateLimitError,
        [
            {
                "catch": AnthropicRateLimitError,
                "provider": "anthropic",
                "model": "claude-3-5-sonnet-latest",
            }
        ],
    )
    @llm.call("openai", "gpt-4o-mini")
    async def answer_question_async(question: str) -> str:
        return question

    with pytest.raises(FallbackError):
        await answer_question_async("What is the meaning of life?")


@patch(
    "mirascope.llm.override",
    new_callable=MagicMock,
    return_value=AsyncMock(),
)
@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=MagicMock,
    side_effect=OpenAIRateLimitError(
        message="",
        response=Response(429, request=Request(method="", url="")),
        body=None,
    ),
)
@pytest.mark.asyncio
async def test_fallback_async_success(
    mock_openai_call: AsyncMock, mock_llm_override: MagicMock
):
    @fallback(
        OpenAIRateLimitError,
        [
            {
                "catch": AnthropicRateLimitError,
                "provider": "anthropic",
                "model": "claude-3-5-sonnet-latest",
            }
        ],
    )
    @llm.call("openai", "gpt-4o-mini")
    async def answer_question(question: str) -> str:
        return question

    response = await answer_question("What is the meaning of life?")
    assert hasattr(response, "_caught")
    assert isinstance(response._caught[0], OpenAIRateLimitError)
