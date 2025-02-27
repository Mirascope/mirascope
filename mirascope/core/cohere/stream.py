"""The `CohereStream` class for convenience around streaming LLM calls.

usage docs: learn/streams.md
"""

from cohere.types import (
    ApiMeta,
    ApiMetaBilledUnits,
    ChatMessage,
    ChatStreamEndEventFinishReason,
    NonStreamedChatResponse,
    Tool,
    ToolCall,
)

from ..base.stream import BaseStream
from ..base.types import CostMetadata
from .call_params import CohereCallParams
from .call_response import CohereCallResponse
from .call_response_chunk import CohereCallResponseChunk
from .dynamic_config import AsyncCohereDynamicConfig, CohereDynamicConfig
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
        Tool,
        AsyncCohereDynamicConfig | CohereDynamicConfig,
        CohereCallParams,
        ChatStreamEndEventFinishReason,
    ]
):
    """A class for convenience around streaming Cohere LLM calls.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.cohere import cohere_call


    @cohere_call("command-r-plus", stream=True)
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"


    stream = recommend_book("fantasy")  # returns `CohereStream` instance
    for chunk, _ in stream:
        print(chunk.content, end="", flush=True)
    ```
    """

    _provider = "cohere"

    def _construct_message_param(
        self, tool_calls: list[ToolCall] | None = None, content: str | None = None
    ) -> ChatMessage:
        return ChatMessage(
            role="assistant",  # pyright: ignore [reportCallIssue]
            message=content if content else "",
            tool_calls=tool_calls,
        )

    def construct_call_response(self) -> CohereCallResponse:
        """Constructs the call response from a consumed CohereStream.

        Raises:
            ValueError: if the stream has not yet been consumed.
        """
        if not hasattr(self, "message_param"):
            raise ValueError(
                "No stream response, check if the stream has been consumed."
            )
        if not self.input_tokens and not self.output_tokens:
            meta = None
        else:
            meta = ApiMeta(
                billed_units=ApiMetaBilledUnits(
                    input_tokens=self.input_tokens, output_tokens=self.output_tokens
                )
            )
        completion = NonStreamedChatResponse(
            generation_id=self.id,
            text=self.message_param.message,
            meta=meta,
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

    @property
    def cost_metadata(self) -> CostMetadata:
        return super().cost_metadata
