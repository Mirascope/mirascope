"""Tests for the _internal utils module."""

from textwrap import dedent
from typing import Annotated

import pytest
from pydantic import BaseModel

from mirascope.core.base import BaseTool, _utils


def test_format_prompt_template() -> None:
    """Tests the `format_prompt_template` function."""
    prompt_template = """
    Recommend a {empty_list} book.

    I like the following genres:
    {genres}

    Here are some of my favorite authors and their books:
    {authors_and_books}
    """

    empty_list = []
    genres = ["fantasy", "mystery"]
    authors_and_books = [
        ["The Name of the Wind", "The Wise Man's Fears"],
        ["The Da Vinci Code", "Angels & Demons"],
    ]
    attrs = {
        "empty_list": empty_list,
        "genres": genres,
        "authors_and_books": authors_and_books,
    }
    formatted_prompt_template = _utils.format_prompt_template(prompt_template, attrs)
    assert (
        formatted_prompt_template
        == dedent(
            """
            Recommend a  book.

            I like the following genres:
            fantasy
            mystery

            Here are some of my favorite authors and their books:
            The Name of the Wind
            The Wise Man's Fears

            The Da Vinci Code
            Angels & Demons
            """
        ).strip()
    )


def test_parse_prompt_messages() -> None:
    """Tests the `parse_prompt_messages` function."""
    template = """
    SYSTEM: You are the world's greatest librarian.
    MESSAGES: {messages}
    USER: Recommend a book.
    """

    messages = [
        {"role": "user", "content": "Hi!"},
        {"role": "assistant", "content": "Hello!"},
    ]
    parsed_messages = _utils.parse_prompt_messages(
        roles=["system", "user", "assistant"],
        template=template,
        attrs={"messages": messages},
    )
    assert parsed_messages == [
        {"role": "system", "content": "You are the world's greatest librarian."},
        {"role": "user", "content": "Hi!"},
        {"role": "assistant", "content": "Hello!"},
        {"role": "user", "content": "Recommend a book."},
    ]

    with pytest.raises(ValueError):
        _utils.parse_prompt_messages(
            roles=["system"], template=template, attrs={"messages": None}
        )

    with pytest.raises(ValueError):
        _utils.parse_prompt_messages(
            roles=["system"], template=template, attrs={"messages": "Hi!"}
        )


def test_convert_function_to_base_model() -> None:
    """Tests conversion of a `Callable` signature to a `BaseModel`."""

    def fn(model_name: str = "", self=None, cls=None) -> str:
        """A test function.

        Args:
            model_name: A test parameter.
        """
        return model_name

    model = _utils.convert_function_to_base_tool(fn, BaseTool)
    assert (
        model._description()
        == """A test function.\n\nArgs:\n    model_name: A test parameter."""
    )
    assert model._name() == "fn"

    tool = model(model_name="test", tool_call="test")  # type: ignore
    assert tool.call() == "test"


def test_convert_function_to_base_model_errors() -> None:
    """Tests the various `ValueErro` cases in `convert_function_to_base_model`."""

    def empty(param) -> str: ...  # pragma: no cover

    with pytest.raises(ValueError):
        _utils.convert_function_to_base_tool(empty, BaseTool)

    def wrong_param_name(param: str) -> str:
        """A test function.

        Args:
            wrong_name: ...
        """
        ...  # pragma: no cover

    with pytest.raises(ValueError):
        _utils.convert_function_to_base_tool(wrong_param_name, BaseTool)

    def missing_param_description(param: str) -> str:
        """A test function.

        Args:
            param:
        """
        ...  # pragma: no cover

    with pytest.raises(ValueError):
        _utils.convert_function_to_base_tool(missing_param_description, BaseTool)


def test_convert_base_model_to_base_tool() -> None:
    """Tests conversion of a `BaseModel` to a `BaseTool`."""

    class Model(BaseModel):
        param: str

        def call(self) -> str:
            return self.param

    model = _utils.convert_base_model_to_base_tool(Model, BaseTool)
    assert model._description() == _utils.DEFAULT_TOOL_DOCSTRING
    assert model(param="test").call() == "test"  # type: ignore


def test_convert_base_type_to_tool() -> None:
    """Tests conversion of a `BaseType` to a `BaseTool`."""

    model = _utils.convert_base_type_to_base_tool(Annotated[str, "a string"], BaseTool)  # type: ignore
    assert model._description() == _utils.DEFAULT_TOOL_DOCSTRING
    assert model._name() == "str"
