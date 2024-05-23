"""Tests for the base ops utility functions."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from mirascope.base.calls import BaseCall
from mirascope.base.ops_utils import get_wrapped_call


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_handle_after_call(
    mock_create,
    fixture_chat_completion: ChatCompletion,
    fixture_with_saving,
):
    """Tests that handle_after_call gets called once after sync call."""
    mock_create.return_value = fixture_chat_completion

    test_model = fixture_with_saving()
    test_model.call()
    test_model.handle_after_call.assert_called_once()


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_handle_after_call_async(
    mock_create,
    fixture_chat_completion: ChatCompletion,
    fixture_with_saving,
):
    """Tests that handle_after_call gets called once after async call."""
    mock_create.return_value = fixture_chat_completion
    test_model = fixture_with_saving()
    await test_model.call_async()
    test_model.handle_after_call.assert_called_once()


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_handle_after_call_stream(
    mock_create,
    fixture_chat_completion_chunks: list[ChatCompletionChunk],
    fixture_with_saving,
):
    """Tests that handle_after_call gets called once after sync streaming."""
    mock_create.return_value = fixture_chat_completion_chunks

    test_model = fixture_with_saving()
    for chunk in test_model.stream():
        pass
    test_model.handle_after_call.assert_called_once()


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_handle_after_call_stream_async(
    mock_create,
    fixture_chat_completion_chunks: list[ChatCompletionChunk],
    fixture_with_saving,
):
    """Tests that handle_after_call gets called once after async streaming."""
    mock_create.return_value.__aiter__.return_value = fixture_chat_completion_chunks

    test_model = fixture_with_saving()
    async for chunk in test_model.stream_async():
        pass
    test_model.handle_after_call.assert_called_once()


def test_get_wrapped_call():
    """Tests that get wrapped call properly returns the class if no provided llm_ops"""

    def wrap_me(): ...  # pragma: no cover

    class Foo(BaseCall): ...

    assert get_wrapped_call(wrap_me, Foo) == wrap_me
