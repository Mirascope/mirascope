"""Tests the `cohere._utils.setup_call` module."""

import os
from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest
from cohere import NonStreamedChatResponse
from cohere.types import ChatMessage
from pydantic import BaseModel

from mirascope.core.cohere._utils._convert_common_call_params import (
    convert_common_call_params,
)
from mirascope.core.cohere._utils._setup_call import setup_call
from mirascope.core.cohere.tool import CohereTool

os.environ["CO_API_KEY"] = "test"


@pytest.fixture()
def mock_base_setup_call() -> MagicMock:
    """Returns the mock setup_call function."""
    mock_setup_call = MagicMock()
    mock_setup_call.return_value = [MagicMock() for _ in range(3)] + [{}]
    return mock_setup_call


@patch(
    "mirascope.core.cohere._utils._setup_call.Client.chat_stream",
    new_callable=MagicMock,
)
@patch("mirascope.core.cohere._utils._setup_call.Client.chat", new_callable=MagicMock)
@patch(
    "mirascope.core.cohere._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.cohere._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call(
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_chat: MagicMock,
    mock_chat_stream: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    """Tests the `setup_call` function."""
    mock_chat.__name__ = "chat"
    mock_chat_stream.__name__ = "chat_stream"
    mock_utils.setup_call = mock_base_setup_call
    system_message = "system"
    preamble_message = "preamble"
    mock_base_setup_call.return_value[-1] = {
        "preamble": preamble_message,
    }
    mock_convert_message_params.return_value = [
        ChatMessage(role="SYSTEM", message=system_message),  # type: ignore
        ChatMessage(role="USER", message="history user"),  # type: ignore
        ChatMessage(
            role="CHATBOT",  # type: ignore
            message="history system",
        ),
        ChatMessage(
            role="USER",  # type: ignore
            message="content",
        ),
    ]
    fn = MagicMock()
    create, prompt_template, messages, tool_types, call_kwargs = setup_call(
        model="command-r-plus",
        client=None,
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
    assert "model" in call_kwargs and call_kwargs["model"] == "command-r-plus"
    assert "message" in call_kwargs and call_kwargs["message"] == messages[-1].message
    mock_base_setup_call.assert_called_once_with(
        fn, {}, None, None, CohereTool, {}, convert_common_call_params
    )
    mock_convert_message_params.assert_called_once_with(
        mock_base_setup_call.return_value[1]
    )
    assert messages == mock_convert_message_params.return_value
    assert "preamble" in call_kwargs
    assert "chat_history" in call_kwargs
    assert call_kwargs["preamble"] == f"{preamble_message}\n\n{system_message}"
    assert call_kwargs["chat_history"] == mock_convert_message_params.return_value[:-1]
    assert (
        call_kwargs["message"] == mock_convert_message_params.return_value[-1].message
    )
    mock_chat.return_value = MagicMock(spec=NonStreamedChatResponse)
    chat = create(stream=False, **call_kwargs)
    stream = create(stream=True, **call_kwargs)
    assert isinstance(chat, NonStreamedChatResponse)
    assert isinstance(stream, Iterator)


@patch(
    "mirascope.core.cohere._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.cohere._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call_json_mode(
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    """Tests the `setup_call` function with JSON mode."""
    mock_utils.setup_call = mock_base_setup_call
    mock_utils.json_mode_content.return_value = "content"
    mock_base_setup_call.return_value[1] = [
        ChatMessage(role="user", message="")  # type: ignore
    ]
    mock_base_setup_call.return_value[-1]["tools"] = MagicMock()
    mock_convert_message_params.side_effect = lambda x: x
    _, _, messages, _, call_kwargs = setup_call(
        model="command-r-plus",
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
    assert messages[-1] == ChatMessage(
        role="user",  # type: ignore
        message=mock_utils.json_mode_content.return_value,
        tool_calls=None,
    )
    assert "tools" in call_kwargs


@patch(
    "mirascope.core.cohere._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.cohere._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call_extract(
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    """Tests the `setup_call` function with extraction."""
    mock_utils.setup_call = mock_base_setup_call
    _, _, messages, _, call_kwargs = setup_call(
        model="command-r-plus",
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
    assert "model" in call_kwargs
    assert "message" in call_kwargs
    assert call_kwargs["model"] == "command-r-plus"
    assert call_kwargs["message"] == messages[-1].message
