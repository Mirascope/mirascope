"""The `GeminiStream` class for convenience around streaming LLM calls.

usage docs: learn/streams.md
"""

from typing import cast

from google.ai.generativelanguage import (
    Candidate,
    Content,
    FunctionCall,
    GenerateContentResponse,
)
from google.generativeai.types import (
    ContentDict,
    ContentsType,
    Tool,
)
from google.generativeai.types import (
    GenerateContentResponse as GenerateContentResponseType,
)
from google.generativeai.types.content_types import PartType

from ..base.stream import BaseStream
from ..base.types import CostMetadata
from .call_params import GeminiCallParams
from .call_response import GeminiCallResponse
from .call_response_chunk import GeminiCallResponseChunk
from .dynamic_config import GeminiDynamicConfig
from .tool import GeminiTool


class GeminiStream(
    BaseStream[
        GeminiCallResponse,
        GeminiCallResponseChunk,
        ContentDict,
        ContentDict,
        ContentDict,
        ContentsType,
        GeminiTool,
        Tool,
        GeminiDynamicConfig,
        GeminiCallParams,
        Candidate.FinishReason,
    ]
):
    """A class for convenience around streaming Gemini LLM calls.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.gemini import gemini_call


    @gemini_call("gemini-1.5-flash", stream=True)
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"

    stream = recommend_book("fantasy")  # returns `GeminiStream` instance
    for chunk, _ in stream:
        print(chunk.content, end="", flush=True)
    ```
    """

    _provider = "gemini"

    def _construct_message_param(
        self, tool_calls: list[FunctionCall] | None = None, content: str | None = None
    ) -> ContentDict:
        """Constructs the message parameter for the assistant."""
        return {
            "role": "model",
            "parts": cast(list[PartType], [{"text": content}] + (tool_calls or [])),
        }

    def construct_call_response(self) -> GeminiCallResponse:
        """Constructs the call response from a consumed GeminiStream.

        Raises:
            ValueError: if the stream has not yet been consumed.
        """
        if not hasattr(self, "message_param"):
            raise ValueError(
                "No stream response, check if the stream has been consumed."
            )
        response = GenerateContentResponseType.from_response(
            GenerateContentResponse(
                candidates=[
                    Candidate(
                        finish_reason=self.finish_reasons[0]
                        if self.finish_reasons
                        else Candidate.FinishReason.STOP,
                        content=Content(
                            role=self.message_param["role"],
                            parts=self.message_param["parts"],
                        ),
                    )
                ]
            )
        )
        return GeminiCallResponse(
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
