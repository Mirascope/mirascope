"""The `llm.format` decorator for defining response formats as classes."""

from collections.abc import Callable
from typing import Literal, TypeAlias, overload

from ..types import P
from .types import FormatT, FormattingMode, ResponseParseable

# Type aliases for decorator return types
ParseableDecorator: TypeAlias = Callable[
    [type[ResponseParseable[P, FormatT]]], type[FormatT]
]
FormatDecorator: TypeAlias = Callable[[type[FormatT]], type[FormatT]]


# Decorator for cases where the class is a ResponseParseable. In this case, if mode
# is unspecified, we default to "parse" to use the custom parser the user provided.
@overload
def format(
    __cls: type[ResponseParseable[P, FormatT]],
    /,
    mode: Literal[
        "strict", "json", "tool", "strict-or-tool", "strict-or-json", "parse"
    ] = "parse",
) -> type[FormatT]:
    """Overload for ResponseParseable classes, where mode defaults to parse."""
    ...


# For general FormatT classes, we will use the "strict-or-tool" parser if unspecified.
@overload
def format(
    __cls: type[FormatT],
    /,
    mode: Literal[
        "strict", "json", "tool", "strict-or-tool", "strict-or-json"
    ] = "strict-or-tool",
) -> type[FormatT]:
    """Overload for regular classes with auto-generated parsers."""
    ...


# Decorator factory for parse mode (ResponseParseable classes)
@overload
def format(
    *,
    mode: Literal["parse"],
) -> ParseableDecorator[P, FormatT]:
    """Overload for decorator factory with parse mode."""
    ...


# Decorator factory for auto-generated modes (regular FormatT classes)
@overload
def format(
    *,
    mode: Literal["strict", "json", "tool", "strict-or-tool", "strict-or-json"],
) -> FormatDecorator[FormatT]:
    """Overload for decorator factory with auto-generated parsers."""
    ...


def format(
    __cls=None,
    /,
    mode: FormattingMode | None = None,
) -> ParseableDecorator[P, FormatT] | type[FormatT] | FormatDecorator[FormatT]:
    """Decorator that defines a structured response format for LLM outputs.

    This decorator converts a class into a structured output format that can be used
    with LLM calls. The original class retains its behavior and typing, while gaining
    the ability to be parsed from LLM responses through the `__response_format__: Format`
    attribute added to the class. The class must inherit from Pydantic BaseModel.

    Args:
      mode: The format mode to use, one of the following:
        - "strict": Use model strict structured outputs, or fail if unavailable.
        - "tool": Use forced tool calling with a special tool that represents a
            formatted response.
        - "json": Use provider json mode if available, or modify prompt to request
            json if not.
        - "strict-or-tool": Use strict mode if available, tool mode if not.
        - "strict-or-json": Use strict mode if available, json mode if not.
        - "parse": Use a custom parse classmethod which takes an llm.Response
            (for full control).

        Note that custom formatting instructions will be auto-appended to the prompt if
          a `formatting_instructions` classmethod is present on the class being decorated.

    Returns:
      Either the decorated class (direct decoration) or a decorator function
      (factory usage).

    Example:
      Using with an LLM call:

      ```python
      from pydantic import BaseModel

      from mirascope import llm


      @llm.format()
      class Book(BaseModel):
          title: str
          author: str

      @llm.call("openai:gpt-4o", format=Book)
      def recommend_book(genre: str):
          return f"Recommend a {genre} book."

      response = recommend_book("fantasy")
      book: Book = response.format()
      print(f"{book.title} by {book.author}")
      ```
    """
    raise NotImplementedError()
