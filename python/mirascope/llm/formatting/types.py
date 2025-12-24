"""Type for the formatting module."""

from typing import Literal, Protocol, runtime_checkable
from typing_extensions import TypeVar

from pydantic import BaseModel

# TODO: Support primitive types (e.g. `format=list[Book]`)
FormattableT = TypeVar("FormattableT", bound=BaseModel | None, default=None)
"""Type variable for structured response format types.

This TypeVar represents the type of structured output format that LLM responses
can be parsed into, or None if no format is specified. 
If format is specified, it must extend Pydantic BaseModel. 
"""


FormattingMode = Literal[
    "strict",
    "json",
    "tool",
]
"""Available modes for response format generation.

- "strict": Use strict mode for structured outputs, asking the LLM to strictly adhere
    to a given JSON schema. Not all providers or models support it, and may not be
    compatible with tool calling. When making a call using this mode, an 
    `llm.FormattingModeNotSupportedError` error may be raised (if "strict" mode is wholly
    unsupported), or an `llm.FeatureNotSupportedError` may be raised (if trying to use 
    strict along with tools and that is unsupported).

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

Note: When `llm.format` is not used, the provider will automatically choose a mode at call time.
"""


@runtime_checkable
class HasFormattingInstructions(Protocol):
    """Protocol for classes that have been decorated with `@format()`."""

    @classmethod
    def formatting_instructions(cls) -> str | None: ...
