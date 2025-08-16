"""Tests the `google._utils.setup_call` module."""

from collections.abc import Callable
from typing import cast
from unittest.mock import MagicMock, patch

import pytest
from google.genai.types import (
    FunctionCallingConfig,
    FunctionCallingConfigMode,
    GenerateContentConfig,
    Part,
    Tool,
)
from pydantic import BaseModel

from mirascope.core.google._utils._convert_common_call_params import (
    convert_common_call_params,
)
from mirascope.core.google._utils._setup_call import setup_call
from mirascope.core.google.call_params import GoogleCallParams
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
def test_setup_call(
    mock_client_class: MagicMock,
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    """Tests the `setup_call` function."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
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
        mock_base_setup_call.return_value[1], mock_client
    )
    assert messages == mock_convert_message_params.return_value
    mock_client_class.assert_called_once_with()
    assert create(**call_kwargs)
    mock_client.models.generate_content.assert_called_once_with(**call_kwargs)
    mock_client.models.generate_content.reset_mock()
    assert create(stream=True, **call_kwargs)
    mock_client.models.generate_content_stream.assert_called_once_with(**call_kwargs)
    mock_client.models.generate_content_stream.reset_mock()
    assert create(stream=False, **call_kwargs)
    mock_client.models.generate_content.assert_called_once_with(**call_kwargs)


@pytest.mark.parametrize(
    "generation_config_type",
    [dict, GenerateContentConfig],
)
@patch(
    "mirascope.core.google._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.google._utils._setup_call._utils", new_callable=MagicMock)
@patch("mirascope.core.google._utils._setup_call.Client", new_callable=MagicMock)
def test_setup_call_json_mode(
    mock_client_class: MagicMock,
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
    generation_config_type: type,
) -> None:
    """Tests the `setup_call` function with JSON mode."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_utils.setup_call = mock_base_setup_call
    mock_utils.json_mode_content = MagicMock()
    mock_base_setup_call.return_value[1] = [
        {
            "role": "system",
            "parts": [{"text": "this is system message"}],
        },
        {"role": "user", "parts": [{"type": "text", "text": "test"}]},
    ]
    tools: list[Tool | Callable] = [MagicMock(spec=Tool)]
    mock_base_setup_call.return_value[-1]["tools"] = tools
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
    mock_convert_message_params.side_effect = lambda x, y: x
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
    mock_client_class.assert_called_once_with()
    assert isinstance(messages[-1], dict)
    assert "parts" in messages[-1]
    assert isinstance(messages[-1]["parts"], list)
    assert messages[-1]["parts"][-1] == {
        "text": mock_utils.json_mode_content.return_value
    }
    assert "config" in call_kwargs
    assert call_kwargs["config"] == GenerateContentConfig(
        system_instruction=[
            Part(
                video_metadata=None,
                thought=None,
                code_execution_result=None,
                executable_code=None,
                file_data=None,
                function_call=None,
                function_response=None,
                inline_data=None,
                text="this is system message",
            )
        ],
        temperature=0.5,
        top_p=0.0,
        top_k=0.0,
        candidate_count=1,
        max_output_tokens=100,
        stop_sequences=["\n"],
        response_logprobs=None,
        logprobs=None,
        presence_penalty=None,
        frequency_penalty=None,
        seed=None,
        response_mime_type="application/json",
        response_schema=None,
        routing_config=None,
        safety_settings=None,
        tools=tools,
        tool_config=None,
        cached_content=None,
        response_modalities=None,
        media_resolution=None,
        speech_config=None,
        audio_timestamp=None,
        automatic_function_calling=None,
        thinking_config=None,
    )


@patch(
    "mirascope.core.google._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.google._utils._setup_call._utils", new_callable=MagicMock)
@patch("mirascope.core.google._utils._setup_call.Client", new_callable=MagicMock)
def test_setup_call_extract(
    mock_client_class: MagicMock,
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
    mock_client_class.assert_called_once_with()
    assert "config" in call_kwargs and isinstance(
        call_kwargs["config"], GenerateContentConfig
    )
    config = call_kwargs["config"]
    assert config.tool_config is not None
    assert config.tool_config.function_calling_config is not None
    assert config.tool_config.function_calling_config == FunctionCallingConfig(
        mode=FunctionCallingConfigMode.ANY, allowed_function_names=["test"]
    )


@patch(
    "mirascope.core.google._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.google._utils._setup_call._utils", new_callable=MagicMock)
@patch("mirascope.core.google._utils._setup_call.Client", new_callable=MagicMock)
def test_setup_call_vertexai_dynamic_config_dict(
    mock_client_class, mock_utils, mock_convert_message_params
):
    dynamic_config = {"metadata": {"tags": set()}}
    fn = MagicMock()
    base_setup = MagicMock(
        return_value=(
            "template",
            [{"role": "user", "parts": [{"text": "msg"}]}],
            None,
            {},
        )
    )
    mock_utils.setup_call = base_setup
    mock_convert_message_params.return_value = [
        {"role": "user", "parts": [{"text": "msg"}]}
    ]
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_client.vertexai = True
    _, _, _, _, _ = setup_call(  # pyright: ignore [reportCallIssue]
        model="google-1.5-flash",
        client=None,
        fn=fn,
        fn_args={},
        dynamic_config=dynamic_config,  # pyright: ignore [reportArgumentType]
        tools=None,
        json_mode=False,
        call_params={},
        response_model=None,
        stream=False,
    )
    assert "metadata" in dynamic_config
    assert "tags" in dynamic_config["metadata"]
    assert "use_vertex_ai" in dynamic_config["metadata"]["tags"]


@patch(
    "mirascope.core.google._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.google._utils._setup_call._utils", new_callable=MagicMock)
@patch("mirascope.core.google._utils._setup_call.Client", new_callable=MagicMock)
def test_setup_call_vertexai_dynamic_config_non_dict(
    mock_client_class, mock_utils, mock_convert_message_params
):
    dynamic_config = None
    fn = MagicMock()
    if hasattr(fn, "_metadata"):
        del fn._metadata
    base_setup = MagicMock(
        return_value=(
            "template",
            [{"role": "user", "parts": [{"text": "msg"}]}],
            None,
            {},
        )
    )
    mock_utils.setup_call = base_setup
    mock_convert_message_params.return_value = [
        {"role": "user", "parts": [{"text": "msg"}]}
    ]
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_client.vertexai = True
    _, _, _, _, _ = setup_call(
        model="google-1.5-flash",
        client=None,
        fn=fn,
        fn_args={},
        dynamic_config=dynamic_config,
        tools=None,
        json_mode=False,
        call_params={},
        response_model=None,
        stream=False,
    )
    assert hasattr(fn, "_metadata")
    metadata = fn._metadata
    assert "tags" in metadata
    assert "use_vertex_ai" in metadata["tags"]


@patch(
    "mirascope.core.google._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.google._utils._setup_call._utils", new_callable=MagicMock)
@patch("mirascope.core.google._utils._setup_call.Client", new_callable=MagicMock)
def test_setup_call_with_call_params(
    mock_client_class: MagicMock,
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    """Tests the `setup_call` function with direct parameters in call_params."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_utils.setup_call = mock_base_setup_call
    fn = MagicMock()

    call_params = cast(GoogleCallParams, {"temperature": 0.8, "top_p": 0.7})

    create, prompt_template, messages, tool_types, call_kwargs = setup_call(
        model="google-1.5-flash",
        client=None,
        fn=fn,
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params=call_params,
        response_model=None,
        stream=False,
    )

    # These parameters should be passed to the base setup_call
    mock_base_setup_call.assert_called_with(
        fn,
        {},
        None,
        None,
        GoogleTool,
        call_params,  # Call params should be passed directly
        convert_common_call_params,
    )

    # Now test with a GenerateContentConfig parameter
    mock_base_setup_call.reset_mock()
    call_params = cast(GoogleCallParams, {"temperature": 0.9, "top_k": 10})

    create, prompt_template, messages, tool_types, call_kwargs = setup_call(
        model="google-1.5-flash",
        client=None,
        fn=fn,
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params=call_params,
        response_model=None,
        stream=False,
    )

    # These parameters should be passed to the base setup_call
    mock_base_setup_call.assert_called_with(
        fn,
        {},
        None,
        None,
        GoogleTool,
        call_params,  # Call params should be passed directly
        convert_common_call_params,
    )


class MyTestModel(BaseModel):
    param: str
    optional_param: int | None = None


# Helper to structure mock returns for _utils.setup_call
def _get_mock_base_setup_call_value(messages=None, call_kwargs_override=None):
    base_messages = (
        messages
        if messages is not None
        else [{"role": "user", "parts": [{"text": "test content"}]}]
    )
    base_call_kwargs = call_kwargs_override if call_kwargs_override is not None else {}
    return [
        MagicMock(),
        base_messages,
        MagicMock(),
        base_call_kwargs,
    ]  # prompt_template, messages, tool_types, call_kwargs


@patch(
    "mirascope.core.google._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.google._utils._setup_call._utils", new_callable=MagicMock)
@patch("mirascope.core.google._utils._setup_call.Client", new_callable=MagicMock)
def test_setup_call_json_mode_with_response_model(
    mock_client_class: MagicMock,
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
) -> None:
    """Tests `setup_call` with `json_mode=True` and a `response_model`.
    It should set `response_schema` in the config and not add generic JSON content.
    """
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_utils.setup_call.return_value = _get_mock_base_setup_call_value()
    mock_convert_message_params.side_effect = lambda x, y: x  # Passthrough

    _, _, messages_out, _, call_kwargs = setup_call(
        model="google-1.5-flash",
        client=None,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=True,
        call_params={},
        response_model=MyTestModel,
        stream=False,
    )

    assert "config" in call_kwargs
    config = call_kwargs["config"]
    assert isinstance(config, GenerateContentConfig)
    assert config.response_mime_type == "application/json"
    assert config.response_schema == MyTestModel

    # Ensure json_mode_content was NOT added to messages
    # Assuming last message is user message and we check its parts
    last_message_parts = messages_out[-1]["parts"]
    for part in last_message_parts:
        if isinstance(part, dict) and "text" in part:
            assert mock_utils.json_mode_content.call_count == 0


@patch(
    "mirascope.core.google._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.google._utils._setup_call._utils", new_callable=MagicMock)
@patch("mirascope.core.google._utils._setup_call.Client", new_callable=MagicMock)
def test_setup_call_json_mode_no_response_model_no_tools(
    mock_client_class: MagicMock,
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
) -> None:
    """Tests `setup_call` with `json_mode=True`, no `response_model`, and no `tools`."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    # Simulate initial messages from base setup call
    initial_messages = [{"role": "user", "parts": [{"text": "initial prompt"}]}]
    mock_utils.setup_call.return_value = _get_mock_base_setup_call_value(
        messages=initial_messages
    )
    mock_convert_message_params.side_effect = lambda x, y: x  # Passthrough
    mock_utils.json_mode_content.return_value = "JSON_MODE_PROMPT_TEXT"

    _, _, messages_out, _, call_kwargs = setup_call(
        model="google-1.5-flash",
        client=None,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,  # Explicitly no tools
        json_mode=True,
        call_params={},
        response_model=None,  # Explicitly no response model
        stream=False,
    )

    assert "config" in call_kwargs
    config = call_kwargs["config"]
    assert isinstance(config, GenerateContentConfig)
    assert config.response_mime_type == "application/json"
    assert getattr(config, "response_schema", None) is None  # Schema should not be set

    # Ensure json_mode_content WAS added to the last message
    assert len(messages_out) > 0
    last_message_parts = messages_out[-1]["parts"]
    assert any(
        part.get("text") == "JSON_MODE_PROMPT_TEXT"
        for part in last_message_parts
        if isinstance(part, dict)
    )
    mock_utils.json_mode_content.assert_called_once_with(None)


@patch(
    "mirascope.core.google._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.google._utils._setup_call._utils", new_callable=MagicMock)
@patch("mirascope.core.google._utils._setup_call.Client", new_callable=MagicMock)
def test_setup_call_json_mode_with_response_model_sets_schema(
    mock_client_class: MagicMock,
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    """Tests `setup_call` with `json_mode=True` and a `response_model`.

    It should set `response_schema` in the config and not add generic JSON content by calling
    `_utils.json_mode_content`.
    """
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_utils.setup_call = mock_base_setup_call

    initial_messages = [{"role": "user", "parts": [{"text": "initial prompt"}]}]
    mock_base_setup_call.return_value[1] = initial_messages 
    mock_base_setup_call.return_value[3] = {} 

    mock_convert_message_params.side_effect = lambda x, y: x

    class TestResponseModel(BaseModel):
        foo: str
        bar: int | None = None

    _, _, messages_out, _, call_kwargs_out = setup_call(
        model="google-1.5-flash",
        client=None,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=True,
        call_params={},
        response_model=TestResponseModel, # Use the concrete model class
        stream=False,
    )

    assert "config" in call_kwargs_out
    config = call_kwargs_out["config"]
    assert isinstance(config, GenerateContentConfig)
    assert config.response_mime_type == "application/json"
    assert config.response_schema == TestResponseModel 

    mock_utils.json_mode_content.assert_not_called()

    assert len(messages_out) == len(initial_messages)
    if initial_messages and messages_out:
        assert messages_out[-1]["parts"] == initial_messages[-1]["parts"]


@patch(
    "mirascope.core.google._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.google._utils._setup_call._utils", new_callable=MagicMock)
@patch("mirascope.core.google._utils._setup_call.Client", new_callable=MagicMock)
def test_setup_call_strict_response_model_forces_schema(
    mock_client_class: MagicMock,
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
) -> None:
    """Test that setup_call uses response_schema when strict=True is set in response_model's config,
    even when json_mode is False.
    """
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_utils.setup_call.return_value = _get_mock_base_setup_call_value()
    mock_convert_message_params.side_effect = lambda x, y: x

    class StrictResponseModel(BaseModel):
        name: str
        age: int

        model_config = {"strict": True}

    # Test with json_mode=False but strict=True
    _, _, messages_out, _, call_kwargs = setup_call(
        model="google-1.5-flash",
        client=None,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,  # json_mode is False
        call_params={},
        response_model=StrictResponseModel,
        stream=False,
    )

    # Should still use response_schema because strict=True
    assert "config" in call_kwargs
    config = call_kwargs["config"]
    assert isinstance(config, GenerateContentConfig)
    assert config.response_mime_type == "application/json"
    assert config.response_schema == StrictResponseModel

    # Should not use tools path
    assert config.tool_config is None

    # Should not append json_mode_content
    mock_utils.json_mode_content.assert_not_called()

    # Test with both json_mode=True and strict=True
    mock_utils.json_mode_content.reset_mock()
    _, _, messages_out, _, call_kwargs = setup_call(
        model="google-1.5-flash",
        client=None,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=True,  # json_mode is True
        call_params={},
        response_model=StrictResponseModel,
        stream=False,
    )

    # Should still use response_schema
    assert "config" in call_kwargs
    config = call_kwargs["config"]
    assert isinstance(config, GenerateContentConfig)
    assert config.response_mime_type == "application/json"
    assert config.response_schema == StrictResponseModel

    # Should not use tools path
    assert config.tool_config is None

    # Should not append json_mode_content
    mock_utils.json_mode_content.assert_not_called()
