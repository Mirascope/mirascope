"""Tests the `mistral._utils.setup_call` module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mistralai import Chat, Mistral
from mistralai.models import (
    AssistantMessage,
    ChatCompletionResponse,
    CompletionChunk,
    TextChunk,
    UserMessage,
)
from pydantic import BaseModel

from mirascope.core.mistral._utils._convert_common_call_params import (
    convert_common_call_params,
)
from mirascope.core.mistral._utils._setup_call import setup_call
from mirascope.core.mistral.tool import MistralTool


@pytest.fixture()
def mock_base_setup_call() -> MagicMock:
    """Returns the mock setup_call function."""
    mock_setup_call = MagicMock()
    mock_setup_call.return_value = [MagicMock() for _ in range(3)] + [{}]
    return mock_setup_call


@patch(
    "mirascope.core.mistral._utils._setup_call.Mistral",
    return_value=MagicMock(),
)
@patch(
    "mirascope.core.mistral._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.mistral._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call(
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_mistral: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    """Tests the `setup_call` function."""
    mock_utils.setup_call = mock_base_setup_call
    mock_chat_iterator = MagicMock()
    mock_chat_iterator.__iter__.return_value = ["chat"]
    mock_mistral.chat = MagicMock()
    mock_mistral.chat.stream.return_value = mock_chat_iterator
    fn = MagicMock()
    create, prompt_template, messages, tool_types, call_kwargs = setup_call(
        model="mistral-large-latest",
        client=mock_mistral,
        fn=fn,
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params={},
        response_model=None,
        stream=False,
    )
    assert prompt_template == mock_base_setup_call.return_value[0]
    assert tool_types == mock_base_setup_call.return_value[2]
    assert "model" in call_kwargs and call_kwargs["model"] == "mistral-large-latest"
    assert "messages" in call_kwargs and call_kwargs["messages"] == messages
    mock_base_setup_call.assert_called_once_with(
        fn, {}, None, None, MistralTool, {}, convert_common_call_params
    )
    mock_convert_message_params.assert_called_once_with(
        mock_base_setup_call.return_value[1]
    )
    assert messages == mock_convert_message_params.return_value
    create(stream=False, **call_kwargs)
    mock_mistral.chat.complete.assert_called_once_with(**call_kwargs)
    stream = create(stream=True, **call_kwargs)
    mock_mistral.chat.stream.assert_called_once_with(**call_kwargs)
    assert next(stream) == "chat"  # pyright: ignore [reportArgumentType]


@patch(
    "mirascope.core.mistral._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.mistral._utils._setup_call._utils", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_async_setup_call(
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    """Tests the `setup_call` function."""
    mock_mistral_chat = AsyncMock(spec=ChatCompletionResponse)
    mock_mistral_chat.__name__ = "chat"

    mock_stream_response = AsyncMock(spec=CompletionChunk)
    mock_stream_response.text = "chat"

    class AsyncMockIterator:
        def __init__(self, item):
            self.item = iter(item)

        def __aiter__(self):
            return self

        async def __anext__(self):
            try:
                return next(self.item)
            except StopIteration:
                raise StopAsyncIteration

    mock_iterator = AsyncMockIterator([mock_stream_response])

    mock_client = MagicMock(spec=Mistral, name="mock_client")
    mock_client.chat = MagicMock(spec=Chat)
    mock_client.chat.stream_async = AsyncMock()
    mock_client.chat.stream_async.return_value = mock_iterator
    mock_client.chat.complete_async = AsyncMock()
    mock_client.chat.complete_async.return_value = mock_mistral_chat

    mock_utils.setup_call = mock_base_setup_call

    fn = AsyncMock()
    create, prompt_template, messages, tool_types, call_kwargs = setup_call(
        model="mistral-large-latest",
        client=mock_client,
        fn=fn,
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params={},
        response_model=None,
        stream=False,
    )
    assert prompt_template == mock_base_setup_call.return_value[0]
    assert tool_types == mock_base_setup_call.return_value[2]
    assert "model" in call_kwargs and call_kwargs["model"] == "mistral-large-latest"
    assert "messages" in call_kwargs and call_kwargs["messages"] == messages
    mock_base_setup_call.assert_called_once_with(
        fn, {}, None, None, MistralTool, {}, convert_common_call_params
    )
    mock_convert_message_params.assert_called_once_with(
        mock_base_setup_call.return_value[1]
    )

    chat = await create(stream=False, **call_kwargs)
    stream = await create(stream=True, **call_kwargs)
    result = []
    async for chunk in stream:
        result.append(chunk)
    assert result == [mock_stream_response]
    assert isinstance(chat, ChatCompletionResponse)
    assert isinstance(stream, AsyncMockIterator)


@pytest.mark.parametrize(
    "base_messages,expected_last_message",
    [
        (
            [UserMessage(content="test")],
            UserMessage(content="test\n\njson_mode_content"),
        ),
        (
            [UserMessage(content=[TextChunk(text="test")])],
            UserMessage(
                content=[
                    TextChunk(text="test", TYPE="text"),
                    TextChunk(text="\n\njson_mode_content", TYPE="text"),
                ]
            ),
        ),
        ([AssistantMessage(content="test")], UserMessage(content="json_mode_content")),
    ],
    ids=["string_content", "list_content", "assistant_message"],
)
@patch(
    "mirascope.core.mistral._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.mistral._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call_json_mode(
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
    base_messages,
    expected_last_message,
) -> None:
    """Tests the setup_call function with JSON mode for different message types and content formats.

    Args:
        mock_utils: Mock for utilities module
        mock_convert_message_params: Mock for message parameter conversion
        mock_base_setup_call: Mock for base setup call
        base_messages: Initial messages to test
        expected_last_message: Expected format of the last message after processing
    """
    # Setup mocks
    mock_utils.setup_call = mock_base_setup_call
    mock_json_mode_content = MagicMock()
    mock_json_mode_content.return_value = "\n\njson_mode_content"
    mock_utils.json_mode_content = mock_json_mode_content
    mock_base_setup_call.return_value[1] = base_messages
    mock_base_setup_call.return_value[-1]["tools"] = MagicMock()
    mock_convert_message_params.side_effect = lambda x: x

    # Execute setup_call
    _, _, messages, _, call_kwargs = setup_call(
        model="mistral-large-latest",
        client=None,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=True,
        call_params={},
        response_model=None,
        stream=False,
    )

    # Verify results
    assert messages[-1] == expected_last_message
    assert "tools" in call_kwargs


@patch(
    "mirascope.core.mistral._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.mistral._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call_extract(
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    """Tests the `setup_call` function with extraction."""
    mock_utils.setup_call = mock_base_setup_call
    _, _, _, _, call_kwargs = setup_call(
        model="mistral-large-latest",
        client=None,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params={},
        response_model=BaseModel,
        stream=False,
    )
    assert "tool_choice" in call_kwargs and call_kwargs["tool_choice"] == "any"
