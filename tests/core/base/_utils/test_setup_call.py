"""Tests the `_utils.setup_call` function."""

from typing import cast

import pytest

from mirascope.core.base import BaseCallParams, CommonCallParams
from mirascope.core.base._utils._setup_call import setup_call
from mirascope.core.base.dynamic_config import BaseDynamicConfig
from mirascope.core.base.message_param import BaseMessageParam
from mirascope.core.base.prompt import prompt_template
from mirascope.core.base.tool import BaseTool


def test_setup_call() -> None:
    """Tests the `setup_call` function."""

    @prompt_template("Recommend a {genre} book.")
    def fn(genre: str) -> None: ...  # pragma: no cover

    def convert_common_call_params(
        common_params: CommonCallParams,
    ) -> BaseCallParams: ...

    template, messages, tool_types, call_kwargs = setup_call(
        fn,
        {"genre": "fantasy"},
        None,
        None,
        BaseTool,
        {"arg": "value"},  # type: ignore
        convert_common_call_params,  # pyright: ignore [reportArgumentType]
    )

    assert template == "Recommend a {genre} book."
    assert messages == [
        BaseMessageParam(role="user", content="Recommend a fantasy book.")
    ]
    assert tool_types is None
    assert call_kwargs == {"arg": "value"}

    @prompt_template("Recommend a {genre} book.")
    def prompt_template_fn(genre: str) -> None:
        """Normal docstr."""

    assert setup_call(
        prompt_template_fn,
        {"genre": "fantasy"},
        None,
        None,
        BaseTool,
        {"arg": "value"},  # type: ignore
        convert_common_call_params,  # pyright: ignore [reportArgumentType]
    ) == (template, messages, tool_types, call_kwargs)


def test_setup_call_with_dynamic_config() -> None:
    """Tests the `setup_call` function with dynamic config."""

    class FormatBook(BaseTool):
        title: str
        author: str

        def call(self) -> None:
            """Format book tool call method."""

        @classmethod
        def tool_schema(cls):
            return {"type": "function", "name": cls._name()}

    def format_book(title: str, author: str) -> None:
        """Format book tool."""

    dynamic_config: BaseDynamicConfig = {
        "metadata": {"tags": {"version:0001"}},
        "computed_fields": {"genre": "fantasy"},
        "tools": [FormatBook, format_book],
        "call_params": {"arg": "value"},
    }

    @prompt_template("Recommend a {genre} book.")
    def fn() -> None: ...  # pragma: no cover

    def convert_common_call_params(common_params: CommonCallParams) -> BaseCallParams:
        """Test conversion function for common parameters."""
        return cast(BaseCallParams, common_params)

    template, messages, tool_types, call_kwargs = setup_call(
        fn,
        {},
        dynamic_config,
        None,
        FormatBook,
        {},
        convert_common_call_params,  # pyright: ignore [reportArgumentType]
    )

    assert template == "Recommend a {genre} book."
    assert messages == [
        BaseMessageParam(role="user", content="Recommend a fantasy book.")
    ]
    assert tool_types and len(tool_types) == 2
    tool0, tool1 = tool_types
    assert tool0._name() == "FormatBook"
    assert tool1._name() == "format_book"
    assert call_kwargs == {
        "arg": "value",
        "tools": [
            {"type": "function", "name": "FormatBook"},
            {"type": "function", "name": "format_book"},
        ],
    }


@pytest.mark.parametrize("messages_type", [list, tuple])
def test_setup_call_with_custom_messages(messages_type) -> None:
    """Tests the `setup_call` function with custom messages."""

    custom_messages = messages_type(
        {
            "role": "user",
            "content": [{"type": "text", "text": "Recommend a fantasy book."}],
        }
    )
    dynamic_config: BaseDynamicConfig = {"messages": custom_messages}

    def fn() -> None:
        """Normal docstr."""

    def convert_common_call_params(common_params: CommonCallParams) -> BaseCallParams:
        """Test conversion function for common parameters."""
        return cast(BaseCallParams, common_params)

    template, messages, tool_types, call_kwargs = setup_call(
        fn,
        {},
        dynamic_config,
        None,
        BaseTool,
        {},
        convert_common_call_params,  # pyright: ignore [reportArgumentType]
    )
    assert template is None
    assert list(custom_messages) == messages
    assert tool_types is None
    assert call_kwargs == {}


# tests/core/base/_utils/test_setup_call.py


def test_setup_call_with_common_params() -> None:
    """Tests setup_call with CommonCallParams.

    Verifies that CommonCallParams are correctly converted using the provided
    conversion function.
    """
    common_params: CommonCallParams = {
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9,
    }

    def convert_common_call_params(params: CommonCallParams) -> BaseCallParams:
        """Test conversion function that prefixes parameters with 'converted_'."""
        return cast(
            BaseCallParams,
            {
                "converted_temperature": params.get("temperature"),
                "converted_max_tokens": params.get("max_tokens"),
                "converted_top_p": params.get("top_p"),
            },
        )

    @prompt_template("Recommend a {genre} book.")
    def fn(genre: str) -> None: ...  # pragma: no cover

    template, messages, tool_types, call_kwargs = setup_call(
        fn,
        {"genre": "fantasy"},
        None,
        None,
        BaseTool,
        common_params,
        convert_common_call_params,  # pyright: ignore [reportArgumentType]
    )

    assert template == "Recommend a {genre} book."
    assert messages == [
        BaseMessageParam(role="user", content="Recommend a fantasy book.")
    ]
    assert tool_types is None
    assert call_kwargs == {
        "converted_temperature": 0.7,
        "converted_max_tokens": 100,
        "converted_top_p": 0.9,
    }


def test_setup_call_with_mixed_common_and_call_params() -> None:
    """Tests setup_call with a mix of CommonCallParams and provider-specific params.

    Verifies that when the input contains both common parameters and provider-specific
    parameters, only the common parameters are converted while others remain unchanged.
    """
    # Dictionary containing both CommonCallParams keys and provider-specific keys
    mixed_params = {
        "temperature": 0.7,  # CommonCallParams key
        "max_tokens": 100,  # CommonCallParams key
        "custom_param": "value",  # Provider-specific key
    }

    def convert_common_call_params(params: CommonCallParams) -> BaseCallParams: ...

    @prompt_template("Recommend a {genre} book.")
    def fn(genre: str) -> None: ...  # pragma: no cover

    template, messages, tool_types, call_kwargs = setup_call(
        fn,
        {"genre": "fantasy"},
        None,
        None,
        BaseTool,
        mixed_params,  # type: ignore
        convert_common_call_params,  # pyright: ignore [reportArgumentType]
    )

    # Provider-specific parameters remain unchanged while common parameters are converted
    assert call_kwargs == mixed_params


def test_setup_call_with_dynamic_config_and_common_params() -> None:
    """Tests setup_call with both dynamic config and CommonCallParams.

    Verifies that parameters from dynamic config are properly merged with
    converted common parameters.
    """
    common_params: CommonCallParams = {
        "temperature": 0.7,
        "max_tokens": 100,
    }

    dynamic_config: BaseDynamicConfig = {
        "call_params": {
            "custom_param": "value",
        }
    }

    def convert_common_call_params(params: CommonCallParams) -> BaseCallParams:
        """Test conversion function for common parameters."""
        return cast(
            BaseCallParams,
            {
                "converted_temperature": params.get("temperature"),
                "converted_max_tokens": params.get("max_tokens"),
            },
        )

    @prompt_template("Recommend a {genre} book.")
    def fn(genre: str) -> None: ...  # pragma: no cover

    template, messages, tool_types, call_kwargs = setup_call(
        fn,
        {"genre": "fantasy"},
        dynamic_config,
        None,
        BaseTool,
        common_params,
        convert_common_call_params,  # pyright: ignore [reportArgumentType]
    )

    # Results from convert_common_call_params are merged with dynamic_config's call_params
    assert call_kwargs == {
        "converted_temperature": 0.7,
        "converted_max_tokens": 100,
        "custom_param": "value",
    }


def test_setup_call_with_empty_common_params() -> None:
    """Tests setup_call with empty CommonCallParams.

    Verifies that the function handles empty parameter dictionaries correctly
    and maintains other expected behavior.
    """

    def convert_common_call_params(params: CommonCallParams) -> BaseCallParams:
        """Test conversion function for common parameters."""
        return cast(BaseCallParams, params)

    @prompt_template("Recommend a {genre} book.")
    def fn(genre: str) -> None: ...  # pragma: no cover

    template, messages, tool_types, call_kwargs = setup_call(
        fn,
        {"genre": "fantasy"},
        None,
        None,
        BaseTool,
        {},  # Empty CommonCallParams
        convert_common_call_params,  # pyright: ignore [reportArgumentType]
    )

    assert template == "Recommend a {genre} book."
    assert messages == [
        BaseMessageParam(role="user", content="Recommend a fantasy book.")
    ]
    assert tool_types is None
    assert call_kwargs == {}
