"""This module contains the `BedrockCallResponseChunk` class.

usage docs: learn/streams.md#handling-streamed-responses
"""

from typing import cast

from pydantic import SkipValidation
from types_aiobotocore_bedrock_runtime.literals import StopReasonType as FinishReason

from ..base import BaseCallResponseChunk, types
from ..base.types import CostMetadata
from ._types import AsyncStreamOutputChunk, StreamOutputChunk, TokenUsageTypeDef
from ._utils._convert_finish_reason_to_common_finish_reasons import (
    _convert_finish_reasons_to_common_finish_reasons,
)


class BedrockCallResponseChunk(
    BaseCallResponseChunk[StreamOutputChunk | AsyncStreamOutputChunk, FinishReason]
):
    """A convenience wrapper around the Bedrock `ChatCompletionChunk` streamed chunks.

    When calling the Bedrock API using a function decorated with `bedrock_call` and
    `stream` set to `True`, the stream will contain `BedrockResponseChunk` instances with
    properties that allow for more convenient access to commonly used attributes.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.bedrock import bedrock_call


    @bedrock_call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
    @prompt_template("Recommend a {genre} book")
    def recommend_book(genre: str):
        ...


    stream = recommend_book("fantasy")  # response is an `BedrockStream`
    for chunk, _ in stream:
        print(chunk.content, end="", flush=True)
    ```
    """

    chunk: SkipValidation[StreamOutputChunk | AsyncStreamOutputChunk]

    @property
    def content(self) -> str:
        """Returns the content for the 0th choice delta."""
        if content_block_delta := self.chunk.get("contentBlockDelta"):
            return content_block_delta["delta"].get("text", "")
        return ""

    @property
    def finish_reasons(self) -> list[FinishReason]:
        """Returns the finish reasons of the response."""
        if (stop_reason := self.chunk.get("messageStop")) and stop_reason.get(
            "stopReason"
        ):
            return [stop_reason["stopReason"]]
        return []

    @property
    def model(self) -> str:
        """Returns the name of the response model."""
        return self.chunk["model"]

    @property
    def id(self) -> str:
        """Returns the id of the response."""
        return self.chunk["responseMetadata"]["RequestId"]

    @property
    def usage(self) -> TokenUsageTypeDef | None:
        """Returns the usage of the chat completion."""
        usage = self.chunk.get("metadata", {}).get("usage")
        if usage:
            return usage
        return None

    @property
    def input_tokens(self) -> int | None:
        """Returns the number of input tokens."""
        if self.usage:
            return self.usage["inputTokens"]
        return None

    @property
    def cached_tokens(self) -> int | None:
        """Returns the number of cached tokens."""
        return None

    @property
    def output_tokens(self) -> int | None:
        """Returns the number of output tokens."""
        if self.usage:
            return self.usage["outputTokens"]
        return None

    @property
    def cost_metadata(self) -> CostMetadata:
        """Returns the cost metadata."""
        return super().cost_metadata

    @property
    def common_finish_reasons(self) -> list[types.FinishReason] | None:
        return _convert_finish_reasons_to_common_finish_reasons(
            cast(list[str], self.finish_reasons)
        )
