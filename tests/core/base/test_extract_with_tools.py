"""Tests the internal `_extract_with_tools` module."""

from functools import partial
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, ValidationError

from mirascope.core.base._extract_with_tools import extract_with_tools_factory


@pytest.fixture()
def mock_extract_with_tools_decorator_kwargs() -> dict:
    """Returns the mock kwargs (excluding fn) for the extract with tools `decorator`."""
    return {
        "model": "model",
        "tools": [MagicMock()],
        "response_model": BaseModel,
        "output_parser": None,
        "client": MagicMock(),
        "call_params": MagicMock(),
    }


class MyBaseModel(BaseModel):
    """Empty base model for testing."""


@patch(
    "mirascope.core.base._extract_with_tools.extract_tool_return",
    new_callable=MagicMock,
)
@patch("mirascope.core.base._extract_with_tools.create_factory", new_callable=MagicMock)
def test_extract_with_tools_factory_sync(
    mock_create_factory: MagicMock,
    mock_extract_tool_return: MagicMock,
    mock_setup_call: MagicMock,
    mock_extract_with_tools_decorator_kwargs: dict,
) -> None:
    """Tests the `extract_factory` method on a sync function."""
    mock_create_decorator = MagicMock()
    mock_create_inner = MagicMock()
    mock_call_response = MagicMock()
    mock_call_response.tools = None
    mock_create_inner.return_value = mock_call_response
    mock_create_decorator.return_value = mock_create_inner
    mock_create_factory.return_value = mock_create_decorator
    mock_extract_tool_return.return_value = MyBaseModel()
    mock_get_json_output = MagicMock()

    decorator = partial(
        extract_with_tools_factory(
            TCallResponse=MagicMock,
            setup_call=mock_setup_call,
            get_json_output=mock_get_json_output,
        ),
        **mock_extract_with_tools_decorator_kwargs,
    )

    def fn(genre: str, *, topic: str) -> None:
        """Recommend a {genre} book on {topic}."""

    decorated_fn = decorator(fn)
    assert decorated_fn._model == mock_extract_with_tools_decorator_kwargs["model"]  # pyright: ignore [reportFunctionMemberAccess]
    output = decorated_fn(genre="fantasy", topic="magic")  # type: ignore
    mock_create_factory.assert_called_once_with(
        TCallResponse=MagicMock, setup_call=mock_setup_call
    )
    mock_create_decorator.assert_called_once_with(
        fn=fn,
        model=mock_extract_with_tools_decorator_kwargs["model"],
        tools=mock_extract_with_tools_decorator_kwargs["tools"],
        response_model=mock_extract_with_tools_decorator_kwargs["response_model"],
        output_parser=mock_extract_with_tools_decorator_kwargs["output_parser"],
        json_mode=True,
        client=mock_extract_with_tools_decorator_kwargs["client"],
        call_params=mock_extract_with_tools_decorator_kwargs["call_params"],
    )
    mock_create_inner.assert_called_once_with(genre="fantasy", topic="magic")
    mock_get_json_output.assert_called_once_with(
        mock_create_inner.return_value,
        True,
    )
    mock_extract_tool_return.assert_called_once_with(
        mock_extract_with_tools_decorator_kwargs["response_model"],
        mock_get_json_output.return_value,
        False,
        {},
    )
    assert output == mock_extract_tool_return.return_value

    mock_extract_tool_return.side_effect = ValidationError.from_exception_data(
        title="", line_errors=[], input_type="json"
    )
    error = None
    try:
        _ = decorator(fn)(genre="fantasy", topic="magic")  # type: ignore
    except ValidationError as e:
        error = e
    assert error is not None
    assert error._response == mock_create_inner.return_value  # type: ignore

    mock_call_response.tools = [MagicMock()]
    output = decorated_fn(genre="fantasy", topic="magic")  # type: ignore
    assert output == mock_call_response


@patch(
    "mirascope.core.base._extract_with_tools.extract_tool_return",
    new_callable=MagicMock,
)
@patch("mirascope.core.base._extract_with_tools.create_factory", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_extract_with_tools_factory_async(
    mock_create_factory: MagicMock,
    mock_extract_tool_return: MagicMock,
    mock_setup_call: MagicMock,
    mock_extract_with_tools_decorator_kwargs: dict,
) -> None:
    """Tests the `extract_factory` method on a sync function."""
    mock_create_decorator = MagicMock()
    mock_create_inner = AsyncMock()
    mock_call_response = MagicMock()
    mock_call_response.tools = None
    mock_create_inner.return_value = mock_call_response
    mock_create_decorator.return_value = mock_create_inner
    mock_create_factory.return_value = mock_create_decorator
    mock_extract_tool_return.return_value = MyBaseModel()
    mock_get_json_output = MagicMock()

    decorator = partial(
        extract_with_tools_factory(
            TCallResponse=MagicMock,
            setup_call=mock_setup_call,
            get_json_output=mock_get_json_output,
        ),
        **mock_extract_with_tools_decorator_kwargs,
    )

    async def fn(genre: str, *, topic: str) -> None:
        """Recommend a {genre} book on {topic}."""

    decorated_fn = decorator(fn)
    assert decorated_fn._model == mock_extract_with_tools_decorator_kwargs["model"]  # pyright: ignore [reportFunctionMemberAccess]
    output = await decorated_fn(genre="fantasy", topic="magic")  # type: ignore
    mock_create_factory.assert_called_once_with(
        TCallResponse=MagicMock, setup_call=mock_setup_call
    )
    mock_create_decorator.assert_called_once_with(
        fn=fn,
        model=mock_extract_with_tools_decorator_kwargs["model"],
        tools=mock_extract_with_tools_decorator_kwargs["tools"],
        response_model=mock_extract_with_tools_decorator_kwargs["response_model"],
        output_parser=mock_extract_with_tools_decorator_kwargs["output_parser"],
        json_mode=True,
        client=mock_extract_with_tools_decorator_kwargs["client"],
        call_params=mock_extract_with_tools_decorator_kwargs["call_params"],
    )
    mock_create_inner.assert_called_once_with(genre="fantasy", topic="magic")
    mock_get_json_output.assert_called_once_with(
        mock_create_inner.return_value,
        True,
    )
    mock_extract_tool_return.assert_called_once_with(
        mock_extract_with_tools_decorator_kwargs["response_model"],
        mock_get_json_output.return_value,
        False,
        {},
    )
    assert output == mock_extract_tool_return.return_value

    mock_extract_tool_return.side_effect = ValidationError.from_exception_data(
        title="", line_errors=[], input_type="json"
    )
    error = None
    try:
        _ = await decorator(fn)(genre="fantasy", topic="magic")  # type: ignore
    except ValidationError as e:
        error = e
    assert error is not None
    assert error._response == mock_create_inner.return_value  # type: ignore

    mock_call_response.tools = [MagicMock()]
    output = await decorated_fn(genre="fantasy", topic="magic")  # type: ignore
    assert output == mock_call_response
