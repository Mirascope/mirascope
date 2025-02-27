"""The `AzureStream` class for convenience around streaming LLM calls.

usage docs: learn/streams.md
"""

import datetime

from azure.ai.inference.models import (
    AssistantMessage,
    ChatChoice,
    ChatCompletions,
    ChatCompletionsToolCall,
    ChatCompletionsToolDefinition,
    ChatRequestMessage,
    ChatResponseMessage,
    CompletionsFinishReason,
    CompletionsUsage,
    FunctionCall,
    ToolMessage,
    UserMessage,
)

from ..base.stream import BaseStream
from ..base.types import CostMetadata
from .call_params import AzureCallParams
from .call_response import AzureCallResponse
from .call_response_chunk import AzureCallResponseChunk
from .dynamic_config import AsyncAzureDynamicConfig, AzureDynamicConfig
from .tool import AzureTool


class AzureStream(
    BaseStream[
        AzureCallResponse,
        AzureCallResponseChunk,
        UserMessage,
        AssistantMessage,
        ToolMessage,
        ChatRequestMessage,
        AzureTool,
        ChatCompletionsToolDefinition,
        AsyncAzureDynamicConfig | AzureDynamicConfig,
        AzureCallParams,
        CompletionsFinishReason,
    ]
):
    """A class for convenience around streaming Azure LLM calls.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.azure import azure_call


    @azure_call("gpt-4o-mini", stream=True)
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"


    stream = recommend_book("fantasy")  # returns `AzureStream` instance
    for chunk, _ in stream:
        print(chunk.content, end="", flush=True)
    ```
    """

    _provider = "azure"

    def _construct_message_param(
        self,
        tool_calls: list[ChatCompletionsToolCall] | None = None,
        content: str | None = None,
    ) -> AssistantMessage:
        """Constructs the message parameter for the assistant."""
        message_param = AssistantMessage(content=content)
        if tool_calls:
            message_param["tool_calls"] = [
                ChatCompletionsToolCall(
                    function=FunctionCall(
                        arguments=tool_call.function.arguments,
                        name=tool_call.function.name,
                    ),
                    id=tool_call.id,
                )
                for tool_call in tool_calls
            ]
        return message_param

    def construct_call_response(self) -> AzureCallResponse:
        """Constructs the call response from a consumed AzureStream.

        Raises:
            ValueError: if the stream has not yet been consumed.
        """
        if not hasattr(self, "message_param"):
            raise ValueError(
                "No stream response, check if the stream has been consumed."
            )
        message = ChatResponseMessage(
            role=self.message_param["role"],
            content=self.message_param.get("content", ""),
            tool_calls=self.message_param.get("tool_calls", []),
        )
        if not self.input_tokens and not self.output_tokens:
            usage = CompletionsUsage(
                completion_tokens=0, prompt_tokens=0, total_tokens=0
            )
        else:
            usage = CompletionsUsage(
                prompt_tokens=int(self.input_tokens or 0),
                completion_tokens=int(self.output_tokens or 0),
                total_tokens=int(self.input_tokens or 0) + int(self.output_tokens or 0),
            )
        completion = ChatCompletions(
            id=self.id if self.id else "",
            model=self.model,
            choices=[
                ChatChoice(
                    finish_reason=self.finish_reasons[0]
                    if self.finish_reasons
                    else "stop",
                    index=0,
                    message=message,
                )
            ],
            created=datetime.datetime.now(),
            usage=usage,
        )
        return AzureCallResponse(
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
        """Get metadata required for cost calculation."""
        return super().cost_metadata
