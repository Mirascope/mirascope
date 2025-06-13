"""The `ResponseFormat` class for defining how to structure an LLM response."""

from dataclasses import dataclass
from typing import Any, Generic, Literal, Protocol, TypeVar

from ..types import Dataclass

T = TypeVar("T", bound=Dataclass)
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
