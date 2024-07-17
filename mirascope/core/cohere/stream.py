"""The `CohereStream` class for convenience around streaming LLM calls."""

from cohere.types import ChatMessage, ToolCall

from ..base._stream import BaseStream
from ._utils import calculate_cost
from .call_params import CohereCallParams
from .call_response import CohereCallResponse
from .call_response_chunk import CohereCallResponseChunk
from .dynamic_config import CohereDynamicConfig
from .tool import CohereTool


class CohereStream(
    BaseStream[
        CohereCallResponse,
        CohereCallResponseChunk,
        ChatMessage,
        ChatMessage,
        ChatMessage,
        CohereTool,
        CohereDynamicConfig,
        CohereCallParams,
    ]
):
    _provider = "cohere"

    @property
    def cost(self) -> float | None:
        """Returns the cost of the call."""
        return calculate_cost(self.input_tokens, self.output_tokens, self.model)

    def _construct_message_param(
        self, tool_calls: list[ToolCall] | None = None, content: str | None = None
    ) -> ChatMessage:
        return ChatMessage(
            role="assistant",  # type: ignore
            message=content if content else "",
            tool_calls=tool_calls,
        )
