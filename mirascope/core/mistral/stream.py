"""The `MistralStream` class for convenience around streaming LLM calls.

usage docs: learn/streams.md
"""

from typing import Any, cast

from mistralai.models import (
    AssistantMessage,
    ChatCompletionChoice,
    ChatCompletionResponse,
    FinishReason,
    SystemMessage,
    ToolMessage,
    UsageInfo,
    UserMessage,
)

from ..base.stream import BaseStream
from ..base.types import CostMetadata
from .call_params import MistralCallParams
from .call_response import MistralCallResponse
from .call_response_chunk import MistralCallResponseChunk
from .dynamic_config import MistralDynamicConfig
from .tool import MistralTool


class MistralStream(
    BaseStream[
        MistralCallResponse,
        MistralCallResponseChunk,
        UserMessage,
        AssistantMessage,
        ToolMessage,
        AssistantMessage | SystemMessage | ToolMessage | UserMessage,
        MistralTool,
        dict[str, Any],
        MistralDynamicConfig,
        MistralCallParams,
        FinishReason,
    ]
):
    """A class for convenience around streaming Mistral LLM calls.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.mistral import mistral_call


    @mistral_call("mistral-large-latest", stream=True)
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"


    stream = recommend_book("fantasy")  # returns `MistralStream` instance
    for chunk, _ in stream:
        print(chunk.content, end="", flush=True)
    ```
    """

    _provider = "mistral"

    def _construct_message_param(
        self, tool_calls: list | None = None, content: str | None = None
    ) -> AssistantMessage:
        message_param = AssistantMessage(
            content=content if content else "", tool_calls=tool_calls
        )
        return message_param

    def construct_call_response(self) -> MistralCallResponse:
        """Constructs the call response from a consumed MistralStream.

        Raises:
            ValueError: if the stream has not yet been consumed.
        """
        if not hasattr(self, "message_param"):
            raise ValueError(
                "No stream response, check if the stream has been consumed."
            )
        usage = UsageInfo(
            prompt_tokens=int(self.input_tokens or 0),
            completion_tokens=int(self.output_tokens or 0),
            total_tokens=int(self.input_tokens or 0) + int(self.output_tokens or 0),
        )
        finish_reason = cast(FinishReason, (self.finish_reasons or [])[0])
        completion = ChatCompletionResponse(
            id=self.id if self.id else "",
            choices=[
                ChatCompletionChoice(
                    finish_reason=finish_reason,
                    index=0,
                    message=self.message_param,
                )
            ],
            created=0,
            model=self.model,
            object="",
            usage=usage,
        )
        return MistralCallResponse(
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
