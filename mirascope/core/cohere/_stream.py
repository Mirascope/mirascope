"""The `CohereStream` class for convenience around streaming LLM calls."""

from ..base import BaseMessageParam
from ..base._stream import BaseStream
from .call_params import CohereCallParams
from .call_response import CohereCallResponse
from .call_response_chunk import CohereCallResponseChunk
from .dynamic_config import CohereDynamicConfig
from .tool import CohereTool


class CohereStream(
    BaseStream[
        CohereCallResponse,
        CohereCallResponseChunk,
        BaseMessageParam,
        BaseMessageParam,
        BaseMessageParam,
        CohereTool,
        CohereDynamicConfig,
        CohereCallParams,
    ]
):
    _provider = "cohere"

    def _construct_message_param(
        self, tool_calls: list | None = None, content: str | None = None
    ) -> BaseMessageParam:
        print(tool_calls)
        return {
            "role": "assistant",
            "message": content
            if "message" in self.message_param_type.__annotations__
            else None,
            "tool_calls": tool_calls,
        }
