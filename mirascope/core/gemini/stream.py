"""The `GeminiStream` class for convenience around streaming LLM calls."""

from google.ai.generativelanguage import (
    Candidate,
    Content,
    FunctionCall,
    GenerateContentResponse,
    Part,
)
from google.generativeai.types import ContentDict
from google.generativeai.types import (  # type: ignore
    GenerateContentResponse as GenerateContentResponseType,
)

from ..base._stream import BaseStream
from ._utils import calculate_cost
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
        ContentDict,
        GeminiTool,
        GeminiDynamicConfig,
        GeminiCallParams,
    ]
):
    _provider = "gemini"

    @property
    def cost(self) -> float | None:
        """Returns the cost of the call."""
        return calculate_cost(self.input_tokens, self.output_tokens, self.model)

    def _construct_message_param(
        self, tool_calls: list[FunctionCall] | None = None, content: str | None = None
    ) -> ContentDict:
        """Constructs the message parameter for the assistant.
        Gemini currently does not support tool calls for streaming.
        """
        return {"role": "model", "parts": [Part(text=content)]}

    def construct_call_response(self) -> GeminiCallResponse:
        if self.message_param is None:
            raise ValueError(
                "The `message_param` attribute must be set before constructing the call response."
            )
        response = GenerateContentResponseType.from_response(
            GenerateContentResponse(
                candidates=[
                    Candidate(
                        finish_reason=1,
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
            messages=self.messages,  # type: ignore
            call_params=self.call_params,
            call_kwargs=self.call_kwargs,
            user_message_param=self.user_message_param,
            start_time=0,
            end_time=0,
        )
