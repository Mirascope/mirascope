"""Type for the formatting module."""

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable
from typing_extensions import TypeAliasType, TypeVar

from pydantic import BaseModel

from .primitives import PrimitiveType

if TYPE_CHECKING:
    from .format import Format
    from .output_parser import OutputParser

FormattableT = TypeVar(
    "FormattableT", bound=BaseModel | PrimitiveType | None, default=None
)

FormatSpec = TypeAliasType(
    "FormatSpec",
    "type[FormattableT] | Format[FormattableT] | OutputParser[FormattableT]",
    type_params=(FormattableT,),
)
"""Type alias for format parameter types.

A FormatSpec can be:
- A type (class) that represents the format schema (e.g., a Pydantic BaseModel)
- A Format wrapper that includes mode and other metadata
- An OutputParser for custom parsing logic
"""
"""Type variable for structured response format types.

This TypeVar represents the type of structured output format that LLM responses
can be parsed into, or None if no format is specified.

Supported format types:
- Pydantic BaseModel subclasses
- Primitive types: str, int, float, bool, bytes, list, set, tuple, dict
- Generic collections: list[Book], dict[str, int], etc.
- Union, Literal, and Annotated types
- Enum types
"""


FormattingMode = Literal[
    "strict",
    "json",
    "tool",
    "parser",
]
"""Available modes for response format generation.

- "strict": Use strict mode for structured outputs, asking the LLM to strictly adhere
    to a given JSON schema. Not all providers or models support it, and may not be
    compatible with tool calling. When making a call using this mode, an
    `llm.FeatureNotSupportedError` error may be raised if the mode is unsupported.

- "json": Use JSON mode for structured outputs. In contrast to strict mode, we ask the
    LLM to output JSON as text, though without guarantees that the model will output
    the expected format schema. If the provider has explicit JSON mode, it will be used;
    otherwise, Mirascope will modify the system prompt to request JSON output. May
    raise an `llm.FeatureNotSupportedError` if tools are present and the
    model does not support tool calling when using JSON mode.

- "tool": Use forced tool calling to structure outputs. Mirascope will construct an
    ad-hoc tool with the required json schema as tool args. When the LLM chooses that
    tool, it will automatically be converted from a `ToolCall` into regular response
    content (abstracting over the tool call). If other tools are present, they will
    be handled as regular tool calls.

- "parser": Use custom parsing with formatting instructions. No schema generation or
    structured output features. The LLM receives only formatting instructions and the
    response is parsed using a custom parser function created with `@llm.output_parser`.

Note: When `llm.format` is not used, the provider will automatically choose a mode at call time.
"""


@runtime_checkable
class HasFormattingInstructions(Protocol):
    """Protocol for classes that have been decorated with `@format()`."""

    @classmethod
    def formatting_instructions(cls) -> str | None: ...
