"""The `LiteLLMStream` class for convenience around streaming LLM calls."""

from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionUserMessageParam,
)

from ..base._stream import BaseStream
from ._utils import calculate_cost
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

    @property
    def cost(self) -> float | None:
        """Returns the cost of the call."""
        return calculate_cost(self.input_tokens, self.output_tokens, self.model)

    def _construct_message_param(
        self, tool_calls: list | None = None, content: str | None = None
    ) -> ChatCompletionAssistantMessageParam:
        message_param = ChatCompletionAssistantMessageParam(
            role="assistant",
            content=content,
        )
        if tool_calls:
            message_param["tool_calls"] = tool_calls
        return message_param
