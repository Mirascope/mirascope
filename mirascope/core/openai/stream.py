"""The `OpenAIStream` class for convenience around streaming LLM calls."""

from openai.types.chat import (
    ChatCompletion,
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessage,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCall,
    ChatCompletionMessageToolCallParam,
    ChatCompletionToolMessageParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_message_tool_call_param import Function
from openai.types.completion_usage import CompletionUsage

from ..base._stream import BaseStream
from ._utils import calculate_cost
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
        OpenAIDynamicConfig,
        OpenAICallParams,
        FinishReason,
    ]
):
    _provider = "openai"

    @property
    def cost(self) -> float | None:
        """Returns the cost of the call."""
        return calculate_cost(self.input_tokens, self.output_tokens, self.model)

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
        return message_param

    def construct_call_response(self) -> OpenAICallResponse:
        """Constructs the call response from a consumed OpenAIStream."""
        if self.message_param is None:
            raise ValueError(  # pragma: no cover
                "No stream response, check if the stream has been consumed."
            )
        message = {
            "role": self.message_param["role"],
            "content": self.message_param.get("content", ""),
            "tool_calls": self.message_param.get("tool_calls", []),
        }
        usage = CompletionUsage(
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
        )
        if self.input_tokens:
            usage.prompt_tokens = int(self.input_tokens)
        if self.output_tokens:
            usage.completion_tokens = int(self.output_tokens)
        usage.total_tokens = usage.prompt_tokens + usage.completion_tokens
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
