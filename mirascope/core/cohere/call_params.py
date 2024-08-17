"""usage docs: learn/calls.md#provider-specific-parameters"""

from __future__ import annotations

from typing import Sequence

from cohere.types import (
    ChatConnector,
    ChatDocument,
    ChatRequestPromptTruncation,
    ToolResult,
)
from typing_extensions import NotRequired

from ..base import BaseCallParams


class CohereCallParams(BaseCallParams):
    """The parameters to use when calling the Cohere API.

    [Cohere API Reference](https://docs.cohere.com/reference/chat)

    Attributes:
        conversation_id: ...
        prompt_truncation: ...
        connectors: ...
        search_queries_only: ...
        documents: ...
        temperature: ...
        max_tokens: ...
        max_input_tokens: ...
        k: ...
        p: ...
        seed: ...
        stop_sequences: ...
        frequency_penalty: ...
        presence_penalty: ...
        raw_prompting: ...
        tool_results: ...
    """

    conversation_id: NotRequired[str | None]
    prompt_truncation: NotRequired[ChatRequestPromptTruncation | None]
    connectors: NotRequired[Sequence[ChatConnector] | None]
    search_queries_only: NotRequired[bool | None]
    documents: NotRequired[Sequence[ChatDocument] | None]
    temperature: NotRequired[float | None]
    max_tokens: NotRequired[int | None]
    max_input_tokens: NotRequired[int | None]
    k: NotRequired[int | None]
    p: NotRequired[float | None]
    seed: NotRequired[int | None]
    stop_sequences: NotRequired[Sequence[str] | None]
    frequency_penalty: NotRequired[float | None]
    presence_penalty: NotRequired[float | None]
    raw_prompting: NotRequired[bool | None]
    tool_results: NotRequired[Sequence[ToolResult] | None]
