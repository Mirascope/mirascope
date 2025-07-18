"""The `Format` class for defining how to structure an LLM response."""

from dataclasses import dataclass
from typing import Any, Generic, Literal, Protocol, runtime_checkable

from typing_extensions import TypeVar

from ..types import CovariantT

FormatT = TypeVar("FormatT", bound=object | None, default=None)
"""Type variable for structured response format types.

This TypeVar represents the type of structured output format that LLM responses
can be parsed into, such as Pydantic models, dataclasses, or custom classes.
It can be None for unstructured responses and defaults to None when no specific
format is required.
"""


class JsonParserFn(Protocol[CovariantT]):
    """Protocol for a JSON mode response format parser."""

    def __call__(self, json: dict[str, Any]) -> CovariantT:
        """Parse a JSON response into an instance of the class.

        Args:
            json: The JSON response from the LLM.

        Returns:
            An instance of the class `FormatCovariantT`.
        """
        ...


class ToolParserFn(Protocol[CovariantT]):
    """Protocol for a tool mode response format parser."""

    def __call__(self, args: dict[str, Any]) -> CovariantT:
        """Parse a tool call response into an instance of the class.

        Args:
            args: The arguments generated for the tool call.

        Returns:
            An instance of the class `FormatCovariantT`.
        """
        ...


class TextParserFn(Protocol[CovariantT]):
    """Protocol for a text mode response format parser."""

    def __call__(self, text: str) -> CovariantT:
        """Parse a text response into an instance of the class.

        Args:
            text: The text response from the LLM.

        Returns:
            An instance of the class `FormatCovariantT`.
        """
        ...


@dataclass
class Format(Generic[FormatT]):
    """Class representing a structured output format for LLM responses.

    A Format defines how LLM responses should be structured and parsed.
    It includes metadata about the format mode, whether to use strict validation,
    and the schema for the expected output.

    This class is not instantiated directly but is created by applying the
    `@format()` decorator to a class definition.

    When decorated with `@format()`, the class retains its original
    fields and constructor, while adding the Format functionality:

    Example:
        ```python
        from mirascope import llm

        @llm.format()
        class Book:
            title: str
            author: str

        @llm.call("openai:gpt-4o", format=Book)
        def recommend_book(genre: str) -> list[llm.Message]:
            return [
                llm.messages.system("You are a helpful assistant."),
                llm.messages.user(f"Recommend a {genre} book.")
            ]

        response: llm.Response[None, Book] = recommend_book("fantasy")
        book: Book = response.format()
        print(f"{book.title} by {book.author}")
        ```
    """

    schema: dict[str, Any]
    """The original class definition before being decorated."""

    parser: JsonParserFn[FormatT] | ToolParserFn[FormatT] | TextParserFn[FormatT]
    """The parser for formatting the response."""

    mode: Literal["json", "tool", "text"]
    """The mode of the response format, determined from the parser's signature."""

    formatting_instructions: str
    """Response formatting instructions, pulled from the parser's docstring."""

    strict: bool
    """Whether the response format should use strict validation when supported."""


@runtime_checkable
class Formattable(Protocol[FormatT]):
    """Protocol for classes that have been decorated with `@format()`."""

    __response_format__: Format[FormatT]
    """The `Format` instance constructed by the `@format()` decorator."""
