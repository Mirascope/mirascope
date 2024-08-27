"""Tests the `openai._utils.setup_call` module."""

import inspect
from typing import ClassVar
from unittest.mock import MagicMock, patch

import pytest
from openai import OpenAI

from mirascope.core.base import ResponseModelConfigDict
from mirascope.core.openai._utils._setup_call import setup_call
from mirascope.core.openai.tool import OpenAITool


@pytest.fixture()
def mock_base_setup_call() -> MagicMock:
    """Returns the mock setup_call function."""
    mock_setup_call = MagicMock()
    mock_setup_call.return_value = [MagicMock() for _ in range(3)] + [{}]
    return mock_setup_call


@patch(
    "mirascope.core.openai._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.openai._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call(
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    """Tests the `setup_call` function."""
    mock_utils.setup_call = mock_base_setup_call
    fn = MagicMock()
    create, prompt_template, messages, tool_types, call_kwargs = setup_call(
        model="gpt-4o",
        client=None,
        fn=fn,
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params={},
        extract=False,
    )
    assert prompt_template == mock_base_setup_call.return_value[0]
    assert tool_types == mock_base_setup_call.return_value[2]
    assert "model" in call_kwargs and call_kwargs["model"] == "gpt-4o"
    assert "messages" in call_kwargs and call_kwargs["messages"] == messages
    mock_base_setup_call.assert_called_once_with(fn, {}, None, None, OpenAITool, {})
    mock_convert_message_params.assert_called_once_with(
        mock_base_setup_call.return_value[1]
    )
    assert messages == mock_convert_message_params.return_value
    assert inspect.signature(create) == inspect.signature(
        OpenAI().chat.completions.create
    )


@patch(
    "mirascope.core.openai._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.openai._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call_json_mode(
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    """Tests the `setup_call` function with JSON mode."""
    mock_utils.setup_call = mock_base_setup_call
    mock_utils.json_mode_content = MagicMock()
    mock_utils.json_mode_content.return_value = "\n\njson output"
    mock_base_setup_call.return_value[1] = [
        {"role": "user", "content": [{"type": "text", "text": "test"}]}
    ]

    class MockToolType(MagicMock):
        model_config: ClassVar[dict] = {}

    mock_base_setup_call.return_value[2] = [MockToolType]
    mock_base_setup_call.return_value[-1]["tools"] = MagicMock()
    mock_convert_message_params.side_effect = lambda x: x
    _, _, messages, _, call_kwargs = setup_call(
        model="gpt-4o",
        client=None,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=True,
        call_params={},
        extract=False,
    )
    assert messages[-1] == {"role": "user", "content": "json output"}
    assert "tools" not in call_kwargs

    mock_base_setup_call.return_value[1] = [
        {"role": "assistant", "content": [{"type": "text", "text": "test"}]}
    ]
    _, _, messages, _, call_kwargs = setup_call(
        model="gpt-4o",
        client=None,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=True,
        call_params={},
        extract=False,
    )
    assert isinstance(messages[-1], dict) and "content" in messages[-1]

    assert messages[-1] == {"role": "user", "content": "json output"}

    class Tool(OpenAITool):
        """A test tool."""

        title: str

        model_config = ResponseModelConfigDict(strict=True)

    mock_base_setup_call.return_value[2] = [Tool]
    _, _, _, _, call_kwargs = setup_call(
        model="gpt-4o",
        client=None,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=True,
        call_params={},
        extract=False,
    )
    assert "response_format" in call_kwargs and call_kwargs["response_format"] == {
        "type": "json_schema",
        "json_schema": {
            "name": "Tool",
            "description": "A test tool.",
            "strict": True,
            "schema": {
                "properties": {"title": {"type": "string"}},
                "required": ["title"],
                "type": "object",
                "additionalProperties": False,
            },
        },
    }


@patch(
    "mirascope.core.openai._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.openai._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call_extract(
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    """Tests the `setup_call` function with extraction."""

    class Tool(OpenAITool):
        """A test tool."""

        title: str

        model_config = ResponseModelConfigDict(strict=True)

    mock_base_setup_call.return_value[2] = [Tool]
    mock_utils.setup_call = mock_base_setup_call
    with pytest.warns(
        UserWarning,
        match="You must set `json_mode=True` to use `strict=True` response models. "
        "Ignoring `strict` and using tools for extraction.",
    ):
        _, _, _, _, call_kwargs = setup_call(
            model="gpt-4o",
            client=None,
            fn=MagicMock(),
            fn_args={},
            dynamic_config=None,
            tools=None,
            json_mode=False,
            call_params={},
            extract=True,
        )
    assert "tool_choice" in call_kwargs and call_kwargs["tool_choice"] == "required"
