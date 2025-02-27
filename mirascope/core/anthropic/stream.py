"""The `AnthropicStream` class for convenience around streaming LLM calls.

usage docs: learn/streams.md
"""

from anthropic.types import (
    Message,
    MessageParam,
    TextBlock,
    ToolParam,
    ToolUseBlock,
    Usage,
)
from anthropic.types.content_block import ContentBlock
from anthropic.types.text_block_param import TextBlockParam
from anthropic.types.tool_use_block_param import ToolUseBlockParam
from pydantic import BaseModel

from ..base.stream import BaseStream
from ..base.types import CostMetadata
from .call_params import AnthropicCallParams
from .call_response import AnthropicCallResponse
from .call_response_chunk import AnthropicCallResponseChunk
from .dynamic_config import AnthropicDynamicConfig, AsyncAnthropicDynamicConfig
from .tool import AnthropicTool

FinishReason = Message.__annotations__["stop_reason"]


class AnthropicStream(
    BaseStream[
        AnthropicCallResponse,
        AnthropicCallResponseChunk,
        MessageParam,
        MessageParam,
        MessageParam,
        MessageParam,
        AnthropicTool,
        ToolParam,
        AsyncAnthropicDynamicConfig | AnthropicDynamicConfig,
        AnthropicCallParams,
        FinishReason,
    ]
):
    """A class for convenience around streaming Anthropic LLM calls.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.anthropic import anthropic_call


    @anthropic_call("claude-3-5-sonnet-20240620", stream=True)
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"


    stream = recommend_book("fantasy")  # returns `AnthropicStream` instance
    for chunk, _ in stream:
        print(chunk.content, end="", flush=True)
    ```
    """

    _provider = "anthropic"

    def _construct_message_param(
        self, tool_calls: list[ToolUseBlock] | None = None, content: str | None = None
    ) -> MessageParam:
        """Constructs the message parameter for the assistant."""
        message_param_tool_calls = []
        if tool_calls:
            message_param_tool_calls: list[ToolUseBlockParam] = [
                ToolUseBlockParam(
                    id=tool_call.id,
                    input=tool_call.input,
                    name=tool_call.name,
                    type="tool_use",
                )
                for tool_call in tool_calls
            ]
        return {
            "role": "assistant",
            "content": ([TextBlockParam(text=content, type="text")] if content else [])
            + message_param_tool_calls,
        }

    def construct_call_response(self) -> AnthropicCallResponse:
        """Constructs the call response from a consumed AnthropicStream.

        Raises:
            ValueError: if the stream has not yet been consumed.
        """
        if not hasattr(self, "message_param"):
            raise ValueError(
                "No stream response, check if the stream has been consumed."
            )
        usage = Usage(
            input_tokens=int(self.input_tokens or 0),
            output_tokens=int(self.output_tokens or 0),
        )

        content_blocks: list[ContentBlock] = []

        if isinstance(self.message_param["content"], str):
            content_blocks.append(
                TextBlock(text=self.message_param["content"], type="text")
            )
        else:
            for content in self.message_param["content"]:
                content_type = (
                    content.type if isinstance(content, BaseModel) else content["type"]
                )

                if content_type == "text":
                    content_blocks.append(TextBlock.model_validate(content))
                elif content_type == "tool_use":
                    content_blocks.append(ToolUseBlock.model_validate(content))
        completion = Message(
            id=self.id if self.id else "",
            content=content_blocks,
            model=self.model,
            role="assistant",
            stop_reason=self.finish_reasons[0] if self.finish_reasons else None,
            stop_sequence=None,
            type="message",
            usage=usage,
        )
        return AnthropicCallResponse(
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
