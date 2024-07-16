"""The `MistralStream` class for convenience around streaming LLM calls."""

from ..base import BaseMessageParam
from ..base._stream import BaseStream
from .call_params import MistralCallParams
from .call_response import MistralCallResponse
from .call_response_chunk import MistralCallResponseChunk
from .dynamic_config import MistralDynamicConfig
from .tool import MistralTool


class MistralStream(
    BaseStream[
        MistralCallResponse,
        MistralCallResponseChunk,
        BaseMessageParam,
        BaseMessageParam,
        BaseMessageParam,
        MistralTool,
        MistralDynamicConfig,
        MistralCallParams,
    ]
):
    _provider = "mistral"

    def _construct_message_param(
        self, tool_calls: list | None = None, content: str | None = None
    ):
        return {
            "role": "assistant",
            "content": content,
        }
