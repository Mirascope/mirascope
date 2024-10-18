"""usage docs: learn/calls.md#provider-specific-parameters"""

from __future__ import annotations

from collections.abc import Iterable

from anthropic.types import TextBlockParam
from anthropic.types.completion_create_params import Metadata
from anthropic.types.message_create_params import ToolChoice
from httpx import Timeout
from typing_extensions import NotRequired

from ..base import BaseCallParams


class AnthropicCallParams(BaseCallParams):
    """The parameters to use when calling the Anthropic API.

    [Anthropic API Reference](https://docs.anthropic.com/en/api/messages)

    Attributes:
        max_tokens: ...
        tool_choice: ...
        metadata: ...
        stop_sequences: ...
        temperature: ...
        top_k: ...
        top_p: ...
        timeout: ...
    """

    extra_headers: NotRequired[dict[str, str] | None]
    max_tokens: int
    tool_choice: NotRequired[ToolChoice | None]
    metadata: NotRequired[Metadata | None]
    stop_sequences: NotRequired[list[str] | None]
    system: NotRequired[str | Iterable[TextBlockParam] | None]
    temperature: NotRequired[float | None]
    top_k: NotRequired[int | None]
    top_p: NotRequired[float | None]
    timeout: NotRequired[float | Timeout | None]
