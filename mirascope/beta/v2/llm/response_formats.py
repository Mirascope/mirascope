# """Response format interface for LLM structured outputs.

# This module provides a way to define structured output formats for LLM responses.
# The `@response_format()` decorator can be applied to classes to specify how LLM
# outputs should be structured and parsed.
# """

from __future__ import annotations

from collections.abc import Callable
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


class TextFormatDef(Protocol[CovariantT]):
    """Protocol for defining a response format."""

    # def __call__(
    #     self,
    #     *args: P.args,
    #     **kwargs: P.kwargs,
    # ) -> CovariantT: ...

    @classmethod
    def parse(cls, text: str) -> CovariantT:
        """Parse a text response into an instance of the class.

        Args:
            text: The text response from the LLM.

        Returns:
            An instance of the class.
        """
        raise NotImplementedError()


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

        @llm.generation(response_format=Book)
        def recommend_book(genre: str) -> list[llm.Message]:
            return [
                llm.system("You are a helpful assistant."),
                llm.user(f"Recommend a {genre} book.")
            ]

        with llm.model("openai:gpt-4o"):
            response: llm.Response[Book] = recommend_book("fantasy")
            book: Book = response.format()
            print(f"{book.title} by {book.author}")
        ```
    """

    original: type[T]
    """The original class definition before being decorated."""

    schema: dict[str, Any]
    """The original class definition before being decorated."""

    mode: Literal["json", "tool", "text"]
    """The mode that determines how the response should be formatted and parsed."""

    strict: bool
    """Whether the response format should use strict validation when supported."""

    @classmethod
    def parse(cls, text: str) -> T:
        """Parse a text response into an instance of the class.

        For "json" and "tool" modes, this method has a default implementation.
        For "text" mode, this method must be implemented by the decorated class.

        Args:
            text: The text response from the LLM.

        Returns:
            An instance of the class.
        """
        raise NotImplementedError()


@overload
def response_format(
    *,
    mode: Literal["text"],
    strict: bool = False,
) -> Callable[[type[TextFormatDef[T]]], type[ResponseFormat[T]]]:
    """Overload for "text" mode, which requires a parse method."""
    ...


@overload
def response_format(
    *,
    mode: Literal["json", "tool"] = "json",
    strict: bool = False,
) -> Callable[[type[T]], type[ResponseFormat[T]]]:
    """Overload for "json" and "tool" modes, which use default parsers."""
    ...


def response_format(
    *,
    mode: Literal["json", "tool", "text"] = "json",
    strict: bool = False,
) -> (
    Callable[[type[T]], type[ResponseFormat[T]]]
    | Callable[[type[TextFormatDef[T]]], type[ResponseFormat[T]]]
):
    """Decorator that defines a structured response format for LLM outputs.

    This decorator can be applied to a class to define how LLM responses should be
    structured and parsed. The decorated class becomes a ResponseFormat that can be
    used with `llm.generation` to specify the expected response structure.

    Args:
        mode: The mode to use for structuring outputs:
            - "json" (default): Use JSON mode for structured outputs
            - "tool": Use forced tool calling to structure outputs
            - "text": Return a text string that will be parsed with parse()
        strict: Whether to use strict validation when supported by the model.
            Default is False.

    Returns:
        A decorator function that converts the class into a ResponseFormat.

    Example:

        ```python
        from mirascope import llm
        from typing import Any

        # JSON mode (default)
        @llm.response_format()
        class Book:
            title: str
            author: str

        # Tool mode with strict validation
        @llm.response_format(mode="tool", strict=True)
        class Weather:
            temperature: float
            conditions: str

        # Text mode with custom parsing
        @llm.response_format(mode="text")
        class MovieRecommendation:
            title: str
            director: str

            @classmethod
            def parse(cls, text: str) -> "MovieRecommendation":
                lines = text.strip().split("\\n")
                return cls(
                    title=lines[0].replace("Title: ", ""),
                    director=lines[1].replace("Director: ", "")
                )

        # Usage with a generation
        @llm.generation(response_format=Book)
        def recommend_book(genre: str) -> list[llm.Message]:
            return [
                llm.system("You are a helpful assistant."),
                llm.user(f"Recommend a {genre} book.")
            ]

        # The response can be formatted as a Book instance
        response = recommend_book("fantasy")
        book = response.format()  # Returns a Book instance
        print(f"{book.title} by {book.author}")
        ```
    """
    raise NotImplementedError()
