"""The `GroqStream` class for convenience around streaming LLM calls.

usage docs: learn/streams.md
"""

from groq.types.chat import (
    ChatCompletion,
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCallParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
    ChatCompletionUserMessageParam,
)
from groq.types.chat.chat_completion import Choice
from groq.types.chat.chat_completion_message import ChatCompletionMessage
from groq.types.completion_usage import CompletionUsage

from ..base.stream import BaseStream
from ..base.types import CostMetadata
from .call_params import GroqCallParams
from .call_response import GroqCallResponse
from .call_response_chunk import GroqCallResponseChunk
from .dynamic_config import AsyncGroqDynamicConfig, GroqDynamicConfig
from .tool import GroqTool

FinishReason = Choice.__annotations__["finish_reason"]


class GroqStream(
    BaseStream[
        GroqCallResponse,
        GroqCallResponseChunk,
        ChatCompletionUserMessageParam,
        ChatCompletionAssistantMessageParam,
        ChatCompletionToolMessageParam,
        ChatCompletionMessageParam,
        GroqTool,
        ChatCompletionToolParam,
        AsyncGroqDynamicConfig | GroqDynamicConfig,
        GroqCallParams,
        FinishReason,
    ]
):
    """A class for convenience around streaming Groq LLM calls.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.groq import groq_call


    @groq_call("llama-3.1-8b-instant", stream=True)
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"

    stream = recommend_book("fantasy")  # returns `GroqStream` instance
    for chunk, _ in stream:
        print(chunk.content, end="", flush=True)
    ```
    """

    _provider = "groq"

    def _construct_message_param(
        self,
        tool_calls: list[ChatCompletionMessageToolCallParam] | None = None,
        content: str | None = None,
    ) -> ChatCompletionAssistantMessageParam:
        message_param = ChatCompletionAssistantMessageParam(
            role="assistant",
            content=content,
        )
        if tool_calls:
            message_param["tool_calls"] = tool_calls
        return message_param

    def construct_call_response(self) -> GroqCallResponse:
        """Constructs the call response from a consumed GroqStream.

        Raises:
            ValueError: if the stream has not yet been consumed.
        """
        if not hasattr(self, "message_param"):
            raise ValueError(
                "No stream response, check if the stream has been consumed."
            )
        message = {
            "role": self.message_param["role"],
            "content": self.message_param.get("content", ""),
            "tool_calls": self.message_param.get("tool_calls", []),
        }
        if not self.input_tokens and not self.output_tokens:
            usage = None
        else:
            usage = CompletionUsage(
                prompt_tokens=int(self.input_tokens or 0),
                completion_tokens=int(self.output_tokens or 0),
                total_tokens=int(self.input_tokens or 0) + int(self.output_tokens or 0),
            )
        completion = ChatCompletion(
            id=self.id if self.id else "",
            model=self.model,
            choices=[
                Choice(
                    finish_reason=self.finish_reasons[0]
                    if self.finish_reasons and self.finish_reasons[0]
                    else "stop",
                    index=0,
                    message=ChatCompletionMessage.model_validate(message),
                )
            ],
            created=0,
            object="chat.completion",
            usage=usage,
        )
        return GroqCallResponse(
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
