"""The `VertexStream` class for convenience around streaming LLM calls.

usage docs: learn/streams.md
"""

from typing import cast

from google.cloud.aiplatform_v1beta1.types import FunctionCall
from vertexai.generative_models import (
    Candidate,
    Content,
    FinishReason,
    GenerationResponse,
    Part,
    Tool,
)

from ..base.stream import BaseStream
from ..base.types import CostMetadata
from .call_params import VertexCallParams
from .call_response import VertexCallResponse
from .call_response_chunk import VertexCallResponseChunk
from .dynamic_config import VertexDynamicConfig
from .tool import VertexTool


class VertexStream(
    BaseStream[
        VertexCallResponse,
        VertexCallResponseChunk,
        Content,
        Content,
        Content,
        Content,
        VertexTool,
        Tool,
        VertexDynamicConfig,
        VertexCallParams,
        FinishReason,
    ]
):
    """A class for convenience around streaming Vertex LLM calls.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.vertex import vertex_call


    @vertex_call("gemini-1.5-flash", stream=True)
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"


    stream = recommend_book("fantasy")  # returns `VertexStream` instance
    for chunk, _ in stream:
        print(chunk.content, end="", flush=True)
    ```
    """

    _provider = "vertex"

    def _construct_message_param(
        self,
        tool_calls: list[FunctionCall] | None = None,
        content: str | None = None,
    ) -> Content:
        """Constructs the message parameter for the assistant."""
        return Content(
            role="model",
            parts=cast(list[Part], [Part.from_text(content)] + (tool_calls or [])),  # pyright: ignore [reportArgumentType]
        )

    def construct_call_response(self) -> VertexCallResponse:
        """Constructs the call response from a consumed VertexStream.

        Raises:
            ValueError: if the stream has not yet been consumed.
        """
        if not hasattr(self, "message_param"):
            raise ValueError(
                "No stream response, check if the stream has been consumed."
            )
        response = GenerationResponse.from_dict(
            {
                "candidates": [
                    Candidate.from_dict(
                        {
                            "finish_reason": self.finish_reasons[0]
                            if self.finish_reasons
                            else FinishReason.STOP,
                            "content": Content(
                                role=self.message_param.role,
                                parts=self.message_param.parts,
                            ).to_dict(),
                        }
                    ).to_dict()
                ]
            }
        )
        return VertexCallResponse(
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
        return super().cost_metadata
