"""Tests the `gemini._utils.setup_call` module."""

from unittest.mock import MagicMock, patch

import pytest
from google.generativeai import GenerativeModel  # type: ignore
from google.generativeai.types import GenerationConfig
from google.generativeai.types.content_types import ToolConfigDict
from pydantic import BaseModel

from mirascope.core.gemini._utils._convert_common_call_params import (
    convert_common_call_params,
)
from mirascope.core.gemini._utils._setup_call import setup_call
from mirascope.core.gemini.tool import GeminiTool


@pytest.fixture()
def mock_base_setup_call() -> MagicMock:
    """Returns the mock setup_call function."""
    mock_setup_call = MagicMock()
    mock_setup_call.return_value = [MagicMock() for _ in range(3)] + [{}]
    return mock_setup_call


@patch(
    "mirascope.core.gemini._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.gemini._utils._setup_call._utils", new_callable=MagicMock)
@patch(
    "mirascope.core.gemini._utils._setup_call.GenerativeModel", new_callable=MagicMock
)
@patch(
    "mirascope.core.gemini._utils._setup_call.GenerativeModel.generate_content",
    new_callable=MagicMock,
)
def test_setup_call(
    mock_generate_content: MagicMock,
    mock_generative_model: MagicMock,
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    """Tests the `setup_call` function."""
    generative_model = GenerativeModel(model_name="gemini-1.5-flash")
    mock_generative_model.return_value = generative_model
    mock_utils.setup_call = mock_base_setup_call
    fn = MagicMock()
    create, prompt_template, messages, tool_types, call_kwargs = setup_call(
        model="gemini-1.5-flash",
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
        fn, {}, None, None, GeminiTool, {}, convert_common_call_params
    )
    mock_convert_message_params.assert_called_once_with(
        mock_base_setup_call.return_value[1]
    )
    assert messages == mock_convert_message_params.return_value
    mock_generative_model.assert_called_once_with(model_name="gemini-1.5-flash")
    assert create(**call_kwargs)
    mock_generate_content.assert_called_once_with(**call_kwargs)
    mock_generate_content.reset_mock()
    assert create(stream=True, **call_kwargs)
    mock_generate_content.assert_called_once_with(**call_kwargs, stream=True)
    mock_generate_content.reset_mock()
    assert create(stream=False, **call_kwargs)
    mock_generate_content.assert_called_once_with(**call_kwargs)


@pytest.mark.parametrize("generation_config_type", [dict, GenerationConfig])
@patch(
    "mirascope.core.gemini._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.gemini._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call_json_mode(
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
    generation_config_type: type,
) -> None:
    """Tests the `setup_call` function with JSON mode."""
    mock_utils.setup_call = mock_base_setup_call
    mock_utils.json_mode_content = MagicMock()
    mock_base_setup_call.return_value[1] = [
        {"role": "user", "parts": [{"type": "text", "text": "test"}]}
    ]
    mock_base_setup_call.return_value[-1]["tools"] = MagicMock()
    mock_base_setup_call.return_value[-1]["generation_config"] = generation_config_type(
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
        model="gemini-1.5-flash",
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
    assert messages[-1]["parts"][-1] == mock_utils.json_mode_content.return_value
    assert "tools" in call_kwargs
    assert "generation_config" in call_kwargs
    assert call_kwargs["generation_config"] == {
        "candidate_count": 1,
        "max_output_tokens": 100,
        "response_mime_type": "application/json",
        "response_schema": None,
        "stop_sequences": ["\n"],
        "temperature": 0.5,
        "top_k": 0,
        "top_p": 0,
    }


@pytest.mark.parametrize("generation_config_type", [dict, GenerationConfig])
@patch(
    "mirascope.core.gemini._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.gemini._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call_system_instruction(
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
    generation_config_type: type,
) -> None:
    """Tests the `setup_call` function with JSON mode."""
    mock_utils.setup_call = mock_base_setup_call
    mock_utils.json_mode_content = MagicMock()
    mock_base_setup_call.return_value[1] = [
        {
            "role": "system",
            "parts": ["system_instruction test"],
        },
        {"role": "user", "parts": [{"type": "text", "text": "test"}]},
    ]
    mock_client = MagicMock()
    mock_client._system_instruction = None
    mock_base_setup_call.return_value[-1]["tools"] = MagicMock()
    mock_base_setup_call.return_value[-1]["generation_config"] = generation_config_type(
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
        model="gemini-1.5-flash",
        client=mock_client,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=True,
        call_params={},
        response_model=None,
        stream=False,
    )
    assert messages[-1]["parts"][-1] == mock_utils.json_mode_content.return_value
    assert mock_client._system_instruction.parts[0].text == "system_instruction test"


@patch(
    "mirascope.core.gemini._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.gemini._utils._setup_call._utils", new_callable=MagicMock)
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
        model="gemini-1.5-flash",
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
    assert "tool_config" in call_kwargs and isinstance(
        call_kwargs["tool_config"], ToolConfigDict
    )
    assert call_kwargs["tool_config"].function_calling_config == {
        "allowed_function_names": ["test"],
        "mode": "any",
    }
