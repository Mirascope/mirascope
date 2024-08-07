"""The `AnthropicStream` class for convenience around streaming LLM calls."""

from typing import Literal

from anthropic.types import Message, MessageParam, TextBlock, ToolUseBlock, Usage
from anthropic.types.content_block import ContentBlock
from anthropic.types.text_block_param import TextBlockParam
from anthropic.types.tool_use_block_param import ToolUseBlockParam
from pydantic import BaseModel

from ..base._stream import BaseStream
from ._utils import calculate_cost
from .call_params import AnthropicCallParams
from .call_response import AnthropicCallResponse
from .call_response_chunk import AnthropicCallResponseChunk
from .dynamic_config import AnthropicDynamicConfig
from .tool import AnthropicTool


class AnthropicStream(
    BaseStream[
        AnthropicCallResponse,
        AnthropicCallResponseChunk,
        MessageParam,
        MessageParam,
        MessageParam,
        MessageParam,
        AnthropicTool,
        AnthropicDynamicConfig,
        AnthropicCallParams,
    ]
):
    _provider = "anthropic"

    @property
    def cost(self) -> float | None:
        """Returns the cost of the call."""
        return calculate_cost(self.input_tokens, self.output_tokens, self.model)

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
        if self.message_param is None:
            raise ValueError(  # pragma: no cover
                "No stream response, check if the stream has been consumed."
            )
        usage = Usage(input_tokens=0, output_tokens=0)
        if self.input_tokens:
            usage.input_tokens = int(self.input_tokens)
        if self.output_tokens:
            usage.output_tokens = int(self.output_tokens)

        message_param: list[ContentBlock] = []

        if isinstance(self.message_param["content"], str):
            message_param.append(
                TextBlock(text=self.message_param["content"], type="text")
            )
        else:
            for content in self.message_param["content"]:
                content_type = (
                    content.type if isinstance(content, BaseModel) else content["type"]
                )

                if content_type == "text":
                    message_param.append(TextBlock.model_validate(content))
                elif content_type == "tool_use":
                    message_param.append(ToolUseBlock.model_validate(content))
        completion = Message(
            id=self.id if self.id else "",
            content=message_param,
            model=self.model,
            role="assistant",
            stop_reason=self.finish_reasons[0] if self.finish_reasons else None,  # type: ignore
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
