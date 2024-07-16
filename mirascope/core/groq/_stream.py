"""The `GroqStream` class for convenience around streaming LLM calls."""

from groq.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionUserMessageParam,
)

from ..base._stream import BaseStream
from .call_params import GroqCallParams
from .call_response import GroqCallResponse
from .call_response_chunk import GroqCallResponseChunk
from .dynamic_config import GroqDynamicConfig
from .tool import GroqTool


class GroqStream(
    BaseStream[
        GroqCallResponse,
        GroqCallResponseChunk,
        ChatCompletionUserMessageParam,
        ChatCompletionAssistantMessageParam,
        ChatCompletionMessageParam,
        GroqTool,
        GroqDynamicConfig,
        GroqCallParams,
    ]
):
    _provider = "groq"

    def _construct_message_param(
        self, tool_calls: list | None = None, content: str | None = None
    ) -> ChatCompletionAssistantMessageParam:
        return ChatCompletionAssistantMessageParam(
            role="assistant",
            content=content,
            tool_calls=tool_calls,
        )
