"""The `OpenAIStream` class for convenience around streaming LLM calls."""

from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionUserMessageParam,
)

from ..base._stream import BaseStream
from .call_params import OpenAICallParams
from .call_response import OpenAICallResponse
from .call_response_chunk import OpenAICallResponseChunk
from .dynamic_config import OpenAIDynamicConfig
from .tool import OpenAITool


class OpenAIStream(
    BaseStream[
        OpenAICallResponse,
        OpenAICallResponseChunk,
        ChatCompletionUserMessageParam,
        ChatCompletionAssistantMessageParam,
        ChatCompletionMessageParam,
        OpenAITool,
        OpenAIDynamicConfig,
        OpenAICallParams,
    ]
):
    _provider = "openai"

    def _construct_message_param(
        self, tool_calls: list | None = None, content: str | None = None
    ) -> ChatCompletionAssistantMessageParam:
        return ChatCompletionAssistantMessageParam(
            role="assistant",
            content=content,
            tool_calls=tool_calls,
        )
