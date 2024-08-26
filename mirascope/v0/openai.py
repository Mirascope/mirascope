"""OpenAI modules for the v0 look-alike implementation."""

from typing import ClassVar, Generic, TypeVar

from openai.types.chat import ChatCompletionToolChoiceOptionParam
from openai.types.chat.completion_create_params import ResponseFormat
from pydantic import ConfigDict

from ..core.openai import (
    OpenAICallResponse,
    OpenAICallResponseChunk,
    OpenAITool,
    openai_call,
)
from .base import BaseCall, BaseCallParams, BaseExtractor, ExtractedType


class OpenAICallParams(BaseCallParams):
    """The parameters to use when calling the OpenAI API."""

    model: str
    frequency_penalty: float | None = None
    logit_bias: dict[str, int] | None = None
    logprobs: bool | None = None
    max_tokens: int | None = None
    n: int | None = None
    presence_penalty: float | None = None
    response_format: ResponseFormat | None = None
    seed: int | None = None
    stop: str | list[str] | None = None
    temperature: float | None = None
    tool_choice: ChatCompletionToolChoiceOptionParam | None = None
    top_logprobs: int | None = None
    top_p: float | None = None
    user: str | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")


class OpenAICall(BaseCall[OpenAICallResponse, OpenAICallResponseChunk, OpenAITool]):
    call_params: ClassVar[BaseCallParams] = OpenAICallParams(model="gpt-4o-mini")

    _decorator = openai_call
    _provider = "openai"


T = TypeVar("T", bound=ExtractedType)


class OpenAIExtractor(BaseExtractor[T], Generic[T]):
    call_params: ClassVar[BaseCallParams] = OpenAICallParams(model="gpt-4o-mini")

    _decorator = openai_call
    _provider = "openai"
