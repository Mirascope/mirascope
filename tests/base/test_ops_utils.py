"""Tests for the base ops utility functions."""
from typing import Any, Callable
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from pydantic import BaseModel

from mirascope.base.ops_utils import wrap_mirascope_class_functions
from mirascope.openai.calls import OpenAICall


def with_saving(cls):
    """Test decorator for saving."""

    def handle_after_call(
        self: BaseModel,
        fn: Callable[..., Any],
        result: Any,
        before_result: Any,
        **kwargs: dict[str, Any],
    ):
        pass

    handle_after_call_mock = MagicMock(wraps=handle_after_call)
    wrap_mirascope_class_functions(cls, None, handle_after_call_mock)
    cls.handle_after_call = handle_after_call_mock
    return cls


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_handle_after_call(
    mock_create,
    fixture_chat_completion: ChatCompletion,
):
    """Tests that handle_after_call gets called once after sync call."""
    mock_create.return_value = fixture_chat_completion

    @with_saving
    class TestModel(OpenAICall):
        prompt_template = """
        Test
        """
        api_key = "Test"

    test_model = TestModel()
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
):
    """Tests that handle_after_call gets called once after async call."""
    mock_create.return_value = fixture_chat_completion

    @with_saving
    class TestModel(OpenAICall):
        prompt_template = """
        Test
        """
        api_key = "Test"

    test_model = TestModel()
    await test_model.call_async()
    test_model.handle_after_call.assert_called_once()


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
def test_handle_after_call_stream(
    mock_create,
    fixture_chat_completion_chunks: list[ChatCompletionChunk],
):
    """Tests that handle_after_call gets called once after sync streaming."""
    mock_create.return_value = fixture_chat_completion_chunks

    @with_saving
    class TestModel(OpenAICall):
        prompt_template = """
        Test
        """
        api_key = "Test"

    test_model = TestModel()
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
):
    """Tests that handle_after_call gets called once after async streaming."""
    mock_create.return_value.__aiter__.return_value = fixture_chat_completion_chunks

    @with_saving
    class TestModel(OpenAICall):
        prompt_template = """
        Test
        """
        api_key = "Test"

    test_model = TestModel()
    async for chunk in test_model.stream_async():
        pass
    test_model.handle_after_call.assert_called_once()
