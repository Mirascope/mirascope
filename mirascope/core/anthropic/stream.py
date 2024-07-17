"""The `AnthropicStream` class for convenience around streaming LLM calls."""

from anthropic.types import MessageParam, TextBlock, ToolUseBlock

from ..base._stream import BaseStream
from ._utils import calculate_cost
from .call_params import AnthropicCallParams
from .call_response import AnthropicCallResponse
from .call_response_chunk import AnthropicCallResponseChunk
from .dynamic_config import AnthropicDynamicConfig
from .tool import AnthropicTool


class AnthropicStream(
    BaseStream[
        AnthropicCallResponse,
        AnthropicCallResponseChunk,
        MessageParam,
        MessageParam,
        MessageParam,
        AnthropicTool,
        AnthropicDynamicConfig,
        AnthropicCallParams,
    ]
):
    _provider = "anthropic"

    @property
    def cost(self) -> float | None:
        """Returns the cost of the call."""
        return calculate_cost(self.input_tokens, self.output_tokens, self.model)

    def _construct_message_param(
        self, tool_calls: list[ToolUseBlock] | None = None, content: str | None = None
    ) -> MessageParam:
        """Returns the tool message parameters for tool call results."""
        return {
            "role": "assistant",
            "content": ([TextBlock(text=content, type="text")] if content else [])
            + (tool_calls or []),
        }
