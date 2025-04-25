"""The `llm.response_format` decorator for defining response formats as classes."""

from collections.abc import Callable, Sequence
from typing import Any, Literal, Protocol, TypeVar, overload

from ..content import Content
from .response_format import ResponseFormat

T = TypeVar("T")
CovariantT = TypeVar("CovariantT", covariant=True)


class JsonResponseFormatDef(Protocol[CovariantT]):
    """Protocol for defining a JSON mode response format."""

    @classmethod
    def parse(cls, json: dict[str, Any]) -> CovariantT:
        """Parse a JSON response into an instance of the class.

        Args:
            json: The JSON response from the LLM.

        Returns:
            An instance of the class.
        """
        ...


class ToolResponseFormatDef(Protocol[CovariantT]):
    """Protocol for defining a tool mode response format."""

    @classmethod
    def parse(cls, args: dict[str, Any]) -> CovariantT:
        """Parse a tool call response into an instance of the class.

        Args:
            args: The arguments generated for the tool call.

        Returns:
            An instance of the class.
        """
        ...


class ContentResponseFormatDef(Protocol[CovariantT]):
    """Protocol for defining a text mode response format."""

    @classmethod
    def parse(cls, content: Content | Sequence[Content]) -> CovariantT:
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
        JsonResponseFormatDef[T]
        | ToolResponseFormatDef[T]
        | ContentResponseFormatDef[T]
    ],
) -> ResponseFormat[T]:
    """Overload for no arguments, which requires a parser classmethod."""
    ...


@overload
def response_format(
    *,
    parser: None = None,
    strict: bool = False,
) -> Callable[
    [JsonResponseFormatDef[T] | ToolResponseFormatDef[T] | ContentResponseFormatDef[T]],
    ResponseFormat[T],
]:
    """Overload for no default parser, which requires a parser classmethod."""
    ...


@overload
def response_format(
    *,
    parser: Literal["json", "tool"],
    strict: bool = False,
) -> Callable[[type[T]], ResponseFormat[T]]:
    """Overload for setting a default parser."""
    ...


def response_format(
    __cls=None,
    *,
    parser: Literal["json", "tool"] | None = None,
    strict: bool = False,
) -> (
    ResponseFormat[T]
    | Callable[
        [
            JsonResponseFormatDef[T]
            | ToolResponseFormatDef[T]
            | ContentResponseFormatDef[T]
        ],
        ResponseFormat[T],
    ]
    | Callable[[type[T]], ResponseFormat[T]]
):
    '''Decorator that defines a structured response format for LLM outputs.

    This decorator can be applied to a class to define how LLM responses should be
    structured and parsed. The decorated class becomes a `ResponseFormat` that can be
    used with `llm.call` to specify the expected response structure.

    Args:
        parser: The default parser to use, if any:
            - "json": Use JSON mode for structured outputs
            - "tool": Use forced tool calling to structure outputs
            - None: No default parser is applied, and a parser classmethod is required
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
            def parse(cls, text: str) -> Self:
                """FORMATTING INSTRUCTIONS:

                ```plaintext
                {title} by {author}
                ```
                """
                title, author = text.split(" by ")
                return cls(title=title.strip(), author=author.strip())
        ```
    '''
    raise NotImplementedError()
