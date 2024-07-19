"""Tests the internal `_stream` module."""

from functools import partial
from typing import cast
from unittest.mock import MagicMock, patch

import pytest

from mirascope.core.base._stream import BaseStream, stream_factory


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


@patch("mirascope.core.base._stream.get_metadata", new_callable=MagicMock)
def test_stream_factory_sync(
    mock_get_metadata: MagicMock,
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

    def fn(genre: str, *, topic: str):
        """Recommend a {genre} book on {topic}."""
        return dynamic_config

    stream: BaseStream = decorator(fn)(genre="fantasy", topic="magic")  # type: ignore
    assert [t for t in stream.stream] == mock_handle_stream.return_value  # type: ignore

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

    mock_setup_call.assert_called_once_with(
        model=mock_stream_decorator_kwargs["model"],
        client=mock_stream_decorator_kwargs["client"],
        fn=fn,
        fn_args=fn_args,
        dynamic_config=dynamic_config,
        tools=mock_stream_decorator_kwargs["tools"],
        json_mode=mock_stream_decorator_kwargs["json_mode"],
        call_params=mock_stream_decorator_kwargs["call_params"],
        extract=False,
    )
    mock_create.assert_called_once_with(stream=True, **mock_call_kwargs)


@patch("mirascope.core.base._stream.get_metadata", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_stream_factory_async(
    mock_get_metadata: MagicMock,
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

    async def fn(genre: str, *, topic: str):
        """Recommend a {genre} book on {topic}."""
        return dynamic_config

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

    mock_setup_call_async.assert_called_once_with(
        model=mock_stream_decorator_kwargs["model"],
        client=mock_stream_decorator_kwargs["client"],
        fn=fn,
        fn_args=fn_args,
        dynamic_config=dynamic_config,
        tools=mock_stream_decorator_kwargs["tools"],
        json_mode=mock_stream_decorator_kwargs["json_mode"],
        call_params=mock_stream_decorator_kwargs["call_params"],
        extract=False,
    )
    mock_create.assert_called_once_with(stream=True, **mock_call_kwargs)
