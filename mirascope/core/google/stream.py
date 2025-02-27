"""The `GoogleStream` class for convenience around streaming LLM calls.

usage docs: learn/streams.md
"""

from typing import cast

from google.genai.types import (
    Candidate,
    Content,
    ContentDict,
    ContentListUnion,
    ContentListUnionDict,
    FinishReason,
    FunctionCall,
    GenerateContentResponse,
    GenerateContentResponseUsageMetadata,
    PartDict,
    Tool,
)

from ..base.stream import BaseStream
from ..base.types import CostMetadata
from .call_params import GoogleCallParams
from .call_response import GoogleCallResponse
from .call_response_chunk import GoogleCallResponseChunk
from .dynamic_config import GoogleDynamicConfig
from .tool import GoogleTool


class GoogleStream(
    BaseStream[
        GoogleCallResponse,
        GoogleCallResponseChunk,
        ContentDict,
        ContentDict,
        ContentDict,
        ContentListUnion | ContentListUnionDict,
        GoogleTool,
        Tool,
        GoogleDynamicConfig,
        GoogleCallParams,
        FinishReason,
    ]
):
    """A class for convenience around streaming Google LLM calls.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.google import google_call


    @google_call("google-1.5-flash", stream=True)
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"

    stream = recommend_book("fantasy")  # returns `GoogleStream` instance
    for chunk, _ in stream:
        print(chunk.content, end="", flush=True)
    ```
    """

    _provider = "google"

    def _construct_message_param(
        self, tool_calls: list[FunctionCall] | None = None, content: str | None = None
    ) -> ContentDict:
        """Constructs the message parameter for the assistant."""
        return {
            "role": "model",
            "parts": cast(
                list[PartDict],
                [{"text": content}]
                + (
                    [
                        {"function_call": tool_call}
                        for tool_call in (tool_calls or [])
                        if tool_calls
                    ]
                    or []
                ),
            ),
        }

    def construct_call_response(self) -> GoogleCallResponse:
        """Constructs the call response from a consumed GoogleStream.

        Raises:
            ValueError: if the stream has not yet been consumed.
        """
        if not hasattr(self, "message_param"):
            raise ValueError(
                "No stream response, check if the stream has been consumed."
            )
        candidates_token_count = (
            int(self.output_tokens) if self.output_tokens is not None else None
        )
        prompt_token_count = (
            int(self.input_tokens) if self.input_tokens is not None else None
        )
        total_token_count = int(candidates_token_count or 0) + int(
            prompt_token_count or 0
        )
        response = GenerateContentResponse(
            candidates=[
                Candidate(
                    finish_reason=self.finish_reasons[0]
                    if self.finish_reasons
                    else FinishReason.STOP,
                    content=Content(
                        role=self.message_param["role"],  # pyright: ignore [reportTypedDictNotRequiredAccess]
                        parts=self.message_param["parts"],  # pyright: ignore [reportTypedDictNotRequiredAccess, reportArgumentType]
                    ),
                )
            ],
            model_version=self.model,
            usage_metadata=GenerateContentResponseUsageMetadata(
                candidates_token_count=candidates_token_count,
                prompt_token_count=prompt_token_count,
                total_token_count=total_token_count,
            ),
        )

        return GoogleCallResponse(
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
