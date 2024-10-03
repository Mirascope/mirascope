"""Tests the `_utils.setup_call` function."""

from mirascope.core.base._utils._setup_call import setup_call
from mirascope.core.base.dynamic_config import BaseDynamicConfig
from mirascope.core.base.message_param import BaseMessageParam
from mirascope.core.base.prompt import prompt_template
from mirascope.core.base.tool import BaseTool


def test_setup_call() -> None:
    """Tests the `setup_call` function."""

    @prompt_template("Recommend a {genre} book.")
    def fn(genre: str) -> None: ...  # pragma: no cover

    template, messages, tool_types, call_kwargs = setup_call(
        fn,
        {"genre": "fantasy"},
        None,
        None,
        BaseTool,
        {"arg": "value"},  # type: ignore
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

    template, messages, tool_types, call_kwargs = setup_call(
        fn, {}, dynamic_config, None, FormatBook, {}
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


def test_setup_call_with_custom_messages() -> None:
    """Tests the `setup_call` function with custom messages."""

    custom_messages = [
        {
            "role": "user",
            "content": [{"type": "text", "text": "Recommend a fantasy book."}],
        }
    ]
    dynamic_config: BaseDynamicConfig = {"messages": custom_messages}

    def fn() -> None:
        """Normal docstr."""

    template, messages, tool_types, call_kwargs = setup_call(
        fn, {}, dynamic_config, None, BaseTool, {}
    )
    assert template is None
    assert custom_messages == messages
    assert tool_types is None
    assert call_kwargs == {}
