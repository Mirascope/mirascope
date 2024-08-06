"""The `OpenAIStream` class for convenience around streaming LLM calls."""

from openai.types.chat import (
    ChatCompletion,
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessage,
    ChatCompletionMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
)

from ..base._stream import BaseStream
from ._utils import calculate_cost
from .call_params import OpenAICallParams
from .call_response import OpenAICallResponse
from .call_response_chunk import OpenAICallResponseChunk
from .dynamic_config import OpenAIDynamicConfig
from .tool import OpenAITool


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
        message_param = ChatCompletionMessage(
            role="assistant",
            content=content,
        )
        if tool_calls:
            message_param.tool_calls = tool_calls
        return message_param.model_dump(exclude={"function_call"})  # type: ignore

    def construct_call_response(self) -> OpenAICallResponse:
        if self.message_param is None:
            raise ValueError(
                "No stream response, check if the stream has been consumed."
            )
        message = {
            "role": self.message_param["role"],
            "content": self.message_param.get("content", ""),
            "tool_calls": self.message_param.get("tool_calls", []),
        }
        completion = ChatCompletion(
            id="id",
            model=self.model,
            choices=[
                Choice(
                    finish_reason="stop",
                    index=0,
                    message=ChatCompletionMessage.model_validate(message),
                )
            ],
            created=0,
            object="chat.completion",
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
            start_time=0,
            end_time=0,
        )
