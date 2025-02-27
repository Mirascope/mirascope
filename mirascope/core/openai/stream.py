"""The `OpenAIStream` class for convenience around streaming LLM calls.

usage docs: learn/streams.md
"""

from collections.abc import AsyncGenerator, Generator

from openai.types.chat import (
    ChatCompletion,
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessage,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCall,
    ChatCompletionMessageToolCallParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_message_tool_call_param import Function
from openai.types.completion_usage import CompletionUsage

from ..base.stream import BaseStream
from ..base.types import CostMetadata
from .call_params import OpenAICallParams
from .call_response import OpenAICallResponse
from .call_response_chunk import OpenAICallResponseChunk
from .dynamic_config import OpenAIDynamicConfig
from .tool import OpenAITool

FinishReason = Choice.__annotations__["finish_reason"]


class OpenAIStream(
    BaseStream[
        OpenAICallResponse,
        OpenAICallResponseChunk,
        ChatCompletionUserMessageParam,
        ChatCompletionAssistantMessageParam,
        ChatCompletionToolMessageParam,
        ChatCompletionMessageParam,
        OpenAITool,
        ChatCompletionToolParam,
        OpenAIDynamicConfig,
        OpenAICallParams,
        FinishReason,
    ]
):
    """A class for convenience around streaming OpenAI LLM calls.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.openai import openai_call


    @openai_call("gpt-4o-mini", stream=True)
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"


    stream = recommend_book("fantasy")  # returns `OpenAIStream` instance
    for chunk, _ in stream:
        print(chunk.content, end="", flush=True)
    ```
    """

    audio_id: str | None = None

    _provider = "openai"

    def __iter__(
        self,
    ) -> Generator[tuple[OpenAICallResponseChunk, OpenAITool | None], None, None]:
        for chunk, tool in super().__iter__():
            if (
                (choices := chunk.chunk.choices)
                and (audio := getattr(choices[0].delta, "audio", None))
                and (audio_id := audio.get("id"))
            ):
                self.audio_id = audio_id
            yield chunk, tool

    def __aiter__(
        self,
    ) -> AsyncGenerator[tuple[OpenAICallResponseChunk, OpenAITool | None], None]:
        aiter = super().__aiter__()

        async def generator() -> AsyncGenerator[
            tuple[OpenAICallResponseChunk, OpenAITool | None], None
        ]:
            async for chunk, tool in aiter:
                if (
                    (choices := chunk.chunk.choices)
                    and (audio := getattr(choices[0].delta, "audio", None))
                    and (audio_id := audio.get("id"))
                ):
                    self.audio_id = audio_id
                yield chunk, tool

        return generator()

    def _construct_message_param(
        self,
        tool_calls: list[ChatCompletionMessageToolCall] | None = None,
        content: str | None = None,
    ) -> ChatCompletionAssistantMessageParam:
        """Constructs the message parameter for the assistant."""
        message_param = ChatCompletionAssistantMessageParam(
            role="assistant", content=content
        )
        if tool_calls:
            message_param["tool_calls"] = [
                ChatCompletionMessageToolCallParam(
                    type="function",
                    function=Function(
                        arguments=tool_call.function.arguments,
                        name=tool_call.function.name,
                    ),
                    id=tool_call.id,
                )
                for tool_call in tool_calls
            ]
        if self.audio_id:
            message_param["audio"] = {"id": self.audio_id}
        return message_param

    def construct_call_response(self) -> OpenAICallResponse:
        """Constructs the call response from a consumed OpenAIStream.

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
                    if self.finish_reasons
                    else "stop",
                    index=0,
                    message=ChatCompletionMessage.model_validate(message),
                )
            ],
            created=0,
            object="chat.completion",
            usage=usage,
        )
        return OpenAICallResponse(
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
