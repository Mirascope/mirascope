"""The `GoogleStream` class for convenience around streaming LLM calls.

usage docs: learn/streams.md
"""

from collections.abc import AsyncGenerator, Generator
from typing import Any, cast

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

from ..base.call_kwargs import BaseCallKwargs
from ..base.metadata import Metadata
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

    def __init__(
        self,
        *,
        stream: Generator[tuple[GoogleCallResponseChunk, GoogleTool | None], None, None]
        | AsyncGenerator[tuple[GoogleCallResponseChunk, GoogleTool | None], None],
        metadata: Metadata,
        tool_types: list[type[GoogleTool]] | None,
        call_response_type: type[GoogleCallResponse],
        model: str,
        prompt_template: str | None,
        fn_args: dict[str, Any],
        dynamic_config: GoogleDynamicConfig,
        messages: list[ContentListUnion | ContentListUnionDict],
        call_params: GoogleCallParams,
        call_kwargs: BaseCallKwargs[Tool],
    ) -> None:
        """Initialize GoogleStream with thinking content tracking."""
        super().__init__(
            stream=stream,
            metadata=metadata,
            tool_types=tool_types,
            call_response_type=call_response_type,
            model=model,
            prompt_template=prompt_template,
            fn_args=fn_args,
            dynamic_config=dynamic_config,
            messages=messages,
            call_params=call_params,
            call_kwargs=call_kwargs,
        )
        self.thinking = ""

    def _update_properties(self, chunk: GoogleCallResponseChunk) -> None:
        """Updates the properties of the stream, including thinking content."""
        super()._update_properties(chunk)
        self.thinking += chunk.thinking

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

        parts: list[PartDict] = []

        # Add thinking part first if we have thinking content
        if self.thinking:
            parts.append({"text": self.thinking, "thought": True})

        for pd in self.message_param.get("parts") or []:
            if pd.get("text") == "":
                # These parts are generated based only on chunk content;
                # thinking parts have empty content and are reconstructed separately.
                # Skip this so the thinking parts aren't duplicated.
                continue
            else:
                parts.append(pd)

        response = GenerateContentResponse(
            candidates=[
                Candidate(
                    finish_reason=self.finish_reasons[0]
                    if self.finish_reasons
                    else FinishReason.STOP,
                    content=Content(
                        role=self.message_param["role"],  # pyright: ignore [reportTypedDictNotRequiredAccess]
                        parts=parts,  # pyright: ignore [reportArgumentType]
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
