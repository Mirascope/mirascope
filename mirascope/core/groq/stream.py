"""The `GroqStream` class for convenience around streaming LLM calls."""

from groq.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCallParam,
    ChatCompletionUserMessageParam,
)

from ..base._stream import BaseStream
from ._utils import calculate_cost
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

    @property
    def cost(self) -> float | None:
        """Returns the cost of the call."""
        return calculate_cost(self.input_tokens, self.output_tokens, self.model)

    def _construct_message_param(
        self,
        tool_calls: list[ChatCompletionMessageToolCallParam] | None = None,
        content: str | None = None,
    ) -> ChatCompletionAssistantMessageParam:
        message_param = ChatCompletionAssistantMessageParam(
            role="assistant",
            content=content,
        )
        if tool_calls:
            message_param["tool_calls"] = tool_calls
        return message_param
