"""The `CohereStream` class for convenience around streaming LLM calls."""

from cohere.types import (
    ApiMeta,
    ApiMetaBilledUnits,
    ChatMessage,
    NonStreamedChatResponse,
    ToolCall,
)

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

    def construct_call_response(self) -> CohereCallResponse:
        """Constructs the call response from a consumed CohereStream."""
        if self.message_param is None:
            raise ValueError(  # pragma: no cover
                "No stream response, check if the stream has been consumed."
            )
        usage = ApiMetaBilledUnits(
            input_tokens=self.input_tokens, output_tokens=self.output_tokens
        )
        completion = NonStreamedChatResponse(
            generation_id=self.id,
            text=self.message_param.message,
            meta=ApiMeta(billed_units=usage),
            finish_reason=self.finish_reasons[0] if self.finish_reasons else None,
        )

        return CohereCallResponse(
            metadata=self.metadata,
            response=completion,
            tool_types=self.tool_types,
            prompt_template=self.prompt_template,
            fn_args=self.fn_args if self.fn_args else {},
            dynamic_config=self.dynamic_config,
            messages=self.messages,
            call_params=self.call_params,
            call_kwargs=self.call_kwargs,
            user_message_param=self.user_message_param,
            start_time=self.start_time,
            end_time=self.end_time,
        )
