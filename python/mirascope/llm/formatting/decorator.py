"""The `llm.format` decorator for defining response formats as classes."""

import inspect
from dataclasses import dataclass
from typing import cast, overload

from .types import (
    FormatInfo,
    FormatT,
    Formattable,
    FormattingMode,
    RequiredFormatT,
)


@dataclass(kw_only=True)
class FormatDecorator:
    """Decorator that makes a `BaseModel` into a `Formattable` (and returns the `BaseModel`)."""

    mode: FormattingMode
    """The `FormattingMode` of the `Formattable`s created by this decorator."""

    def __call__(self, __cls: type[RequiredFormatT]) -> type[RequiredFormatT]:
        """Convert a `BaseModel` into a `Formattable` and return the `BaseModel`."""

        description = None
        if __cls.__doc__:
            description = inspect.cleandoc(__cls.__doc__)

        cast(Formattable, __cls).__mirascope_format_info__ = FormatInfo(
            name=__cls.__name__,
            description=description,
            schema=__cls.model_json_schema(),
            mode=self.mode,
            format=__cls,
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
    the ability to be parsed from LLM responses through the `__mirascope_format_info__: Format`
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

    The decorated BaseModel may provide custom formatting instructions via a
    `formatting_instructions(cls)` classmethod. If that method is present, it will be called,
    and the resulting instructions will automatically be appended to the system prompt.

    If no formatting instructions are present, then Mirascope may auto-generate instructions
    based on the active format mode. To disable this behavior and all prompt modification,
    you can add the `formatting_instructions` classmethod and have it return `None`.

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
