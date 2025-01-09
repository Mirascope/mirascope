"""Tests the internal `_create` module."""

from functools import partial
from typing import TypeVar, cast
from unittest.mock import MagicMock, patch

import pytest

from mirascope.core.base._create import create_factory
from mirascope.core.base.call_response import BaseCallResponse

_T = TypeVar("_T")


@pytest.fixture()
def mock_create_decorator_kwargs() -> dict:
    """Returns the mock kwargs (excluding fn) for the create `decorator` function."""

    def output_parser(output: _T) -> _T:
        return output

    return {
        "model": "model",
        "tools": [],
        "response_model": None,
        "output_parser": output_parser,
        "json_mode": True,
        "client": MagicMock(),
        "call_params": MagicMock(),
    }


@patch("mirascope.core.base._create.prompt_template", new_callable=MagicMock)
@patch(
    "mirascope.core.base._create.get_possible_user_message_param",
    new_callable=MagicMock,
)
@patch("mirascope.core.base._create.get_metadata", new_callable=MagicMock)
def test_create_factory_sync(
    mock_get_metadata: MagicMock,
    mock_get_possible_user_message_param: MagicMock,
    mock_prompt_template_decorator: MagicMock,
    mock_setup_call: MagicMock,
    mock_create_decorator_kwargs: dict,
) -> None:
    """Tests the `create_factory` method on a sync function."""
    (
        mock_create,
        mock_prompt_template,
        mock_messages,
        mock_tool_types,
        mock_call_kwargs,
    ) = mock_setup_call.return_value
    mock_create = cast(MagicMock, mock_create)

    decorator = partial(
        create_factory(TCallResponse=MagicMock, setup_call=mock_setup_call),
        **mock_create_decorator_kwargs,
    )

    dynamic_config = MagicMock()
    dynamic_config.get.return_value = None

    def fn(genre: str, *, topic: str):
        """Recommend a {genre} book on {topic}."""
        return dynamic_config

    mock_prompt_template_decorator.return_value = lambda x: fn

    decorated_fn = decorator(fn)
    assert decorated_fn._model == mock_create_decorator_kwargs["model"]  # pyright: ignore [reportFunctionMemberAccess]
    output: BaseCallResponse = decorated_fn("fantasy", topic="magic")  # type: ignore

    assert output.metadata == mock_get_metadata.return_value
    assert output.response == mock_create.return_value
    assert output.tool_types == mock_tool_types
    assert output.prompt_template == mock_prompt_template
    fn_args = {"genre": "fantasy", "topic": "magic"}
    assert output.fn_args == fn_args
    assert output.messages == mock_messages
    assert output.call_params == mock_create_decorator_kwargs["call_params"]
    assert output.call_kwargs == mock_call_kwargs
    assert (
        output.user_message_param == mock_get_possible_user_message_param.return_value
    )
    assert output.start_time is not None
    assert output.end_time is not None
    assert output._model == "model"

    mock_setup_call.assert_called_once_with(
        model="model",
        client=mock_create_decorator_kwargs["client"],
        fn=fn,
        fn_args=fn_args,
        dynamic_config=dynamic_config,
        tools=mock_create_decorator_kwargs["tools"],
        json_mode=mock_create_decorator_kwargs["json_mode"],
        call_params=mock_create_decorator_kwargs["call_params"],
        response_model=None,
        stream=False,
    )
    mock_create.assert_called_once_with(stream=False, **mock_call_kwargs)


@patch("mirascope.core.base._create.get_dynamic_configuration")
@patch("mirascope.core.base._create.prompt_template", new_callable=MagicMock)
@patch(
    "mirascope.core.base._create.get_possible_user_message_param",
    new_callable=MagicMock,
)
@patch("mirascope.core.base._create.get_metadata", new_callable=MagicMock)
@pytest.mark.parametrize(
    "dynamic_config_value, expected_dynamic_client",
    [
        (None, None),
        ({"client": "dynamic_client"}, "dynamic_client"),
        (MagicMock(), None),
    ],
)
def test_create_factory_sync_dynamic_config_cases(
    mock_get_metadata: MagicMock,
    mock_get_possible_user_message_param: MagicMock,
    mock_prompt_template_decorator: MagicMock,
    mock_get_dynamic_configuration: MagicMock,
    mock_setup_call: MagicMock,
    mock_create_decorator_kwargs: dict,
    dynamic_config_value,
    expected_dynamic_client,
) -> None:
    """Tests the create_factory with different dynamic_config values."""
    (
        mock_create,
        mock_prompt_template,
        mock_messages,
        mock_tool_types,
        mock_call_kwargs,
    ) = mock_setup_call.return_value
    mock_create = cast(MagicMock, mock_create)

    decorator = partial(
        create_factory(TCallResponse=MagicMock, setup_call=mock_setup_call),
        **mock_create_decorator_kwargs,
    )

    if isinstance(dynamic_config_value, MagicMock):
        dynamic_config_value.get.return_value = None

    mock_get_dynamic_configuration.return_value = dynamic_config_value

    def fn(genre: str, *, topic: str):
        """Recommend a {genre} book on {topic}."""

    mock_prompt_template_decorator.return_value = lambda x: fn

    decorated_fn = decorator(fn)
    decorated_fn("fantasy", topic="magic")  # type: ignore

    fn_args = {"genre": "fantasy", "topic": "magic"}

    expected_client = expected_dynamic_client or mock_create_decorator_kwargs["client"]

    # Assert that setup_call was called with expected client
    mock_setup_call.assert_called_once_with(
        model="model",
        client=expected_client,
        fn=fn,
        fn_args=fn_args,
        dynamic_config=dynamic_config_value,
        tools=mock_create_decorator_kwargs["tools"],
        json_mode=mock_create_decorator_kwargs["json_mode"],
        call_params=mock_create_decorator_kwargs["call_params"],
        response_model=None,
        stream=False,
    )
    # Other asserts as in previous test
    mock_create.assert_called_once_with(stream=False, **mock_call_kwargs)


@patch("mirascope.core.base._create.prompt_template", new_callable=MagicMock)
@patch(
    "mirascope.core.base._create.get_possible_user_message_param",
    new_callable=MagicMock,
)
@patch("mirascope.core.base._create.get_metadata", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_create_factory_async(
    mock_get_metadata: MagicMock,
    mock_get_possible_user_message_param: MagicMock,
    mock_prompt_template_decorator: MagicMock,
    mock_setup_call_async: MagicMock,
    mock_create_decorator_kwargs: dict,
) -> None:
    """Tests the `create_factory` method on a sync function."""
    (
        mock_create,
        mock_prompt_template,
        mock_messages,
        mock_tool_types,
        mock_call_kwargs,
    ) = mock_setup_call_async.return_value
    mock_create = cast(MagicMock, mock_create)

    decorator = partial(
        create_factory(TCallResponse=MagicMock, setup_call=mock_setup_call_async),
        **mock_create_decorator_kwargs,
    )

    dynamic_config = MagicMock()
    dynamic_config.get.return_value = None

    async def fn(genre: str, *, topic: str):
        """Recommend a {genre} book on {topic}."""
        return dynamic_config

    mock_prompt_template_decorator.return_value = lambda x: fn

    output: BaseCallResponse = await decorator(fn)("fantasy", topic="magic")  # type: ignore

    assert output.metadata == mock_get_metadata.return_value
    assert output.response == mock_create.return_value
    assert output.tool_types == mock_tool_types
    assert output.prompt_template == mock_prompt_template
    fn_args = {"genre": "fantasy", "topic": "magic"}
    assert output.fn_args == fn_args
    assert output.messages == mock_messages
    assert output.call_params == mock_create_decorator_kwargs["call_params"]
    assert output.call_kwargs == mock_call_kwargs
    assert (
        output.user_message_param == mock_get_possible_user_message_param.return_value
    )
    assert output.start_time is not None
    assert output.end_time is not None
    assert output._model == "model"

    mock_setup_call_async.assert_called_once_with(
        model="model",
        client=mock_create_decorator_kwargs["client"],
        fn=fn,
        fn_args=fn_args,
        dynamic_config=dynamic_config,
        tools=mock_create_decorator_kwargs["tools"],
        json_mode=mock_create_decorator_kwargs["json_mode"],
        call_params=mock_create_decorator_kwargs["call_params"],
        response_model=None,
        stream=False,
    )
    mock_create.assert_called_once_with(stream=False, **mock_call_kwargs)


@patch("mirascope.core.base._create.get_dynamic_configuration")
@patch("mirascope.core.base._create.prompt_template", new_callable=MagicMock)
@patch(
    "mirascope.core.base._create.get_possible_user_message_param",
    new_callable=MagicMock,
)
@patch("mirascope.core.base._create.get_metadata", new_callable=MagicMock)
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "dynamic_config_value, expected_dynamic_client",
    [
        (None, None),
        ({"client": "dynamic_client"}, "dynamic_client"),
        (MagicMock(), None),
    ],
)
async def test_create_factory_async_dynamic_config_cases(
    mock_get_metadata: MagicMock,
    mock_get_possible_user_message_param: MagicMock,
    mock_prompt_template_decorator: MagicMock,
    mock_get_dynamic_configuration: MagicMock,
    mock_setup_call_async: MagicMock,
    mock_create_decorator_kwargs: dict,
    dynamic_config_value,
    expected_dynamic_client,
) -> None:
    """Tests the create_factory with different dynamic_config values in async function."""
    (
        mock_create,
        mock_prompt_template,
        mock_messages,
        mock_tool_types,
        mock_call_kwargs,
    ) = mock_setup_call_async.return_value
    mock_create = cast(MagicMock, mock_create)

    decorator = partial(
        create_factory(TCallResponse=MagicMock, setup_call=mock_setup_call_async),
        **mock_create_decorator_kwargs,
    )

    # Ensure get_dynamic_configuration is an async function that returns the desired value
    async def async_get_dynamic_configuration(fn, args, kwargs):
        return dynamic_config_value

    mock_get_dynamic_configuration.side_effect = async_get_dynamic_configuration

    if isinstance(dynamic_config_value, MagicMock):
        dynamic_config_value.get.return_value = None

    async def fn(genre: str, *, topic: str):
        """Recommend a {genre} book on {topic}."""

    mock_prompt_template_decorator.return_value = lambda x: fn

    decorated_fn = decorator(fn)
    await decorated_fn("fantasy", topic="magic")  # type: ignore

    fn_args = {"genre": "fantasy", "topic": "magic"}

    expected_client = expected_dynamic_client or mock_create_decorator_kwargs["client"]

    # Assert that setup_call was called with expected client
    mock_setup_call_async.assert_called_once_with(
        model="model",
        client=expected_client,
        fn=fn,
        fn_args=fn_args,
        dynamic_config=dynamic_config_value,
        tools=mock_create_decorator_kwargs["tools"],
        json_mode=mock_create_decorator_kwargs["json_mode"],
        call_params=mock_create_decorator_kwargs["call_params"],
        response_model=None,
        stream=False,
    )
    # Other asserts as in previous test
    mock_create.assert_called_once_with(stream=False, **mock_call_kwargs)
