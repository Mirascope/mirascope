"""The `XAIStream` class for convenience around streaming xAI LLM calls.

usage docs: learn/streams.md
"""

from collections.abc import AsyncGenerator, Generator

from ..openai import OpenAIStream
from .call_response import XAICallResponse
from .call_response_chunk import XAICallResponseChunk
from .tool import XAITool


class XAIStream(OpenAIStream):
    """A simple wrapper around `OpenAIStream`.

    Everything is the same except updates to the `construct_call_response` method and
    the `cost` property so that cost is properly calculated using xAI's cost
    calculation method. This ensures cost calculation works for non-OpenAI models.
    """

    _provider = "xai"

    def __iter__(
        self,
    ) -> Generator[tuple[XAICallResponseChunk, XAITool | None], None, None]:
        yield from super().__iter__()  # pyright: ignore [reportReturnType]

    def __aiter__(
        self,
    ) -> AsyncGenerator[tuple[XAICallResponseChunk, XAITool | None], None]:
        return super().__aiter__()  # pyright: ignore [reportReturnType] # pragma: no cover

    @property
    def cost(self) -> float | None:
        """Returns the cost of the call."""
        response = self.construct_call_response()
        return response.cost

    def construct_call_response(self) -> XAICallResponse:
        openai_call_response = super().construct_call_response()
        openai_response = openai_call_response.response
        response = XAICallResponse.model_validate(openai_response)
        response._model = self.model
        return response
