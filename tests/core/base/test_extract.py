"""Tests the internal `_extract` module."""

from functools import partial
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, ValidationError

from mirascope.core.base._extract import extract_factory


@pytest.fixture()
def mock_extract_decorator_kwargs() -> dict:
    """Returns the mock kwargs (excluding fn) for the extract `decorator` function."""
    return {
        "model": "model",
        "response_model": BaseModel,
        "output_parser": None,
        "json_mode": True,
        "client": MagicMock(),
        "call_params": MagicMock(),
    }


class MyBaseModel(BaseModel):
    """Empty base model for testing."""


class CustomError(Exception):
    """Custom error for testing general exceptions."""

    pass


@patch("mirascope.core.base._extract.setup_extract_tool", new_callable=MagicMock)
@patch("mirascope.core.base._extract.extract_tool_return", new_callable=MagicMock)
@patch("mirascope.core.base._extract.create_factory", new_callable=MagicMock)
def test_extract_factory_sync(
    mock_create_factory: MagicMock,
    mock_extract_tool_return: MagicMock,
    mock_setup_extract_tool: MagicMock,
    mock_setup_call: MagicMock,
    mock_extract_decorator_kwargs: dict,
) -> None:
    """Tests the `extract_factory` method on a sync function."""
    mock_create_decorator = MagicMock()
    mock_create_inner = MagicMock()
    mock_create_decorator.return_value = mock_create_inner
    mock_create_factory.return_value = mock_create_decorator
    mock_extract_tool_return.return_value = MyBaseModel()
    mock_get_json_output = MagicMock()

    decorator = partial(
        extract_factory(
            TCallResponse=MagicMock,
            TToolType=MagicMock,
            setup_call=mock_setup_call,
            get_json_output=mock_get_json_output,
        ),
        **mock_extract_decorator_kwargs,
    )

    def fn(genre: str, *, topic: str) -> None:
        """Recommend a {genre} book on {topic}."""

    decorated_fn = decorator(fn)
    assert decorated_fn._model == mock_extract_decorator_kwargs["model"]  # pyright: ignore [reportFunctionMemberAccess]
    output = decorated_fn(genre="fantasy", topic="magic")  # type: ignore
    mock_create_factory.assert_called_once_with(
        TCallResponse=MagicMock, setup_call=mock_setup_call
    )
    mock_create_decorator.assert_called_once_with(
        fn=fn,
        model=mock_extract_decorator_kwargs["model"],
        tools=None,
        response_model=BaseModel,
        output_parser=None,
        json_mode=mock_extract_decorator_kwargs["json_mode"],
        client=mock_extract_decorator_kwargs["client"],
        call_params=mock_extract_decorator_kwargs["call_params"],
    )
    mock_create_inner.assert_called_once_with(genre="fantasy", topic="magic")
    mock_get_json_output.assert_called_once_with(
        mock_create_inner.return_value, mock_extract_decorator_kwargs["json_mode"]
    )
    mock_extract_tool_return.assert_called_once_with(
        mock_extract_decorator_kwargs["response_model"],
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


@patch("mirascope.core.base._extract.setup_extract_tool", new_callable=MagicMock)
@patch("mirascope.core.base._extract.extract_tool_return", new_callable=MagicMock)
@patch("mirascope.core.base._extract.create_factory", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_extract_factory_async(
    mock_create_factory: MagicMock,
    mock_extract_tool_return: MagicMock,
    mock_setup_extract_tool: MagicMock,
    mock_setup_call: MagicMock,
    mock_extract_decorator_kwargs: dict,
) -> None:
    """Tests the `extract_factory` method on an async function."""
    mock_create_decorator = MagicMock()
    mock_create_inner = AsyncMock()
    mock_create_decorator.return_value = mock_create_inner
    mock_create_factory.return_value = mock_create_decorator
    mock_extract_tool_return.return_value = MyBaseModel()
    mock_get_json_output = MagicMock()

    decorator = partial(
        extract_factory(
            TCallResponse=MagicMock,
            TToolType=MagicMock,
            setup_call=mock_setup_call,
            get_json_output=mock_get_json_output,
        ),
        **mock_extract_decorator_kwargs,
    )

    async def fn(genre: str, *, topic: str) -> None:
        """Recommend a {genre} book on {topic}."""

    output = await decorator(fn)(genre="fantasy", topic="magic")  # type: ignore
    mock_create_factory.assert_called_once_with(
        TCallResponse=MagicMock, setup_call=mock_setup_call
    )
    mock_create_decorator.assert_called_once_with(
        fn=fn,
        model=mock_extract_decorator_kwargs["model"],
        tools=None,
        response_model=BaseModel,
        output_parser=None,
        json_mode=mock_extract_decorator_kwargs["json_mode"],
        client=mock_extract_decorator_kwargs["client"],
        call_params=mock_extract_decorator_kwargs["call_params"],
    )
    mock_get_json_output.assert_called_once_with(
        mock_create_inner.return_value, mock_extract_decorator_kwargs["json_mode"]
    )
    mock_extract_tool_return.assert_called_once_with(
        mock_extract_decorator_kwargs["response_model"],
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


@patch("mirascope.core.base._extract.setup_extract_tool", new_callable=MagicMock)
@patch("mirascope.core.base._extract.extract_tool_return", new_callable=MagicMock)
@patch("mirascope.core.base._extract.create_factory", new_callable=MagicMock)
def test_extract_factory_sync_validation_error(
    mock_create_factory: MagicMock,
    mock_extract_tool_return: MagicMock,
    mock_setup_extract_tool: MagicMock,
    mock_setup_call: MagicMock,
    mock_extract_decorator_kwargs: dict,
) -> None:
    """Test the sync case where ValidationError is raised."""
    mock_create_decorator = MagicMock()
    mock_create_inner = MagicMock()
    mock_create_decorator.return_value = mock_create_inner
    mock_create_factory.return_value = mock_create_decorator
    mock_get_json_output = MagicMock()

    decorator = partial(
        extract_factory(
            TCallResponse=MagicMock,
            TToolType=MagicMock,
            setup_call=mock_setup_call,
            get_json_output=mock_get_json_output,
        ),
        **mock_extract_decorator_kwargs,
    )

    def fn(genre: str) -> None:
        """Test function."""

    mock_extract_tool_return.side_effect = ValidationError.from_exception_data(
        title="", line_errors=[], input_type="json"
    )

    with pytest.raises(ValidationError) as e:
        _ = decorator(fn)(genre="fantasy")  # pyright: ignore [reportCallIssue]

    assert e.value._response == mock_create_inner.return_value  # pyright: ignore [reportAttributeAccessIssue]


@patch("mirascope.core.base._extract.setup_extract_tool", new_callable=MagicMock)
@patch("mirascope.core.base._extract.extract_tool_return", new_callable=MagicMock)
@patch("mirascope.core.base._extract.create_factory", new_callable=MagicMock)
def test_extract_factory_sync_general_error(
    mock_create_factory: MagicMock,
    mock_extract_tool_return: MagicMock,
    mock_setup_extract_tool: MagicMock,
    mock_setup_call: MagicMock,
    mock_extract_decorator_kwargs: dict,
) -> None:
    """Test the sync case where a general Exception is raised."""
    mock_create_decorator = MagicMock()
    mock_create_inner = MagicMock()
    mock_create_decorator.return_value = mock_create_inner
    mock_create_factory.return_value = mock_create_decorator
    mock_get_json_output = MagicMock()
    mock_get_json_output.side_effect = CustomError("Custom error occurred")

    decorator = partial(
        extract_factory(
            TCallResponse=MagicMock,
            TToolType=MagicMock,
            setup_call=mock_setup_call,
            get_json_output=mock_get_json_output,
        ),
        **mock_extract_decorator_kwargs,
    )

    def fn(genre: str) -> None:
        """Test function."""

    with pytest.raises(CustomError) as e:
        _ = decorator(fn)(genre="fantasy")  # pyright: ignore [reportCallIssue]

    assert e.value._response == mock_create_inner.return_value  # pyright: ignore [reportAttributeAccessIssue]


@patch("mirascope.core.base._extract.setup_extract_tool", new_callable=MagicMock)
@patch("mirascope.core.base._extract.extract_tool_return", new_callable=MagicMock)
@patch("mirascope.core.base._extract.create_factory", new_callable=MagicMock)
def test_extract_factory_sync_json_output_error(
    mock_create_factory: MagicMock,
    mock_extract_tool_return: MagicMock,
    mock_setup_extract_tool: MagicMock,
    mock_setup_call: MagicMock,
    mock_extract_decorator_kwargs: dict,
) -> None:
    """Test the sync case where get_json_output raises an Exception."""
    mock_create_decorator = MagicMock()
    mock_create_inner = MagicMock()
    mock_create_decorator.return_value = mock_create_inner
    mock_create_factory.return_value = mock_create_decorator
    mock_get_json_output = MagicMock()
    mock_get_json_output.side_effect = ValueError("Invalid JSON format")

    decorator = partial(
        extract_factory(
            TCallResponse=MagicMock,
            TToolType=MagicMock,
            setup_call=mock_setup_call,
            get_json_output=mock_get_json_output,
        ),
        **mock_extract_decorator_kwargs,
    )

    def fn(genre: str) -> None:
        """Test function."""

    with pytest.raises(ValueError) as e:
        _ = decorator(fn)(genre="fantasy")  # pyright: ignore [reportCallIssue]

    assert e.value._response == mock_create_inner.return_value  # pyright: ignore [reportAttributeAccessIssue]


@patch("mirascope.core.base._extract.setup_extract_tool", new_callable=MagicMock)
@patch("mirascope.core.base._extract.extract_tool_return", new_callable=MagicMock)
@patch("mirascope.core.base._extract.create_factory", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_extract_factory_async_general_error(
    mock_create_factory: MagicMock,
    mock_extract_tool_return: MagicMock,
    mock_setup_extract_tool: MagicMock,
    mock_setup_call: MagicMock,
    mock_extract_decorator_kwargs: dict,
) -> None:
    """Test the async case where a general Exception is raised."""
    mock_create_decorator = MagicMock()
    mock_create_inner = AsyncMock()
    mock_create_decorator.return_value = mock_create_inner
    mock_create_factory.return_value = mock_create_decorator
    mock_get_json_output = MagicMock()
    mock_extract_tool_return.side_effect = CustomError("Custom error in async")

    decorator = partial(
        extract_factory(
            TCallResponse=MagicMock,
            TToolType=MagicMock,
            setup_call=mock_setup_call,
            get_json_output=mock_get_json_output,
        ),
        **mock_extract_decorator_kwargs,
    )

    async def fn(genre: str) -> None:
        """Async test function."""

    with pytest.raises(CustomError) as e:
        await decorator(fn)(genre="fantasy")  # pyright: ignore [reportCallIssue]

    assert e.value._response == mock_create_inner.return_value  # pyright: ignore [reportAttributeAccessIssue]
