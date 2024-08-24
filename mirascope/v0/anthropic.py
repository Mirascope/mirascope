"""OpenAI modules for the v0 look-alike implementation."""

from collections.abc import Callable
from typing import ClassVar, Generic, Literal, TypeVar

from anthropic import (
    Anthropic,
    AnthropicBedrock,
    AnthropicVertex,
    AsyncAnthropic,
    AsyncAnthropicBedrock,
    AsyncAnthropicVertex,
)
from anthropic._types import URL  # pyright: ignore [reportPrivateImportUsage]
from anthropic.types.completion_create_params import Metadata
from pydantic import ConfigDict

from ..core.anthropic import (
    AnthropicCallResponse,
    AnthropicCallResponseChunk,
    AnthropicTool,
    anthropic_call,
)
from .base import BaseCall, BaseCallParams, BaseExtractor, ExtractedType


def bedrock_client_wrapper(
    aws_secret_key: str | None = None,
    aws_access_key: str | None = None,
    aws_region: str | None = None,
    aws_session_token: str | None = None,
    base_url: str | URL | None = None,
) -> Callable[[Anthropic | AsyncAnthropic], AnthropicBedrock | AsyncAnthropicBedrock]:
    """Returns a client wrapper for using Anthropic models on AWS Bedrock."""

    def inner_wrapper(
        client: Anthropic | AsyncAnthropic,
    ) -> AnthropicBedrock | AsyncAnthropicBedrock:
        """Returns matching `AnthropicBedrock` or `AsyncAnthropicBedrock` client."""
        kwargs = {
            "aws_secret_key": aws_secret_key,
            "aws_access_key": aws_access_key,
            "aws_region": aws_region,
            "aws_session_token": aws_session_token,
            "base_url": base_url,
        }
        if isinstance(client, Anthropic):
            return AnthropicBedrock(**kwargs)
        return AsyncAnthropicBedrock(**kwargs)

    return inner_wrapper


def vertex_client_wrapper(
    project_id: str | None = None,
    region: str | None = None,
) -> Callable[[Anthropic | AsyncAnthropic], AnthropicVertex | AsyncAnthropicVertex]:
    """Returns a client wrapper for using Anthropic models on GCP Vertex."""

    def inner_wrapper(
        client: Anthropic | AsyncAnthropic,
    ) -> AnthropicVertex | AsyncAnthropicVertex:
        """Returns matching `AnthropicVertex` or `AsyncAnthropicVertex` client."""
        kwargs = {"project_id": project_id, "region": region}
        if isinstance(client, Anthropic):
            return AnthropicVertex(**kwargs)  # type: ignore
        return AsyncAnthropicVertex(**kwargs)  # type: ignore

    return inner_wrapper


class AnthropicCallParams(BaseCallParams[AnthropicTool]):
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
