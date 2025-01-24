"""Tests the `google._utils.setup_call` module."""

from unittest.mock import MagicMock, patch

import pytest
from google.genai import Client
from google.genai.types import (
    FunctionCallingConfigMode,
    GenerateContentConfig,
)
from pydantic import BaseModel

from mirascope.core.google._utils._convert_common_call_params import (
    convert_common_call_params,
)
from mirascope.core.google._utils._setup_call import setup_call
from mirascope.core.google.tool import GoogleTool


@pytest.fixture()
def mock_base_setup_call() -> MagicMock:
    """Returns the mock setup_call function."""
    mock_setup_call = MagicMock()
    mock_setup_call.return_value = [MagicMock() for _ in range(3)] + [{}]
    return mock_setup_call


@patch(
    "mirascope.core.google._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.google._utils._setup_call._utils", new_callable=MagicMock)
@patch("mirascope.core.google._utils._setup_call.Client", new_callable=MagicMock)
@patch(
    "google.genai.models.Models.generate_content",
    new_callable=MagicMock,
)
def test_setup_call(
    mock_generate_content: MagicMock,
    mock_client: MagicMock,
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    """Tests the `setup_call` function."""
    client = Client()
    mock_client.return_value = client
    mock_utils.setup_call = mock_base_setup_call
    fn = MagicMock()
    create, prompt_template, messages, tool_types, call_kwargs = setup_call(
        model="google-1.5-flash",
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
    assert "contents" in call_kwargs and call_kwargs["contents"] == messages
    mock_base_setup_call.assert_called_once_with(
        fn, {}, None, None, GoogleTool, {}, convert_common_call_params
    )
    mock_convert_message_params.assert_called_once_with(
        mock_base_setup_call.return_value[1]
    )
    assert messages == mock_convert_message_params.return_value
    mock_client.assert_called_once_with()
    assert create(**call_kwargs)
    mock_generate_content.assert_called_once_with(**call_kwargs)
    mock_generate_content.reset_mock()
    assert create(stream=True, **call_kwargs)
    mock_generate_content.assert_called_once_with(**call_kwargs, stream=True)
    mock_generate_content.reset_mock()
    assert create(stream=False, **call_kwargs)
    mock_generate_content.assert_called_once_with(**call_kwargs)


@pytest.mark.parametrize(
    "generation_config_type,expected",
    [
        [
            dict,
            {
                "candidate_count": 1,
                "max_output_tokens": 100,
                "response_mime_type": "application/json",
                "response_schema": None,
                "stop_sequences": ["\n"],
                "temperature": 0.5,
                "top_k": 0,
                "top_p": 0,
            },
        ],
        [
            GenerateContentConfig,
            {
                "audio_timestamp": None,
                "automatic_function_calling": None,
                "cached_content": None,
                "candidate_count": 1,
                "frequency_penalty": None,
                "logprobs": None,
                "max_output_tokens": 100,
                "media_resolution": None,
                "presence_penalty": None,
                "response_logprobs": None,
                "response_mime_type": "application/json",
                "response_modalities": None,
                "response_schema": None,
                "routing_config": None,
                "safety_settings": None,
                "seed": None,
                "speech_config": None,
                "stop_sequences": ["\n"],
                "system_instruction": None,
                "temperature": 0.5,
                "thinking_config": None,
                "tool_config": None,
                "tools": None,
                "top_k": 0.0,
                "top_p": 0.0,
            },
        ],
    ],
)
@patch(
    "mirascope.core.google._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.google._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call_json_mode(
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
    generation_config_type: type,
    expected: dict,
) -> None:
    """Tests the `setup_call` function with JSON mode."""
    mock_utils.setup_call = mock_base_setup_call
    mock_utils.json_mode_content = MagicMock()
    mock_base_setup_call.return_value[1] = [
        {"role": "user", "parts": [{"type": "text", "text": "test"}]}
    ]
    mock_base_setup_call.return_value[-1]["tools"] = MagicMock()
    mock_base_setup_call.return_value[-1]["config"] = generation_config_type(
        candidate_count=1,
        max_output_tokens=100,
        response_mime_type="application/xml",
        response_schema=None,
        stop_sequences=["\n"],
        temperature=0.5,
        top_k=0,
        top_p=0,
    )
    mock_convert_message_params.side_effect = lambda x: x
    _, _, messages, _, call_kwargs = setup_call(
        model="google-1.5-flash",
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
    assert isinstance(messages[-1], dict)
    assert "parts" in messages[-1]
    assert isinstance(messages[-1]["parts"], list)
    assert messages[-1]["parts"][-1] == mock_utils.json_mode_content.return_value
    assert "tools" in call_kwargs
    assert "config" in call_kwargs
    assert call_kwargs["config"] == expected


@patch(
    "mirascope.core.google._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.google._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call_extract(
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    """Tests the `setup_call` function with extraction."""
    mock_tool = MagicMock()
    mock_tool._name.side_effect = lambda: "test"
    mock_base_setup_call.return_value[2] = [mock_tool]
    mock_utils.setup_call = mock_base_setup_call
    _, _, _, _, call_kwargs = setup_call(
        model="google-1.5-flash",
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
    assert "config" in call_kwargs and isinstance(call_kwargs["config"], dict)
    config = call_kwargs["config"]
    assert "tool_config" in config and isinstance(config["tool_config"], dict)
    assert "function_calling_config" in config["tool_config"] and isinstance(
        config["tool_config"]["function_calling_config"], dict
    )
    tool_config = config["tool_config"]
    assert tool_config["function_calling_config"] == {
        "allowed_function_names": ["test"],
        "mode": FunctionCallingConfigMode.ANY,
    }
