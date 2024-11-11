"""usage docs: learn/calls.md#provider-specific-parameters"""

from __future__ import annotations

from collections.abc import Sequence

from cohere.types import (
    ChatConnector,
    ChatDocument,
    ChatMessage,
    ChatRequestPromptTruncation,
    ToolResult,
)
from typing_extensions import NotRequired

from ..base import BaseCallParams
from ..base.call_params import CommonCallParams, convert_params, convert_stop_to_list


class CohereCallParams(BaseCallParams):
    """The parameters to use when calling the Cohere API.

    [Cohere API Reference](https://docs.cohere.com/reference/chat)

    Attributes:
        chat_history: ...
        connectors: ...
        conversation_id: ...
        documents: ...
        frequency_penalty: ...
        k: ...
        max_input_tokens: ...
        max_tokens: ...
        p: ...
        preamble: ...
        presence_penalty: ...
        prompt_truncation: ...
        raw_prompting: ...
        search_queries_only: ...
        seed: ...
        stop_sequences: ...
        temperature: ...
        tool_results: ...
    """

    chat_history: NotRequired[Sequence[ChatMessage] | None]
    connectors: NotRequired[Sequence[ChatConnector] | None]
    conversation_id: NotRequired[str | None]
    documents: NotRequired[Sequence[ChatDocument] | None]
    frequency_penalty: NotRequired[float | None]
    k: NotRequired[int | None]
    max_input_tokens: NotRequired[int | None]
    max_tokens: NotRequired[int | None]
    p: NotRequired[float | None]
    preamble: NotRequired[str | None]
    presence_penalty: NotRequired[float | None]
    prompt_truncation: NotRequired[ChatRequestPromptTruncation | None]
    raw_prompting: NotRequired[bool | None]
    search_queries_only: NotRequired[bool | None]
    seed: NotRequired[int | None]
    stop_sequences: NotRequired[Sequence[str] | None]
    temperature: NotRequired[float | None]
    tool_results: NotRequired[Sequence[ToolResult] | None]


def get_cohere_call_params_from_common(params: CommonCallParams) -> CohereCallParams:
    """Converts common call parameters to Cohere-specific call parameters."""
    mapping = {
        "temperature": "temperature",
        "max_tokens": "max_tokens",
        "top_p": "p",
        "frequency_penalty": "frequency_penalty",
        "presence_penalty": "presence_penalty",
        "seed": "seed",
        "stop": "stop_sequences",
    }
    transforms = [
        ("stop", convert_stop_to_list),
    ]
    return convert_params(params, mapping, CohereCallParams, transforms)
