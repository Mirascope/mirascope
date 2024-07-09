"""The `GeminiStream` class for convenience around streaming LLM calls."""

from google.generativeai.types import ContentDict

from ..base._stream import BaseStream
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
        GeminiTool,
        GeminiDynamicConfig,
        GeminiCallParams,
    ]
):
    _provider = "gemini"

    def construct_message_param(
        self, tool_calls: list | None = None, content: str | None = None
    ) -> ContentDict:
        return {
            "role": "assistant",
            "content": {
                "parts": [{"type": "text", "text": content}],
            },
        }
