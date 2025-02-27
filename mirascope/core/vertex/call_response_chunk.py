"""This module contains the `VertexCallResponseChunk` class.

usage docs: learn/streams.md#handling-streamed-responses
"""

from vertexai.generative_models import FinishReason, GenerationResponse

from ..base import BaseCallResponseChunk, types
from ..base.types import CostMetadata
from ._utils._convert_finish_reason_to_common_finish_reasons import (
    _convert_finish_reasons_to_common_finish_reasons,
)


class VertexCallResponseChunk(
    BaseCallResponseChunk[GenerationResponse, FinishReason]  # , Candidate.FinishReason]
):
    """A convenience wrapper around the Vertex AI streamed response chunks.

    When calling the Vertex AI API using a function decorated with `vertex_call` and
    `stream` set to `True`, the stream will contain `VertexCallResponseChunk` instances
    with properties that allow for more convenient access to commonly used attributes.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.vertex import vertex_call


    @vertex_call("gemini-1.5-flash", stream=True)
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"

    stream = recommend_book("fantasy")  # response is an `VertexStream`
    for chunk, _ in stream:
        print(chunk.content, end="", flush=True)
    ```
    """

    @property
    def content(self) -> str:
        """Returns the chunk content for the 0th choice."""
        return self.chunk.candidates[0].content.parts[0].text

    @property
    def finish_reasons(self) -> list[FinishReason]:
        """Returns the finish reasons of the response."""
        return [candidate.finish_reason for candidate in self.chunk.candidates]

    @property
    def model(self) -> None:
        """Returns the model name.

        vertex does not return model, so we return None
        """
        return None

    @property
    def id(self) -> str | None:
        """Returns the id of the response.

        vertex does not return an id
        """
        return None

    @property
    def usage(self) -> None:
        """Returns the usage of the chat completion.

        vertex does not have Usage, so we return None
        """
        return None

    @property
    def input_tokens(self) -> None:
        """Returns the number of input tokens."""
        return None

    @property
    def cached_tokens(self) -> None:
        """Returns the number of cached tokens."""
        return None

    @property
    def output_tokens(self) -> None:
        """Returns the number of output tokens."""
        return None

    @property
    def cost_metadata(self) -> CostMetadata:
        """Returns the cost metadata."""
        return super().cost_metadata

    @property
    def common_finish_reasons(self) -> list[types.FinishReason] | None:
        return _convert_finish_reasons_to_common_finish_reasons(
            [finish_reason.name for finish_reason in self.finish_reasons]
        )
