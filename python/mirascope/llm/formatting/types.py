"""The `Format` class for defining how to structure an LLM response."""

from dataclasses import dataclass
from typing import Literal, Protocol, runtime_checkable
from typing_extensions import TypeVar

from pydantic import BaseModel

FormatT = TypeVar("FormatT", bound=BaseModel | None, default=None)
"""Type variable for structured response format types.

This TypeVar represents the type of structured output format that LLM responses
can be parsed into, or None if no format is specified. 
If format is specified, it must extend Pydantic BaseModel. 
"""

RequiredFormatT = TypeVar("RequiredFormatT", bound=BaseModel)
"""Type variable for mandatory structured response format types.

This TypeVar represents the type of structured output format that LLM responses
can be parsed into. It must extend Pydantic BaseModel.
"""

FormattingMode = Literal[
    "strict",
    "json",
    "tool",
    "strict-or-tool",
    "strict-or-json",
]
"""Available modes for response format generation.

- "strict": Use strict mode for structured outputs, asking the LLM to strictly adhere
    to a given JSON schema. Not compatible with tool calling, and only available
    for some providers. Will throw a runtime error if it cannot be used.

- "json": Use JSON mode for structured outputs. The LLM will respond with valid JSON.
    If the provider does not support an explicit JSON mode, then the prompt
    will be modified to request JSON output.

- "tool": Use forced tool calling to structure outputs. Mirascope will construct an
    ad-hoc tool with the required json schema as tool args. When the LLM chooses that
    tool, it will automatically be converted from a ToolCall into regular response
    content (abstracting over the tool call). If other tools are present, they will
    be handled as regular tool calls.

- "strict-or-tool": Use "strict" mode if supported, or fall back to "tool" mode if not. 
    Will log an info message on fallback.

- "strict-or-json": Use "strict" mode if supported, or fall back to "json" mode if not.
    Will log an info message on fallback.
"""


@dataclass(kw_only=True)
class FormatInfo:
    """Class representing a structured output format for LLM responses.

    A `FormatInfo` defines how LLM responses should be structured and parsed.
    It includes metadata about the format mode, whether to use strict validation,
    and the schema for the expected output.

    This class is not instantiated directly but is created by applying the
    `@format()` decorator to a class definition.

    When decorated with `@format()`, the class retains its original
    fields and constructor, while adding the `FormatInfo`:

    Example:
      ```python
      from mirascope import llm

      @llm.format()
      class Book:
          title: str
          author: str

      @llm.call(
          provider="openai",
          model_id="gpt-4o-mini",
          format=Book,
      )
      def recommend_book(genre: str) -> list[llm.Message]:
          return [
              llm.messages.system("You are a helpful assistant."),
              llm.messages.user(f"Recommend a {genre} book.")
          ]

      response: llm.Response[Book] = recommend_book("fantasy")
      book: Book = response.format()
      print(f"{book.title} by {book.author}")
    ```
    """

    name: str
    """The name of the response format."""

    description: str | None
    """A description of the response format, if available."""

    schema: dict[str, object]
    """JSON schema representation of the structured output format."""

    mode: FormattingMode
    """The mode of the response format. 
    
    Determines how the LLM call may be modified in order to extract the expected format.
    """

    format: type[BaseModel]
    """The associated format that this `FormatInfo` describes."""


ConcreteFormattingMode = Literal[
    "strict",
    "tool",
    "json",
]
"""Concrete mode for formatting responses with a particular LLM.

The semantics for modes "strict", "tool", and "json" are as described in `FormattingMode`. 

"strict-or-tool" and "strict-or-json" are not present because they will have resolved to one of "strict", "tool", or "json".
"""


@dataclass(kw_only=True)
class ResolvedFormatInfo:
    """Resolved format info for direct processing by LLM.

    A `FormatInfo` is converted into a `ResolvedFormatInfo` using
    `ResolvedFormatInfo.from_format_info(...)`. Based on information about the model's capabilities,
    it will include a concrete formatting mode. It may also contain formatting instructions
    that will be added to the model's system message. Those formatting instructions will be
    the `FormatInfo`'s system instructions if present, or may be auto-generated instructions
    (e.g. a dump of the expected JSON schema in JSON mode) if no custom formatting instructions
    were provided.
    """

    mode: ConcreteFormattingMode
    """The concrete formatting mode that will be used."""

    info: FormatInfo
    """The FormatInfo this ResolvedFormatInfo was resolved from."""

    formatting_instructions: str | None
    """The formatting instructions that will be added to the LLM system prompt.
    
    These are computed based on the `FormattingInstructions` present on the `FormatInfo`.
    """


@runtime_checkable
class Formattable(Protocol):
    """Protocol for classes that have been decorated with `@format()`."""

    __mirascope_format_info__: FormatInfo
    """The `FormatInfo` instance added by the `@format()` decorator."""


@runtime_checkable
class HasFormattingInstructions(Protocol):
    """Protocol for classes that have been decorated with `@format()`."""

    @classmethod
    def formatting_instructions(cls) -> str | None: ...
