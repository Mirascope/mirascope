"""Response formatting interfaces for structuring LLM outputs.

This module provides a way to define structured output formats for LLM responses.
The `@response_format` decorator can be applied to classes to specify how LLM
outputs should be structured and parsed.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import (
    Any,
    Generic,
    Literal,
    Protocol,
    TypeVar,
    overload,
)

__all__ = ["ResponseFormat", "response_format"]


T = TypeVar("T")
CovariantT = TypeVar("CovariantT", covariant=True)


class JsonParserFn(Protocol[CovariantT]):
    """Protocol for a JSON mode response format parser."""

    def __call__(self, json: dict[str, Any]) -> CovariantT:
        """Parse a JSON response into an instance of the class.

        Args:
            json: The JSON response from the LLM.

        Returns:
            An instance of the class `CovariantT`.
        """
        ...


class ToolParserFn(Protocol[CovariantT]):
    """Protocol for a tool mode response format parser."""

    def __call__(self, args: dict[str, Any]) -> CovariantT:
        """Parse a tool call response into an instance of the class.

        Args:
            args: The arguments generated for the tool call.

        Returns:
            An instance of the class `CovariantT`.
        """
        ...


class TextParserFn(Protocol[CovariantT]):
    """Protocol for a text mode response format parser."""

    def __call__(self, text: str) -> CovariantT:
        """Parse a text response into an instance of the class.

        Args:
            text: The text response from the LLM.

        Returns:
            An instance of the class `CovariantT`.
        """
        ...


@dataclass
class ResponseFormat(Generic[T]):
    """Class representing a structured output format for LLM responses.

    A ResponseFormat defines how LLM responses should be structured and parsed.
    It includes metadata about the format mode, whether to use strict validation,
    and the schema for the expected output.

    This class is not instantiated directly but is created by applying the
    `@response_format()` decorator to a class definition.

    When decorated with `@response_format()`, the class retains its original
    fields and constructor, while adding the ResponseFormat functionality:

    Example:
        ```python
        from mirascope import llm

        @llm.response_format()
        class Book:
            title: str
            author: str

        @llm.call("openai:gpt-4o", response_format=Book)
        def recommend_book(genre: str) -> list[llm.Message]:
            return [
                llm.system("You are a helpful assistant."),
                llm.user(f"Recommend a {genre} book.")
            ]

        response: llm.Response[Book] = recommend_book("fantasy")
        book: Book = response.format()
        print(f"{book.title} by {book.author}")
        ```
    """

    original: type[T]
    """The original class definition before being decorated."""

    schema: dict[str, Any]
    """The original class definition before being decorated."""

    parser: JsonParserFn[T] | ToolParserFn[T] | TextParserFn[T]
    """The parser for formatting the response."""

    mode: Literal["json", "tool", "text"]
    """The mode of the response format, determined from the parser's signature."""

    formatting_instructions: str
    """Response formatting instructions, pulled from the parser's docstring."""

    strict: bool
    """Whether the response format should use strict validation when supported."""


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


class TextResponseFormatDef(Protocol[CovariantT]):
    """Protocol for defining a text mode response format."""

    @classmethod
    def parse(cls, text: str) -> CovariantT:
        """Parse a text response into an instance of the class.

        Args:
            text: The text response from the LLM.

        Returns:
            An instance of the class.
        """
        ...


@overload
def response_format(
    __cls: type[
        JsonResponseFormatDef[T] | ToolResponseFormatDef[T] | TextResponseFormatDef[T]
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
    [JsonResponseFormatDef[T] | ToolResponseFormatDef[T] | TextResponseFormatDef[T]],
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
            | TextResponseFormatDef[T]
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
