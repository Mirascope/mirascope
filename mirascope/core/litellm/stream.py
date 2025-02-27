"""The `LiteLLMStream` class for convenience around streaming LLM calls.

usage docs: learn/streams.md
"""

from collections.abc import AsyncGenerator, Generator

from litellm import Choices, Message
from litellm.cost_calculator import completion_cost
from litellm.types.utils import ModelResponse

from ..base.types import CostMetadata
from ..openai import OpenAIStream, OpenAITool
from .call_response import LiteLLMCallResponse
from .call_response_chunk import LiteLLMCallResponseChunk


class LiteLLMStream(OpenAIStream):
    """A simple wrapper around `OpenAIStream`.

    Everything is the same except updates to the `construct_call_response` method and
    the `cost` property so that cost is properly calculated using LiteLLM's cost
    calculation method. This ensures cost calculation works for non-OpenAI models.
    """

    _provider = "litellm"

    def __iter__(
        self,
    ) -> Generator[tuple[LiteLLMCallResponseChunk, OpenAITool | None], None, None]:
        yield from super().__iter__()  # pyright: ignore [reportReturnType]

    def __aiter__(
        self,
    ) -> AsyncGenerator[tuple[LiteLLMCallResponseChunk, OpenAITool | None], None]:
        return super().__aiter__()  # pyright: ignore [reportReturnType] # pragma: no cover

    @property
    def cost_metadata(self) -> CostMetadata:
        """Returns metadata needed for cost calculation."""
        response = self.construct_call_response()
        return CostMetadata(
            cost=response.cost,
        )

    def construct_call_response(self) -> LiteLLMCallResponse:
        openai_call_response = super().construct_call_response()
        openai_response = openai_call_response.response
        model_response = ModelResponse(
            id=openai_response.id,
            choices=[
                Choices(
                    finish_reason=choice.finish_reason,
                    index=choice.index,
                    message=Message(**choice.message.model_dump()),
                    logprobs=choice.logprobs,
                )
                for choice in openai_response.choices
            ],
            created=openai_response.created,
            model=openai_response.model,
            object=openai_response.object,
            system_fingerprint=openai_response.system_fingerprint,
            usage=openai_response.usage.model_dump() if openai_response.usage else None,
        )
        model_response._hidden_params["response_cost"] = completion_cost(
            model=self.model,
            messages=openai_call_response.messages,
            completion=openai_call_response.content,
        )
        response = LiteLLMCallResponse(
            metadata=openai_call_response.metadata,
            response=model_response,  # pyright: ignore [reportArgumentType]
            tool_types=openai_call_response.tool_types,
            prompt_template=openai_call_response.prompt_template,
            fn_args=openai_call_response.fn_args,
            dynamic_config=openai_call_response.dynamic_config,
            messages=openai_call_response.messages,
            call_params=openai_call_response.call_params,
            call_kwargs=openai_call_response.call_kwargs,
            user_message_param=openai_call_response.user_message_param,
            start_time=openai_call_response.start_time,
            end_time=openai_call_response.end_time,
        )
        response._model = self.model
        return response
