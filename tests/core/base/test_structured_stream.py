"""Tests for the internal `_structured_stream` module."""

from functools import partial
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mirascope.core.base._structured_stream import (
    BaseStructuredStream,
    structured_stream_factory,
)


@pytest.fixture()
def mock_structured_stream_decorator_kwargs() -> dict:
    """Returns mock kwargs (excluding fn) for structured stream `decorator` function."""
    return {
        "model": "model",
        "response_model": MagicMock,
        "json_mode": True,
        "client": MagicMock(),
        "call_params": MagicMock(),
    }


@patch(
    "mirascope.core.base._structured_stream.setup_extract_tool", new_callable=MagicMock
)
@patch("mirascope.core.base._structured_stream.stream_factory", new_callable=MagicMock)
def test_structured_stream_factory_sync(
    mock_stream_factory: MagicMock,
    mock_setup_extract_tool: MagicMock,
    mock_setup_call: MagicMock,
    mock_structured_stream_decorator_kwargs: dict,
) -> None:
    """Tests the `structured_stream_factory` method on a sync function."""
    mock_stream_decorator = MagicMock()
    mock_stream_inner = MagicMock()
    mock_stream_inner.return_value = [("chunk", None)]
    mock_stream_decorator.return_value = mock_stream_inner
    mock_stream_factory.return_value = mock_stream_decorator
    mock_get_json_output = MagicMock()
    mock_get_json_output.return_value = "json_output"
    decorator = partial(
        structured_stream_factory(
            TCallResponse=MagicMock,
            TCallResponseChunk=MagicMock,
            TStream=MagicMock,
            TToolType=MagicMock,
            setup_call=mock_setup_call,
            get_json_output=mock_get_json_output,
        ),
        **mock_structured_stream_decorator_kwargs,
    )

    dynamic_config = MagicMock()

    def fn(genre: str, *, topic: str):
        """Recommend a {genre} book on {topic}."""
        return dynamic_config

    structured_stream: BaseStructuredStream = decorator(fn)(
        genre="fantasy",  # type: ignore
        topic="magic",
    )
    assert structured_stream.stream == mock_stream_inner.return_value
    assert (
        structured_stream.response_model
        == mock_structured_stream_decorator_kwargs["response_model"]
    )
    mock_stream_factory.assert_called_once()
    mock_stream_decorator.assert_called_once_with(
        fn=fn,
        model=mock_structured_stream_decorator_kwargs["model"],
        tools=[mock_setup_extract_tool.return_value],
        json_mode=mock_structured_stream_decorator_kwargs["json_mode"],
        client=mock_structured_stream_decorator_kwargs["client"],
        call_params=mock_structured_stream_decorator_kwargs["call_params"],
    )
    mock_stream_inner.assert_called_once_with(genre="fantasy", topic="magic")
    assert [t for t in structured_stream.stream] == [("chunk", None)]

    # Test internal `handle_stream`
    kwargs = mock_stream_factory.call_args.kwargs
    assert (
        "handle_stream" in kwargs
        and (handle_stream := kwargs["handle_stream"]) is not None
    )
    for chunk, tool in handle_stream(["chunk0", "chunk1"], None):
        assert hasattr(chunk, "content") and getattr(chunk, "content") == "json_output"
        assert tool is None


@patch(
    "mirascope.core.base._structured_stream.setup_extract_tool", new_callable=MagicMock
)
@patch("mirascope.core.base._structured_stream.stream_factory", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_structured_stream_factory_async(
    mock_stream_factory: MagicMock,
    mock_setup_extract_tool: MagicMock,
    mock_setup_call_async: MagicMock,
    mock_structured_stream_decorator_kwargs: dict,
) -> None:
    """Tests the `structured_stream_factory` method on an async function."""
    mock_stream_decorator = MagicMock()
    mock_stream_inner = AsyncMock()
    mock_stream_inner.return_value.__aiter__.return_value = [("chunk", None)]
    mock_stream_decorator.return_value = mock_stream_inner
    mock_stream_factory.return_value = mock_stream_decorator
    mock_get_json_output = MagicMock()
    mock_get_json_output.return_value = "json_output"
    decorator = partial(
        structured_stream_factory(
            TCallResponse=MagicMock,
            TCallResponseChunk=MagicMock,
            TStream=MagicMock,
            TToolType=MagicMock,
            setup_call=mock_setup_call_async,
            get_json_output=mock_get_json_output,
        ),
        **mock_structured_stream_decorator_kwargs,
    )

    dynamic_config = MagicMock()

    async def fn(genre: str, *, topic: str):
        """Recommend a {genre} book on {topic}."""
        return dynamic_config

    structured_stream: BaseStructuredStream = await decorator(fn)(
        genre="fantasy",  # type: ignore
        topic="magic",
    )
    assert structured_stream.stream == mock_stream_inner.return_value
    assert (
        structured_stream.response_model
        == mock_structured_stream_decorator_kwargs["response_model"]
    )
    mock_stream_factory.assert_called_once()
    mock_stream_decorator.assert_called_once_with(
        fn=fn,
        model=mock_structured_stream_decorator_kwargs["model"],
        tools=[mock_setup_extract_tool.return_value],
        json_mode=mock_structured_stream_decorator_kwargs["json_mode"],
        client=mock_structured_stream_decorator_kwargs["client"],
        call_params=mock_structured_stream_decorator_kwargs["call_params"],
    )
    mock_stream_inner.assert_called_once_with(genre="fantasy", topic="magic")
    stream_response = []
    async for t in structured_stream.stream:
        stream_response.append(t)
    assert stream_response == mock_stream_inner.return_value.__aiter__.return_value

    # Test internal `handle_stream_async`
    kwargs = mock_stream_factory.call_args.kwargs
    assert (
        "handle_stream_async" in kwargs
        and (handle_stream := kwargs["handle_stream_async"]) is not None
    )

    async def generator():
        yield "chunk0"
        yield "chunk1"

    async for chunk, tool in handle_stream(generator(), None):
        assert hasattr(chunk, "content") and getattr(chunk, "content") == "json_output"
        assert tool is None
