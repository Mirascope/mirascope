"""The `llm.format` decorator for defining response formats as classes."""

import inspect

from ..types import NoneType
from ._utils import default_formatting_instructions
from .types import Format, FormattableT, FormattingMode, HasFormattingInstructions


def format(
    formattable: type[FormattableT] | None,
    *,
    mode: FormattingMode,
) -> Format[FormattableT] | None:
    """Returns a `Format` that describes structured output for a Formattable type.

    This function converts a Formattable type (e.g. Pydantic BaseModel) into a `Format`
    object that describes how the object should be formatted. Calling `llm.format`
    is optional, as all the APIs that expect a `Format` can also take the Formattable
    type directly. However, calling `llm.format` is necessary in order to specify the
    formatting mode that will be used.

    Args:
        mode: The format mode to use, one of the following:
            - "strict": Use model strict structured outputs, or fail if unavailable.
            - "tool": Use forced tool calling with a special tool that represents a
              formatted response.
            - "json": Use provider json mode if available, or modify prompt to request
              json if not.

    The Formattable type may provide custom formatting instructions via a
    `formatting_instructions(cls)` classmethod. If that method is present, it will be called,
    and the resulting instructions will automatically be appended to the system prompt.

    If no formatting instructions are present, then Mirascope may auto-generate instructions
    based on the active format mode. To disable this behavior and all prompt modification,
    you can add the `formatting_instructions` classmethod and have it return `None`.

    Returns:
      A `Format` object describing the Formattable type.

    Example:
      Using with an LLM call:

      ```python
      from pydantic import BaseModel

      from mirascope import llm


      class Book(BaseModel):
          title: str
          author: str

      format = llm.format(Book, mode="strict")

      @llm.call(
          provider_id="openai",
          model_id="openai/gpt-5-mini",
          format=format,
      )
      def recommend_book(genre: str):
          return f"Recommend a {genre} book."

      response = recommend_book("fantasy")
      book: Book = response.parse()
      print(f"{book.title} by {book.author}")
      ```
    """
    # TODO: Add caching or memoization to this function (e.g. functools.lru_cache)

    if formattable is None or formattable is NoneType:
        return None

    description = None
    if formattable.__doc__:
        description = inspect.cleandoc(formattable.__doc__)

    schema = formattable.model_json_schema()
    formatting_instructions = None
    if isinstance(formattable, HasFormattingInstructions):
        formatting_instructions = formattable.formatting_instructions()
    else:
        formatting_instructions = default_formatting_instructions(schema, mode)

    return Format[FormattableT](
        name=formattable.__name__,
        description=description,
        schema=schema,
        mode=mode,
        formatting_instructions=formatting_instructions,
        formattable=formattable,
    )


def resolve_format(
    formattable: type[FormattableT] | Format[FormattableT] | None,
    default_mode: FormattingMode,
) -> Format[FormattableT] | None:
    """Resolve a `Format` (or None) from a possible `Format` or Formattable."""
    if isinstance(formattable, Format):
        return formattable
    else:
        return format(formattable, mode=default_mode)
