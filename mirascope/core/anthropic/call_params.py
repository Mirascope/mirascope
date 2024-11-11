"""usage docs: learn/calls.md#provider-specific-parameters"""

from __future__ import annotations

from collections.abc import Iterable

from anthropic.types import TextBlockParam
from anthropic.types.completion_create_params import Metadata
from anthropic.types.message_create_params import ToolChoice
from httpx import Timeout
from typing_extensions import NotRequired, Unpack

from ..base import BaseCallParams
from ..base.call_params import CommonCallParams, convert_params, convert_stop_to_list


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


def get_anthropic_call_params_from_common(
    **params: Unpack[CommonCallParams],
) -> AnthropicCallParams:
    """Converts common call parameters to Anthropic-specific call parameters."""
    mapping = {
        "temperature": "temperature",
        "max_tokens": "max_tokens",
        "top_p": "top_p",
        "stop": "stop_sequences",
    }
    transforms = [
        ("stop", convert_stop_to_list),
    ]
    return convert_params(params, mapping, AnthropicCallParams, transforms)
