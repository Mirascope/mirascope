"""The `OpenAIStream` class for convenience around streaming LLM calls."""

from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCallParam,
    ChatCompletionUserMessageParam,
)

from ..base._stream import BaseStream
from ._utils import calculate_cost
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
