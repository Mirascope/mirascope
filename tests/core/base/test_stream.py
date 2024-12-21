"""Tests the `stream` module."""

from functools import partial
from typing import cast
from unittest.mock import MagicMock, patch

import pytest

from mirascope.core.base.stream import BaseStream, stream_factory


@pytest.fixture()
def mock_stream_decorator_kwargs() -> dict:
    """Returns the mock kwargs (excluding fn) for the stream `decorator` function."""
    return {
        "model": "model",
        "tools": [],
        "json_mode": True,
        "client": MagicMock(),
        "call_params": MagicMock(),
    }


@patch("mirascope.core.base.stream.prompt_template", new_callable=MagicMock)
@patch("mirascope.core.base.stream.get_metadata", new_callable=MagicMock)
def test_stream_factory_sync(
    mock_get_metadata: MagicMock,
    mock_prompt_template_decorator: MagicMock,
    mock_setup_call: MagicMock,
    mock_stream_decorator_kwargs: dict,
) -> None:
    """Tests the `stream_factory` method on a sync function."""
    (
        mock_create,
        mock_prompt_template,
        mock_messages,
        mock_tool_types,
        mock_call_kwargs,
    ) = mock_setup_call.return_value
    mock_create = cast(MagicMock, mock_create)

    mock_handle_stream = MagicMock()
    mock_handle_stream.return_value = [("chunk", "tool")]
    mock_call_response_type = MagicMock
    decorator = partial(
        stream_factory(
            TCallResponse=mock_call_response_type,
            TStream=MagicMock,
            setup_call=mock_setup_call,
            handle_stream=mock_handle_stream,
            handle_stream_async=MagicMock(),
        ),
        **mock_stream_decorator_kwargs,
    )

    dynamic_config = MagicMock()
    mock_get = MagicMock()
    mock_get.return_value = None
    dynamic_config.get = mock_get

    def fn(genre: str, *, topic: str):
        """Recommend a {genre} book on {topic}."""
        return dynamic_config

    mock_prompt_template_decorator.return_value = lambda x: fn

    decorated_fn = decorator(fn)
    assert decorated_fn._model == mock_stream_decorator_kwargs["model"]  # pyright: ignore [reportFunctionMemberAccess]
    stream: BaseStream = decorated_fn(genre="fantasy", topic="magic")  # type: ignore
    assert list(stream.stream) == mock_handle_stream.return_value  # type: ignore

    assert stream.metadata == mock_get_metadata.return_value
    assert stream.tool_types == mock_tool_types
    assert stream.call_response_type == mock_call_response_type
    assert stream.model == mock_stream_decorator_kwargs["model"]
    assert stream.prompt_template == mock_prompt_template
    fn_args = {"genre": "fantasy", "topic": "magic"}
    assert stream.fn_args == fn_args
    assert stream.dynamic_config == dynamic_config
    assert stream.messages == mock_messages
    assert stream.call_params == mock_stream_decorator_kwargs["call_params"]
    assert stream.call_kwargs == mock_call_kwargs

    mock_setup_call.assert_called_once_with(
        model=mock_stream_decorator_kwargs["model"],
        client=mock_stream_decorator_kwargs["client"],
        fn=fn,
        fn_args=fn_args,
        dynamic_config=dynamic_config,
        tools=mock_stream_decorator_kwargs["tools"],
        json_mode=mock_stream_decorator_kwargs["json_mode"],
        call_params=mock_stream_decorator_kwargs["call_params"],
        response_model=None,
        stream=True,
    )
    mock_create.assert_called_once_with(stream=True, **mock_call_kwargs)


@patch("mirascope.core.base.stream.prompt_template", new_callable=MagicMock)
@patch("mirascope.core.base.stream.get_metadata", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_stream_factory_async(
    mock_get_metadata: MagicMock,
    mock_prompt_template_decorator: MagicMock,
    mock_setup_call_async: MagicMock,
    mock_stream_decorator_kwargs: dict,
) -> None:
    """Tests the `stream_factory` method on an async function."""
    (
        mock_create,
        mock_prompt_template,
        mock_messages,
        mock_tool_types,
        mock_call_kwargs,
    ) = mock_setup_call_async.return_value
    mock_create = cast(MagicMock, mock_create)

    mock_handle_stream_async = MagicMock()
    mock_handle_stream_async.return_value.__aiter__.return_value = [("chunk", "tool")]
    mock_call_response_type = MagicMock
    decorator = partial(
        stream_factory(
            TCallResponse=mock_call_response_type,
            TStream=MagicMock,
            setup_call=mock_setup_call_async,
            handle_stream=MagicMock(),
            handle_stream_async=mock_handle_stream_async,
        ),
        **mock_stream_decorator_kwargs,
    )

    dynamic_config = MagicMock()
    mock_get = MagicMock()
    mock_get.return_value = None
    dynamic_config.get = mock_get

    async def fn(genre: str, *, topic: str):
        """Recommend a {genre} book on {topic}."""
        return dynamic_config

    mock_prompt_template_decorator.return_value = lambda x: fn

    stream: BaseStream = await decorator(fn)(genre="fantasy", topic="magic")  # type: ignore
    stream_response = []
    async for t in stream.stream:  # type: ignore
        stream_response.append(t)
    assert (
        stream_response == mock_handle_stream_async.return_value.__aiter__.return_value
    )  # type: ignore

    assert stream.metadata == mock_get_metadata.return_value
    assert stream.tool_types == mock_tool_types
    assert stream.call_response_type == mock_call_response_type
    assert stream.model == mock_stream_decorator_kwargs["model"]
    assert stream.prompt_template == mock_prompt_template
    fn_args = {"genre": "fantasy", "topic": "magic"}
    assert stream.fn_args == fn_args
    assert stream.dynamic_config == dynamic_config
    assert stream.messages == mock_messages
    assert stream.call_params == mock_stream_decorator_kwargs["call_params"]
    assert stream.call_kwargs == mock_call_kwargs

    mock_setup_call_async.assert_called_once_with(
        model=mock_stream_decorator_kwargs["model"],
        client=mock_stream_decorator_kwargs["client"],
        fn=fn,
        fn_args=fn_args,
        dynamic_config=dynamic_config,
        tools=mock_stream_decorator_kwargs["tools"],
        json_mode=mock_stream_decorator_kwargs["json_mode"],
        call_params=mock_stream_decorator_kwargs["call_params"],
        response_model=None,
        stream=True,
    )
    mock_create.assert_called_once_with(stream=True, **mock_call_kwargs)


@patch(
    "mirascope.core.base.stream.get_possible_user_message_param",
    new_callable=MagicMock,
)
@patch.multiple(BaseStream, __abstractmethods__=set())
@pytest.mark.asyncio
async def test_base_stream(mock_get_possible_user_message_param: MagicMock) -> None:
    """Tests the `BaseStream` class."""
    mock_construct_message_param = MagicMock()
    mock_construct_message_param.return_value = "mock_message_param"
    BaseStream._construct_message_param = mock_construct_message_param
    call_response_type = MagicMock
    mock_tool_message_params = MagicMock()
    call_response_type.tool_message_params = mock_tool_message_params

    mock_chunk = MagicMock()
    mock_chunk.content = "content"
    mock_chunk.input_tokens = 1
    mock_chunk.output_tokens = 2
    mock_chunk.model = "updated_model"

    mock_tool = MagicMock()
    mock_tool.tool_call = "tool_call"
    mock_tool.call = lambda: "tool_call_response"

    stream = BaseStream(
        stream=(t for t in [(mock_chunk, mock_tool)]),
        metadata={},
        tool_types=[],
        call_response_type=call_response_type,
        model="model",
        prompt_template="prompt_template",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
    )  # type: ignore
    assert (
        stream.user_message_param == mock_get_possible_user_message_param.return_value
    )
    assert list(stream) == [(mock_chunk, mock_tool)]
    mock_construct_message_param.assert_called_once_with(["tool_call"], "content")
    assert stream.message_param == "mock_message_param"
    assert stream.model == "updated_model"

    async def generator():
        yield mock_chunk, mock_tool

    stream.stream, stream.message_param = generator(), None
    stream_response, tools_and_outputs = [], []
    async for chunk, tool in stream:
        stream_response.append((chunk, tool))
        tools_and_outputs.append((tool, tool.call()))  # type: ignore
    assert stream_response == [(mock_chunk, mock_tool)]
    mock_construct_message_param.assert_called_with(["tool_call"], "content")
    assert stream.message_param == "mock_message_param"
    assert stream.model == "updated_model"

    assert stream.tool_message_params(tools_and_outputs)
    mock_tool_message_params.assert_called_once_with(tools_and_outputs)
