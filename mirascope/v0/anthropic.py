"""OpenAI modules for the v0 look-alike implementation."""

from typing import ClassVar, Generic, Literal, TypeVar

from anthropic.types.completion_create_params import Metadata
from pydantic import ConfigDict

from ..core.anthropic import (
    AnthropicCallResponse,
    AnthropicCallResponseChunk,
    AnthropicTool,
    anthropic_call,
)
from .base import BaseCall, BaseCallParams, BaseExtractor, ExtractedType


class AnthropicCallParams(BaseCallParams):
    """The parameters to use when calling d Claud API with a prompt."""

    max_tokens: int = 1000
    model: str = "claude-3-haiku-20240307"
    metadata: Metadata | None = None
    stop_sequences: list[str] | None = None
    system: str | None = None
    temperature: float | None = None
    top_k: int | None = None
    top_p: float | None = None

    response_format: Literal["json"] | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")


class AnthropicCall(
    BaseCall[AnthropicCallResponse, AnthropicCallResponseChunk, AnthropicTool]
):
    call_params: ClassVar[BaseCallParams] = AnthropicCallParams(
        model="claude-3-5-sonnet-20240620"
    )

    _decorator = anthropic_call
    _provider = "anthropic"


T = TypeVar("T", bound=ExtractedType)


class AnthropicExtractor(BaseExtractor[T], Generic[T]):
    call_params: ClassVar[BaseCallParams] = AnthropicCallParams(
        model="claude-3-5-sonnet-20240620"
    )

    _decorator = anthropic_call
    _provider = "anthropic"
