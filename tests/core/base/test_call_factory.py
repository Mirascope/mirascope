"""Tests the `call_factory` module."""

from unittest.mock import MagicMock, patch

import pytest

from mirascope.core.base._call_factory import call_factory


@pytest.fixture()
def mock_call_factory_kwargs() -> dict:
    """Returns the mock kwargs for the `call_factory` function."""
    return {
        "TCallResponse": MagicMock,
        "TCallResponseChunk": MagicMock,
        "TToolType": MagicMock,
        "TStream": MagicMock,
        "default_call_params": MagicMock(),
        "setup_call": MagicMock(),
        "get_json_output": MagicMock(),
        "handle_stream": MagicMock(),
        "handle_stream_async": MagicMock(),
    }


@patch("mirascope.core.base._call_factory.create_factory", new_callable=MagicMock)
@patch("mirascope.core.base._call_factory.partial", new_callable=MagicMock)
def test_call_factory_create(
    mock_partial: MagicMock,
    mock_create_factory: MagicMock,
    mock_call_factory_kwargs: dict,
) -> None:
    """Tests the `create_factory` route for the `call_factory` method."""
    call = call_factory(**mock_call_factory_kwargs)
    create_kwargs = {
        "model": "model",
        "tools": [],
        "response_model": None,
        "output_parser": MagicMock(),
        "json_mode": True,
        "client": MagicMock(),
    }
    _ = call(**create_kwargs)
    mock_create_factory.assert_called_once_with(
        TCallResponse=mock_call_factory_kwargs["TCallResponse"],
        setup_call=mock_call_factory_kwargs["setup_call"],
    )
    mock_partial.assert_called_once_with(
        mock_create_factory.return_value,
        **create_kwargs,
        call_params=mock_call_factory_kwargs["default_call_params"],
    )


@patch("mirascope.core.base._call_factory.stream_factory", new_callable=MagicMock)
@patch("mirascope.core.base._call_factory.partial", new_callable=MagicMock)
def test_call_factory_stream(
    mock_partial: MagicMock,
    mock_stream_factory: MagicMock,
    mock_call_factory_kwargs: dict,
) -> None:
    """Tests the `stream_factory` route for the `call_factory` method."""
    call = call_factory(**mock_call_factory_kwargs)
    stream_kwargs = {
        "model": "model",
        "tools": [],
        "json_mode": False,
        "client": MagicMock(),
        "call_params": MagicMock(),
    }
    _ = call(stream=True, **stream_kwargs)
    mock_stream_factory.assert_called_once_with(
        TCallResponse=mock_call_factory_kwargs["TCallResponse"],
        TStream=mock_call_factory_kwargs["TStream"],
        setup_call=mock_call_factory_kwargs["setup_call"],
        handle_stream=mock_call_factory_kwargs["handle_stream"],
        handle_stream_async=mock_call_factory_kwargs["handle_stream_async"],
    )
    mock_partial.assert_called_once_with(
        mock_stream_factory.return_value, **stream_kwargs, partial_tools=False
    )


@patch("mirascope.core.base._call_factory.extract_factory", new_callable=MagicMock)
@patch("mirascope.core.base._call_factory.partial", new_callable=MagicMock)
def test_call_factory_extract(
    mock_partial: MagicMock,
    mock_extract_factory: MagicMock,
    mock_call_factory_kwargs: dict,
) -> None:
    """Tests the `extract_factory` route for the `call_factory` method."""
    call = call_factory(**mock_call_factory_kwargs)
    extract_kwargs = {
        "model": "model",
        "response_model": MagicMock,
        "output_parser": None,
        "json_mode": False,
        "client": MagicMock(),
        "call_params": MagicMock(),
    }
    _ = call(**extract_kwargs)
    mock_extract_factory.assert_called_once_with(
        TCallResponse=mock_call_factory_kwargs["TCallResponse"],
        TToolType=mock_call_factory_kwargs["TToolType"],
        setup_call=mock_call_factory_kwargs["setup_call"],
        get_json_output=mock_call_factory_kwargs["get_json_output"],
    )
    mock_partial.assert_called_once_with(
        mock_extract_factory.return_value, **extract_kwargs
    )


@patch(
    "mirascope.core.base._call_factory.extract_with_tools_factory",
    new_callable=MagicMock,
)
@patch("mirascope.core.base._call_factory.partial", new_callable=MagicMock)
def test_call_factory_extract_with_tools(
    mock_partial: MagicMock,
    mock_extract_with_tools_factory: MagicMock,
    mock_call_factory_kwargs: dict,
) -> None:
    """Tests the `extract_factory` route for the `call_factory` method."""
    call = call_factory(**mock_call_factory_kwargs)
    extract_with_tools_kwargs = {
        "model": "model",
        "tools": [MagicMock()],
        "response_model": MagicMock,
        "output_parser": None,
        "client": MagicMock(),
        "call_params": MagicMock(),
    }
    _ = call(**extract_with_tools_kwargs)
    mock_extract_with_tools_factory.assert_called_once_with(
        TCallResponse=mock_call_factory_kwargs["TCallResponse"],
        setup_call=mock_call_factory_kwargs["setup_call"],
        get_json_output=mock_call_factory_kwargs["get_json_output"],
    )
    mock_partial.assert_called_once_with(
        mock_extract_with_tools_factory.return_value,
        **extract_with_tools_kwargs,
    )


@patch(
    "mirascope.core.base._call_factory.structured_stream_factory",
    new_callable=MagicMock,
)
@patch("mirascope.core.base._call_factory.partial", new_callable=MagicMock)
def test_call_factory_structured_stream(
    mock_partial: MagicMock,
    mock_structured_stream_factory: MagicMock,
    mock_call_factory_kwargs: dict,
) -> None:
    """Tests the `structured_stream_factory` route for the `call_factory` method."""
    call = call_factory(**mock_call_factory_kwargs)
    structured_stream_kwargs = {
        "model": "model",
        "response_model": MagicMock,
        "json_mode": False,
        "client": MagicMock(),
        "call_params": MagicMock(),
    }
    _ = call(stream=True, **structured_stream_kwargs)
    mock_structured_stream_factory.assert_called_once_with(
        TCallResponse=mock_call_factory_kwargs["TCallResponse"],
        TCallResponseChunk=mock_call_factory_kwargs["TCallResponseChunk"],
        TStream=mock_call_factory_kwargs["TStream"],
        TToolType=mock_call_factory_kwargs["TToolType"],
        setup_call=mock_call_factory_kwargs["setup_call"],
        get_json_output=mock_call_factory_kwargs["get_json_output"],
    )
    mock_partial.assert_called_once_with(
        mock_structured_stream_factory.return_value, **structured_stream_kwargs
    )


def test_call_decorator_invalid_output_parser_with_stream(
    mock_call_factory_kwargs: dict,
) -> None:
    """Tests a ValueError is raised if `output_parser` is provided and `stream=True`."""
    call = call_factory(**mock_call_factory_kwargs)
    with pytest.raises(
        ValueError, match="Cannot use `output_parser` with `stream=True`"
    ):
        call("model", stream=True, output_parser=MagicMock())
