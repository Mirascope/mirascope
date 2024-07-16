"""The `LiteLLMStream` class for convenience around streaming LLM calls."""

from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionUserMessageParam,
)

from ..base._stream import BaseStream
from .call_params import LiteLLMCallParams
from .call_response import LiteLLMCallResponse
from .call_response_chunk import LiteLLMCallResponseChunk
from .dynamic_config import LiteLLMDynamicConfig
from .tool import LiteLLMTool


class LiteLLMStream(
    BaseStream[
        LiteLLMCallResponse,
        LiteLLMCallResponseChunk,
        ChatCompletionUserMessageParam,
        ChatCompletionAssistantMessageParam,
        ChatCompletionMessageParam,
        LiteLLMTool,
        LiteLLMDynamicConfig,
        LiteLLMCallParams,
    ]
):
    _provider = "litellm"

    def _construct_message_param(
        self, tool_calls: list | None = None, content: str | None = None
    ) -> ChatCompletionAssistantMessageParam:
        return ChatCompletionAssistantMessageParam(
            role="assistant",
            content=content,
            tool_calls=tool_calls,
        )
