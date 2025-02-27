"""The `BedrockStream` class for convenience around streaming LLM calls.

usage docs: learn/streams.md
"""

from typing import Any, cast

from mypy_boto3_bedrock_runtime.literals import StopReasonType as FinishReason
from mypy_boto3_bedrock_runtime.type_defs import (
    ConverseResponseTypeDef,
    ConverseStreamMetadataEventTypeDef,
    MessageOutputTypeDef,
    ResponseMetadataTypeDef,
)
from types_aiobotocore_bedrock_runtime.type_defs import (
    ConverseStreamMetadataEventTypeDef as AsyncConverseStreamMetadataEventTypeDef,
)
from types_aiobotocore_bedrock_runtime.type_defs import (
    ResponseMetadataTypeDef as AsyncResponseMetadataTypeDef,
)

from ..base.stream import BaseStream
from ..base.types import CostMetadata
from ._types import (
    AssistantMessageTypeDef,
    InternalBedrockMessageParam,
    ToolTypeDef,
    ToolUseBlockContentTypeDef,
    ToolUseBlockMessageTypeDef,
    UserMessageTypeDef,
)
from .call_params import BedrockCallParams
from .call_response import BedrockCallResponse
from .call_response_chunk import BedrockCallResponseChunk
from .dynamic_config import AsyncBedrockDynamicConfig, BedrockDynamicConfig
from .tool import BedrockTool

_DEFAULT_RESPONSE_METADATA = ResponseMetadataTypeDef(
    RequestId="", HTTPStatusCode=500, HTTPHeaders={}, RetryAttempts=0
)


class BedrockStream(
    BaseStream[
        BedrockCallResponse,
        BedrockCallResponseChunk,
        UserMessageTypeDef,
        AssistantMessageTypeDef,
        ToolUseBlockMessageTypeDef,
        InternalBedrockMessageParam,
        BedrockTool,
        ToolTypeDef,
        AsyncBedrockDynamicConfig | BedrockDynamicConfig,
        BedrockCallParams,
        FinishReason,
    ]
):
    """A class for convenience around streaming Bedrock LLM calls.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.bedrock import bedrock_call


    @bedrock_call("gpt-4o-mini", stream=True)
    @prompt_template("Recommend a {genre} book")
    def recommend_book(genre: str):
        ...


    stream = recommend_book("fantasy")  # returns `BedrockStream` instance
    for chunk, _ in stream:
        print(chunk.content, end="", flush=True)
    ```
    """

    _provider = "bedrock"

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        super().__init__(*args, **kwargs)
        self._metadata: (
            ConverseStreamMetadataEventTypeDef
            | AsyncConverseStreamMetadataEventTypeDef
            | None
        ) = None
        self._response_metadata: (
            ResponseMetadataTypeDef | AsyncResponseMetadataTypeDef
        ) = _DEFAULT_RESPONSE_METADATA

    def _construct_message_param(
        self,
        tool_calls: list[ToolUseBlockContentTypeDef] | None = None,
        content: str | None = None,
    ) -> AssistantMessageTypeDef:
        """Constructs the message parameter for the assistant."""
        contents = []
        if content is not None:
            contents.append({"text": content})

        if tool_calls:
            contents += [
                cast(ToolUseBlockContentTypeDef, {"toolUse": tool_call})
                for tool_call in tool_calls
            ]
        message_param = AssistantMessageTypeDef(role="assistant", content=contents)
        return message_param

    def _update_properties(self, chunk: BedrockCallResponseChunk) -> None:
        """Updates the properties of the stream."""
        super()._update_properties(chunk)
        if metadata := chunk.chunk.get("metadata"):
            self._metadata = metadata
        self._response_metadata = chunk.chunk["responseMetadata"]

    def construct_call_response(self) -> BedrockCallResponse:
        """Constructs the call response from a consumed BedrockStream.

        Raises:
            ValueError: if the stream has not yet been consumed.
        """
        if not hasattr(self, "message_param"):
            raise ValueError(
                "No stream response, check if the stream has been consumed."
            )
        response = ConverseResponseTypeDef(
            output={"message": cast(MessageOutputTypeDef, self.message_param)},
            stopReason=self.finish_reasons[0] if self.finish_reasons else "end_turn",
            usage=self.metadata.get("usage", {}),
            metrics=self.metadata.get("metrics", {}),
            additionalModelResponseFields={},
            trace=self.metadata.get("trace", {}),
            ResponseMetadata=self._response_metadata,
        )
        return BedrockCallResponse(
            metadata=self.metadata,
            response=response,
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
