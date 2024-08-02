"""The `MistralStream` class for convenience around streaming LLM calls."""

from mistralai.models.chat_completion import ChatMessage

from ..base._stream import BaseStream
from ._utils import calculate_cost
from .call_params import MistralCallParams
from .call_response import MistralCallResponse
from .call_response_chunk import MistralCallResponseChunk
from .dynamic_config import MistralDynamicConfig
from .tool import MistralTool


class MistralStream(
    BaseStream[
        MistralCallResponse,
        MistralCallResponseChunk,
        ChatMessage,
        ChatMessage,
        ChatMessage,
        ChatMessage,
        MistralTool,
        MistralDynamicConfig,
        MistralCallParams,
    ]
):
    _provider = "mistral"

    @property
    def cost(self) -> float | None:
        """Returns the cost of the call."""
        return calculate_cost(self.input_tokens, self.output_tokens, self.model)

    def _construct_message_param(
        self, tool_calls: list | None = None, content: str | None = None
    ) -> ChatMessage:
        message_param = ChatMessage(
            role="assistant", content=content if content else "", tool_calls=tool_calls
        )
        return message_param
