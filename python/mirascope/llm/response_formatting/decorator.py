"""The `llm.response_format` decorator for defining response formats as classes."""

from collections.abc import Callable, Sequence
from typing import Any, Literal, Protocol, overload

from ..content import AssistantContent
from ..types import FormatCovariantT, RequiredFormatT


class JsonResponseFormatDef(Protocol[FormatCovariantT]):
    """Protocol for defining a JSON mode response format."""

    @classmethod
    def parse(cls, json: dict[str, Any]) -> FormatCovariantT:
        """Parse a JSON response into an instance of the class.

        Args:
            json: The JSON response from the LLM.

        Returns:
            An instance of the class.
        """
        ...


class ToolResponseFormatDef(Protocol[FormatCovariantT]):
    """Protocol for defining a tool mode response format."""

    @classmethod
    def parse(cls, args: dict[str, Any]) -> FormatCovariantT:
        """Parse a tool call response into an instance of the class.

        Args:
            args: The arguments generated for the tool call.

        Returns:
            An instance of the class.
        """
        ...


class ContentResponseFormatDef(Protocol[FormatCovariantT]):
    """Protocol for defining a content mode response format."""

    @classmethod
    def parse(
        cls, content: AssistantContent | Sequence[AssistantContent]
    ) -> FormatCovariantT:
        """Parse a response into an instance of the class.

        Args:
            content: The array of content response from the LLM.

        Returns:
            An instance of the class.
        """
        ...


@overload
def response_format(
    __cls: type[
        JsonResponseFormatDef[RequiredFormatT]
        | ToolResponseFormatDef[RequiredFormatT]
        | ContentResponseFormatDef[RequiredFormatT]
    ],
) -> type[RequiredFormatT]:
    """Overload for no arguments, which requires a parser classmethod."""
    ...


@overload
def response_format(
    *,
    parser: None = None,
    strict: bool = False,
) -> Callable[
    [
        JsonResponseFormatDef[RequiredFormatT]
        | ToolResponseFormatDef[RequiredFormatT]
        | ContentResponseFormatDef[RequiredFormatT]
    ],
    type[RequiredFormatT],
]:
    """Overload for no default parser, which requires a parser classmethod."""
    ...


@overload
def response_format(
    *,
    parser: Literal["json", "tool"],
    strict: bool = False,
) -> Callable[[type[RequiredFormatT]], type[RequiredFormatT]]:
    """Overload for setting a default parser."""
    ...


def response_format(
    __cls=None,
    *,
    parser: Literal["json", "tool"] | None = None,
    strict: bool = False,
) -> (
    RequiredFormatT
    | Callable[
        [
            JsonResponseFormatDef[RequiredFormatT]
            | ToolResponseFormatDef[RequiredFormatT]
            | ContentResponseFormatDef[RequiredFormatT]
        ],
        type[RequiredFormatT],
    ]
    | Callable[[type[RequiredFormatT]], type[RequiredFormatT]]
):
    '''Decorator that defines a structured response format for LLM outputs.

    This decorator operates as a dataclass transformation so that the original class
    retains its original behavior and typing. At definition time, the decorator will
    set the `__response_format__: ResponseFormat` attribute on the class, which is used
    downstream to determine how to parse the LLM response.

    By default, the decorator requires the decorated class has a `parse` classmethod.
    The single argument of this method determines how to set the call parameters for
    structuring the response, which must be one of:
        - `content: AssistantContent | Sequence[AssistantContent]` for structuring the content itself
        - `json: dict[str, Any]` for structuring the response using JSON mode
        - `args: dict[str, Any]` for structuring the response using tool mode

    You can also set the `parser` argument to opt-in to a default parser.

    Args:
        parser: The default parser to use, if any:
            - "json": Use JSON mode for structured outputs
            - "tool": Use forced tool calling to structure outputs
            - None: No default parser is applied, and a `parse` classmethod is required
        strict: Whether to use strict structured outputs when supported by the model.
            Default is False.

    Returns:
        A decorator function that converts the class into a `ResponseFormat`.

    Example:

        A simple `Book` response formatted using the default "json" parser:

        ```python
        from mirascope import llm

        @llm.response_format(parser="json")
        class Book:
            title: str
            author: str
        ```

    Example:

        A custom text parser

        ```python
        from typing_extensions import Self

        from mirascope import llm

        @llm.response_format
        class Book:
            title: str
            author: str

            @classmethod
            def parse(cls, content: AssistantContent | Sequence[AssistantContent]) -> Book:
                """FORMATTING INSTRUCTIONS:

                ```plaintext
                {title} by {author}
                ```
                """
                title, author = content[0].text.split(" by ")
                return cls(title=title.strip(), author=author.strip())
        ```
    '''
    raise NotImplementedError()
