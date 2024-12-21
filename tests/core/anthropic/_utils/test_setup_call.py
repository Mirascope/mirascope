"""Tests the `anthropic._utils.setup_call` module."""

import inspect
from unittest.mock import MagicMock, patch

import pytest
from anthropic import Anthropic
from pydantic import BaseModel

from mirascope.core.anthropic._utils import convert_common_call_params
from mirascope.core.anthropic._utils._setup_call import setup_call
from mirascope.core.anthropic.tool import AnthropicTool


@pytest.fixture()
def mock_base_setup_call() -> MagicMock:
    """Returns the mock setup_call function."""
    mock_setup_call = MagicMock()
    mock_setup_call.return_value = [MagicMock() for _ in range(3)] + [{}]
    return mock_setup_call


@patch(
    "mirascope.core.anthropic._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.anthropic._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call(
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    """Tests the `setup_call` function."""
    mock_utils.setup_call = mock_base_setup_call
    mock_base_setup_call.return_value[3] = {"max_tokens": 1000}
    fn = MagicMock()
    create, prompt_template, messages, tool_types, call_kwargs = setup_call(
        model="claude-3-5-sonnet-20240620",
        client=None,
        fn=fn,
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params={"max_tokens": 1000},
        response_model=None,
        stream=False,
    )
    assert prompt_template == mock_base_setup_call.return_value[0]
    assert tool_types == mock_base_setup_call.return_value[2]
    assert (
        "model" in call_kwargs and call_kwargs["model"] == "claude-3-5-sonnet-20240620"
    )
    assert "messages" in call_kwargs and call_kwargs["messages"] == messages
    mock_base_setup_call.assert_called_once_with(
        fn,
        {},
        None,
        None,
        AnthropicTool,
        {"max_tokens": 1000},
        convert_common_call_params,
    )
    mock_convert_message_params.assert_called_once_with(
        mock_base_setup_call.return_value[1]
    )
    assert messages == mock_convert_message_params.return_value
    assert inspect.signature(create) == inspect.signature(Anthropic().messages.create)


@patch("mirascope.core.anthropic._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call_system_message(
    mock_utils: MagicMock, mock_base_setup_call: MagicMock
) -> None:
    mock_base_setup_call.return_value[1] = [
        {"role": "system", "content": [{"type": "text", "text": "test"}]}
    ]
    mock_utils.setup_call = mock_base_setup_call
    mock_base_setup_call.return_value[3] = {"max_tokens": 1000}
    _, _, _, _, call_kwargs = setup_call(
        model="claude-3-5-sonnet-20240620",
        client=None,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params={"max_tokens": 1000},
        response_model=None,
        stream=False,
    )
    assert "system" in call_kwargs
    assert call_kwargs["system"] == [{"type": "text", "text": "test"}]


@patch(
    "mirascope.core.anthropic._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.anthropic._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call_json_mode(
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    """Tests the `setup_call` function with JSON mode."""
    mock_utils.setup_call = mock_base_setup_call
    mock_utils.json_mode_content = MagicMock()
    mock_base_setup_call.return_value[1] = [
        {"role": "user", "content": [{"type": "text", "text": "test"}]}
    ]
    mock_base_setup_call.return_value[3] = {"max_tokens": 1000, "tools": MagicMock()}
    mock_convert_message_params.side_effect = lambda x: x
    _, _, messages, _, call_kwargs = setup_call(
        model="claude-3-5-sonnet-20240620",
        client=None,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=True,
        call_params={"max_tokens": 1000},
        response_model=None,
        stream=False,
    )
    assert messages[-1]["content"][-1] == {  # type: ignore
        "type": "text",
        "text": mock_utils.json_mode_content.return_value,
    }
    assert "tools" in call_kwargs

    mock_utils.json_mode_content.return_value = "\n\njson"
    mock_base_setup_call.return_value[1] = [{"role": "user", "content": "test"}]
    _, _, messages, _, call_kwargs = setup_call(
        model="claude-3-5-sonnet-20240620",
        client=None,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=True,
        call_params={"max_tokens": 1000},
        response_model=None,
        stream=False,
    )
    assert messages[-1]["content"] == "test\n\njson"  # type: ignore


@patch(
    "mirascope.core.anthropic._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.anthropic._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call_extract(
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    """Tests the `setup_call` function with extraction."""
    mock_base_setup_call.return_value[2] = [
        MagicMock(spec=AnthropicTool, __name__="tool")
    ]
    mock_base_setup_call.return_value[3] = {"max_tokens": 1000}
    mock_utils.setup_call = mock_base_setup_call
    _, _, _, tool_types, call_kwargs = setup_call(
        model="claude-3-5-sonnet-20240620",
        client=None,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params={"max_tokens": 1000},
        response_model=BaseModel,
        stream=False,
    )
    assert isinstance(tool_types, list)
    assert "tool_choice" in call_kwargs and call_kwargs["tool_choice"] == {
        "type": "tool",
        "name": tool_types[0]._name(),
    }
