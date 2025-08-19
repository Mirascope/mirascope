"""The `llm.format` decorator for defining response formats as classes."""

import inspect
from dataclasses import dataclass
from typing import cast, overload

from .types import (
    Format,
    FormatT,
    Formattable,
    FormattingMode,
    HasFormattingInstructions,
    RequiredFormatT,
)


@dataclass(kw_only=True)
class FormatDecorator:
    """Decorator that makes a `BaseModel` into a `Formattable` (and returns the `BaseModel`)."""

    mode: FormattingMode
    """The `FormattingMode` of the `Formattable`s created by this decorator."""

    def __call__(self, __cls: type[RequiredFormatT]) -> type[RequiredFormatT]:
        """Convert a `BaseModel` into a `Formattable` and return the `BaseModel`."""
        formatting_instructions = None
        if isinstance(__cls, HasFormattingInstructions):
            formatting_instructions = inspect.cleandoc(__cls.formatting_instructions())

        description = None
        if __cls.__doc__:
            description = inspect.cleandoc(__cls.__doc__)

        cast(Formattable, __cls).__response_format__ = Format(
            name=__cls.__name__,
            description=description,
            schema=__cls.model_json_schema(),
            mode=self.mode,
            formatting_instructions=formatting_instructions,
        )

        return __cls


@overload
def format(
    __cls: type[FormatT],
    /,
    mode: FormattingMode | None = None,
) -> type[FormatT]:
    """Overload to convert a class into a Formattable."""
    ...


@overload
def format(
    *,
    mode: FormattingMode | None = None,
) -> FormatDecorator:
    """Overload to create a FormatDecorator."""
    ...


def format(
    __cls: type[FormatT] | None = None,
    /,
    mode: FormattingMode | None = None,
) -> type[FormatT] | FormatDecorator:
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

        @llm.call(
            provider="openai",
            model="gpt-4o-mini",
            format=Book,
        )
        def recommend_book(genre: str):
          return f"Recommend a {genre} book."

      response = recommend_book("fantasy")
      book: Book = response.format()
      print(f"{book.title} by {book.author}")
      ```
    """
    decorator = FormatDecorator(mode=mode or "strict-or-tool")
    if __cls is None or __cls is type(None):
        return decorator
    return decorator(__cls)
