"""The `GeminiStream` class for convenience around streaming LLM calls."""

from google.ai.generativelanguage import FunctionCall
from google.generativeai.types import ContentDict

from ..base._stream import BaseStream
from ._utils import calculate_cost
from .call_params import GeminiCallParams
from .call_response import GeminiCallResponse
from .call_response_chunk import GeminiCallResponseChunk
from .dynamic_config import GeminiDynamicConfig
from .tool import GeminiTool


class GeminiStream(
    BaseStream[
        GeminiCallResponse,
        GeminiCallResponseChunk,
        ContentDict,
        ContentDict,
        ContentDict,
        ContentDict,
        GeminiTool,
        GeminiDynamicConfig,
        GeminiCallParams,
    ]
):
    _provider = "gemini"

    @property
    def cost(self) -> float | None:
        """Returns the cost of the call."""
        return calculate_cost(self.input_tokens, self.output_tokens, self.model)

    def _construct_message_param(
        self, tool_calls: list[FunctionCall] | None = None, content: str | None = None
    ) -> ContentDict:
        return {
            "role": "model",
            "parts": [{"type": "text", "text": content}] + (tool_calls or []),
        }
