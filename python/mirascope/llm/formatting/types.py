"""The `Format` class for defining how to structure an LLM response."""

from dataclasses import dataclass
from typing import Any, Generic, Literal, Protocol, runtime_checkable

from pydantic import BaseModel
from typing_extensions import TypeVar

from ..responses import Response
from ..types import CovariantT, P

FormatT = TypeVar("FormatT", bound=BaseModel | None, default=None)
"""Type variable for structured response format types.

This TypeVar represents the type of structured output format that LLM responses
can be parsed into, such as Pydantic models, dataclasses, or custom classes.
It can be None for unstructured responses and defaults to None when no specific
format is required.
"""

FormattingMode = Literal[
    "strict", "json", "tool", "strict-or-tool", "strict-or-json", "parse"
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
    Will log a warning on fallback.

- "strict-or-json": Use "strict" mode if supported, or fall back to "json" mode if not.
    Will log a warning on fallback.

- "parse": Use a `parse` classmethod on the FormatT, which will expect an `llm.Response`
    as input, and produce the formatted object.
"""


class ResponseParseable(Protocol[P, CovariantT]):
    """Protocol for defining a class with a custom parse classmethod."""

    @classmethod
    def parse(cls, response: Response, *args: P.args, **kwargs: P.kwargs) -> CovariantT:
        """Parse an LLM response into an instance of the class.

        Args:
          response: the LLM response.
          kwargs: Extra kwargs may be provided if specified via llm.formatting.FromCallArgs.
            If so, the extra args will match the call args that were marked FromCallArgs.

        Returns:
            An instance of the class.
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

      response: llm.Response[Book] = recommend_book("fantasy")
      book: Book = response.format()
      print(f"{book.title} by {book.author}")
    ```
    """

    schema: dict[str, Any]
    """JSON schema representation of the structured output format."""

    mode: FormattingMode
    """The mode of the response format. 
    
    Determines how the LLM call may be modified in order to extract the expected format.
    """

    formatting_instructions: str | None
    """Format instructions. Will be appended to the prompt if present.
    
    May be provided as an argument to the llm.format decorator, or pulled from a
    formatting_instructions class method.
    """


@runtime_checkable
class Formattable(Protocol[FormatT]):
    """Protocol for classes that have been decorated with `@format()`."""

    __response_format__: Format[FormatT]
    """The `Format` instance constructed by the `@format()` decorator."""
