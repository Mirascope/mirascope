"""The `AnthropicStream` class for convenience around streaming LLM calls."""

from anthropic.types import MessageParam

from ..base._stream import BaseStream
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

    def construct_message_param(
        self, tool_calls: list | None = None, content: str | None = None
    ) -> MessageParam:
        """Returns the tool message parameters for tool call results."""
        return {
            "role": "assistant",
            "content": [{"type": "text", "text": content}] + tool_calls,
        }
