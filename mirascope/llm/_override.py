"""Overrides the provider-specific call with the specified provider."""

from __future__ import annotations

from collections.abc import AsyncIterable, Awaitable, Callable, Iterable
from enum import Enum
from functools import wraps
from typing import TYPE_CHECKING, Any, Literal, ParamSpec, TypeVar, overload

from pydantic import BaseModel

from ..core.base import BaseTool, BaseType, CommonCallParams
from ..core.base._utils import fn_is_async
from ..core.base.stream_config import StreamConfig
from ..core.base.types import LocalProvider, Provider
from ._context import _context
from .call_response import CallResponse
from .stream import Stream

if TYPE_CHECKING:
    from ..core.anthropic import AnthropicCallParams
    from ..core.azure import AzureCallParams
    from ..core.bedrock import BedrockCallParams
    from ..core.cohere import CohereCallParams
    from ..core.gemini import GeminiCallParams
    from ..core.google import GoogleCallParams
    from ..core.groq import GroqCallParams
    from ..core.litellm import LiteLLMCallParams
    from ..core.mistral import MistralCallParams
    from ..core.openai import OpenAICallParams
    from ..core.vertex import VertexCallParams
    from ..core.xai import XAICallParams
else:
    AnthropicCallParams = AzureCallParams = BedrockCallParams = CohereCallParams = (
        GeminiCallParams
    ) = GoogleCallParams = GroqCallParams = LiteLLMCallParams = MistralCallParams = (
        OpenAICallParams
    ) = VertexCallParams = XAICallParams = None


_P = ParamSpec("_P")
_R = TypeVar("_R")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType | Enum)
_ParsedOutputT = TypeVar("_ParsedOutputT")


### PASSTHROUGH ###
# Anthropic passthrough
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["anthropic"],
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AnthropicCallParams | None = None,
) -> Callable[_P, Awaitable[_R]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["anthropic"],
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AnthropicCallParams | None = None,
) -> Callable[_P, _R]: ...


# Azure passthrough
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["azure"],
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AzureCallParams | None = None,
) -> Callable[_P, Awaitable[_R]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["azure"],
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AzureCallParams | None = None,
) -> Callable[_P, _R]: ...


# Bedrock passthrough
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["bedrock"],
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | BedrockCallParams | None = None,
) -> Callable[_P, Awaitable[_R]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["bedrock"],
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | BedrockCallParams | None = None,
) -> Callable[_P, _R]: ...


# Cohere passthrough
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["cohere"],
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | CohereCallParams | None = None,
) -> Callable[_P, Awaitable[_R]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["cohere"],
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | CohereCallParams | None = None,
) -> Callable[_P, _R]: ...


# Gemini passthrough
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["gemini"],
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GeminiCallParams | None = None,
) -> Callable[_P, Awaitable[_R]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["gemini"],
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GeminiCallParams | None = None,
) -> Callable[_P, _R]: ...


# Google passthrough
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["google"],
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GoogleCallParams | None = None,
) -> Callable[_P, Awaitable[_R]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["google"],
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GoogleCallParams | None = None,
) -> Callable[_P, _R]: ...


# Groq passthrough
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["groq"],
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GroqCallParams | None = None,
) -> Callable[_P, Awaitable[_R]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["groq"],
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GroqCallParams | None = None,
) -> Callable[_P, _R]: ...


# LiteLLM passthrough
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["litellm"],
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | LiteLLMCallParams | None = None,
) -> Callable[_P, Awaitable[_R]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["litellm"],
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | LiteLLMCallParams | None = None,
) -> Callable[_P, _R]: ...


# Mistral passthrough
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["mistral"],
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | MistralCallParams | None = None,
) -> Callable[_P, Awaitable[_R]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["mistral"],
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | MistralCallParams | None = None,
) -> Callable[_P, _R]: ...


# OpenAI passthrough
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["openai"] | LocalProvider,
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | OpenAICallParams | None = None,
) -> Callable[_P, Awaitable[_R]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["openai"] | LocalProvider,
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | OpenAICallParams | None = None,
) -> Callable[_P, _R]: ...


# Vertex passthrough
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["vertex"],
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | VertexCallParams | None = None,
) -> Callable[_P, Awaitable[_R]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["vertex"],
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | VertexCallParams | None = None,
) -> Callable[_P, _R]: ...


# xAI passthrough
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["xai"],
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | XAICallParams | None = None,
) -> Callable[_P, Awaitable[_R]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["xai"],
    model: str,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | XAICallParams | None = None,
) -> Callable[_P, _R]: ...


# Generic passthrough
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: None = None,
    model: None = None,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | None = None,
) -> Callable[_P, Awaitable[_R]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: None = None,
    model: None = None,
    stream: None = None,
    tools: None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | None = None,
) -> Callable[_P, _R]: ...


### CallResponse ###
# Anthropic CallResponse
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["anthropic"],
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AnthropicCallParams | None = None,
) -> Callable[_P, Awaitable[CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["anthropic"],
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AnthropicCallParams | None = None,
) -> Callable[_P, CallResponse]: ...


# Azure CallResponse
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["azure"],
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AzureCallParams | None = None,
) -> Callable[_P, Awaitable[CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["azure"],
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AzureCallParams | None = None,
) -> Callable[_P, CallResponse]: ...


# Bedrock CallResponse
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["bedrock"],
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | BedrockCallParams | None = None,
) -> Callable[_P, Awaitable[CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["bedrock"],
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | BedrockCallParams | None = None,
) -> Callable[_P, CallResponse]: ...


# Cohere CallResponse
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["cohere"],
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | CohereCallParams | None = None,
) -> Callable[_P, Awaitable[CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["cohere"],
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | CohereCallParams | None = None,
) -> Callable[_P, CallResponse]: ...


# Gemini CallResponse
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["gemini"],
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GeminiCallParams | None = None,
) -> Callable[_P, Awaitable[CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["gemini"],
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GeminiCallParams | None = None,
) -> Callable[_P, CallResponse]: ...


# Google CallResponse
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["google"],
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GoogleCallParams | None = None,
) -> Callable[_P, Awaitable[CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["google"],
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GoogleCallParams | None = None,
) -> Callable[_P, CallResponse]: ...


# Groq CallResponse
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["groq"],
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GroqCallParams | None = None,
) -> Callable[_P, Awaitable[CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["groq"],
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GroqCallParams | None = None,
) -> Callable[_P, CallResponse]: ...


# LiteLLM CallResponse
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["litellm"],
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | LiteLLMCallParams | None = None,
) -> Callable[_P, Awaitable[CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["litellm"],
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | LiteLLMCallParams | None = None,
) -> Callable[_P, CallResponse]: ...


# Mistral CallResponse
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["mistral"],
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | MistralCallParams | None = None,
) -> Callable[_P, Awaitable[CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["mistral"],
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | MistralCallParams | None = None,
) -> Callable[_P, CallResponse]: ...


# OpenAI CallResponse
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["openai"] | LocalProvider,
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | OpenAICallParams | None = None,
) -> Callable[_P, Awaitable[CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["openai"] | LocalProvider,
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | OpenAICallParams | None = None,
) -> Callable[_P, CallResponse]: ...


# Vertex CallResponse
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["vertex"],
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | VertexCallParams | None = None,
) -> Callable[_P, Awaitable[CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["vertex"],
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | VertexCallParams | None = None,
) -> Callable[_P, CallResponse]: ...


# XAI CallResponse
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["xai"],
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | XAICallParams | None = None,
) -> Callable[_P, Awaitable[CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["xai"],
    model: str,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | XAICallParams | None = None,
) -> Callable[_P, CallResponse]: ...


# Generic CallResponse
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: None = None,
    model: str | None = None,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | None = None,
) -> Callable[_P, Awaitable[CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: None = None,
    model: str | None = None,
    stream: Literal[False],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | None = None,
) -> Callable[_P, CallResponse]: ...


### Stream ###
# Anthropic Stream
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["anthropic"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AnthropicCallParams | None = None,
) -> Callable[_P, Awaitable[Stream]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["anthropic"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AnthropicCallParams | None = None,
) -> Callable[_P, Stream]: ...


# Azure Stream
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["azure"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AzureCallParams | None = None,
) -> Callable[_P, Awaitable[Stream]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["azure"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AzureCallParams | None = None,
) -> Callable[_P, Stream]: ...


# Bedrock Stream
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["bedrock"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | BedrockCallParams | None = None,
) -> Callable[_P, Awaitable[Stream]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["bedrock"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | BedrockCallParams | None = None,
) -> Callable[_P, Stream]: ...


# Cohere Stream
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["cohere"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | CohereCallParams | None = None,
) -> Callable[_P, Awaitable[Stream]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["cohere"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | CohereCallParams | None = None,
) -> Callable[_P, Stream]: ...


# Gemini Stream
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["gemini"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GeminiCallParams | None = None,
) -> Callable[_P, Awaitable[Stream]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["gemini"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GeminiCallParams | None = None,
) -> Callable[_P, Stream]: ...


# Google Stream
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["google"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GoogleCallParams | None = None,
) -> Callable[_P, Awaitable[Stream]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["google"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GoogleCallParams | None = None,
) -> Callable[_P, Stream]: ...


# Groq Stream
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["groq"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GroqCallParams | None = None,
) -> Callable[_P, Awaitable[Stream]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["groq"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GroqCallParams | None = None,
) -> Callable[_P, Stream]: ...


# LiteLLM Stream
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["litellm"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | LiteLLMCallParams | None = None,
) -> Callable[_P, Awaitable[Stream]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["litellm"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | LiteLLMCallParams | None = None,
) -> Callable[_P, Stream]: ...


# Mistral Stream
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["mistral"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | MistralCallParams | None = None,
) -> Callable[_P, Awaitable[Stream]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["mistral"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | MistralCallParams | None = None,
) -> Callable[_P, Stream]: ...


# OpenAI Stream
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["openai"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | OpenAICallParams | None = None,
) -> Callable[_P, Awaitable[Stream]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["openai"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | OpenAICallParams | None = None,
) -> Callable[_P, Stream]: ...


# Vertex Stream
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["vertex"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | VertexCallParams | None = None,
) -> Callable[_P, Awaitable[Stream]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["vertex"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | VertexCallParams | None = None,
) -> Callable[_P, Stream]: ...


# XAI Stream
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["xai"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | XAICallParams | None = None,
) -> Callable[_P, Awaitable[Stream]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["xai"],
    model: str,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | XAICallParams | None = None,
) -> Callable[_P, Stream]: ...


# Generic Stream (for when provider is None or a LocalProvider)
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: LocalProvider | None = None,
    model: str | None = None,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | None = None,
) -> Callable[_P, Awaitable[Stream]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: LocalProvider | None = None,
    model: str | None = None,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | None = None,
) -> Callable[_P, Stream]: ...


### _ResponseModelT ###
# Anthropic _ResponseModelT
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["anthropic"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AnthropicCallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["anthropic"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AnthropicCallParams | None = None,
) -> Callable[_P, _ResponseModelT]: ...


# Azure _ResponseModelT
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["azure"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AzureCallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["azure"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AzureCallParams | None = None,
) -> Callable[_P, _ResponseModelT]: ...


# Bedrock _ResponseModelT
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["bedrock"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | BedrockCallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["bedrock"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | BedrockCallParams | None = None,
) -> Callable[_P, _ResponseModelT]: ...


# Cohere _ResponseModelT
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["cohere"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | CohereCallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["cohere"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | CohereCallParams | None = None,
) -> Callable[_P, _ResponseModelT]: ...


# Gemini _ResponseModelT
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["gemini"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GeminiCallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["gemini"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GeminiCallParams | None = None,
) -> Callable[_P, _ResponseModelT]: ...


# Google _ResponseModelT
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["google"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GoogleCallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["google"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GoogleCallParams | None = None,
) -> Callable[_P, _ResponseModelT]: ...


# Groq _ResponseModelT
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["groq"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GroqCallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["groq"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GroqCallParams | None = None,
) -> Callable[_P, _ResponseModelT]: ...


# LiteLLM _ResponseModelT
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["litellm"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | LiteLLMCallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["litellm"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | LiteLLMCallParams | None = None,
) -> Callable[_P, _ResponseModelT]: ...


# Mistral _ResponseModelT
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["mistral"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | MistralCallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["mistral"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | MistralCallParams | None = None,
) -> Callable[_P, _ResponseModelT]: ...


# OpenAI _ResponseModelT
@overload
def override(  # pyright: ignore [reportOverlappingOverload]
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["openai"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | OpenAICallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["openai"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | OpenAICallParams | None = None,
) -> Callable[_P, _ResponseModelT]: ...


# Vertex _ResponseModelT
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["vertex"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | VertexCallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["vertex"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | VertexCallParams | None = None,
) -> Callable[_P, _ResponseModelT]: ...


# XAI _ResponseModelT
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["xai"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | XAICallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["xai"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | XAICallParams | None = None,
) -> Callable[_P, _ResponseModelT]: ...


# Generic _ResponseModelT (for when provider is None or a LocalProvider)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: LocalProvider | None = None,
    model: str | None = None,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: LocalProvider | None = None,
    model: str | None = None,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | None = None,
) -> Callable[_P, _ResponseModelT]: ...


### _ParsedOutputT ###
# Anthropic _ParsedOutputT
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["anthropic"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AnthropicCallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["anthropic"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AnthropicCallParams | None = None,
) -> Callable[_P, _ParsedOutputT]: ...


# Azure _ParsedOutputT
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["azure"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AzureCallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["azure"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AzureCallParams | None = None,
) -> Callable[_P, _ParsedOutputT]: ...


# Bedrock _ParsedOutputT
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["bedrock"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | BedrockCallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["bedrock"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | BedrockCallParams | None = None,
) -> Callable[_P, _ParsedOutputT]: ...


# Cohere _ParsedOutputT
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["cohere"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | CohereCallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["cohere"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | CohereCallParams | None = None,
) -> Callable[_P, _ParsedOutputT]: ...


# Gemini _ParsedOutputT
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["gemini"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GeminiCallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["gemini"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GeminiCallParams | None = None,
) -> Callable[_P, _ParsedOutputT]: ...


# Google _ParsedOutputT
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["google"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GoogleCallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["google"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GoogleCallParams | None = None,
) -> Callable[_P, _ParsedOutputT]: ...


# Groq _ParsedOutputT
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["groq"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GroqCallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["groq"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GroqCallParams | None = None,
) -> Callable[_P, _ParsedOutputT]: ...


# LiteLLM _ParsedOutputT
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["litellm"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | LiteLLMCallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["litellm"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | LiteLLMCallParams | None = None,
) -> Callable[_P, _ParsedOutputT]: ...


# Mistral _ParsedOutputT
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["mistral"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | MistralCallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["mistral"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | MistralCallParams | None = None,
) -> Callable[_P, _ParsedOutputT]: ...


# OpenAI _ParsedOutputT
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["openai"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | OpenAICallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["openai"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | OpenAICallParams | None = None,
) -> Callable[_P, _ParsedOutputT]: ...


# Vertex _ParsedOutputT
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["vertex"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | VertexCallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["vertex"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | VertexCallParams | None = None,
) -> Callable[_P, _ParsedOutputT]: ...


# XAI _ParsedOutputT
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["xai"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | XAICallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["xai"],
    model: str,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | XAICallParams | None = None,
) -> Callable[_P, _ParsedOutputT]: ...


# Generic _ParsedOutputT (for when provider is None or a LocalProvider)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: LocalProvider | None = None,
    model: str | None = None,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: LocalProvider | None = None,
    model: str | None = None,
    stream: Literal[None, False] = None,
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | None = None,
) -> Callable[_P, _ParsedOutputT]: ...


### Async/Iterable[_ResponseModelT] ###
# Anthropic Async/Iterable[_ResponseModelT]
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["anthropic"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AnthropicCallParams | None = None,
) -> Callable[_P, Awaitable[AsyncIterable[_ResponseModelT]]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["anthropic"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AnthropicCallParams | None = None,
) -> Callable[_P, Iterable[_ResponseModelT]]: ...


# Azure Async/Iterable[_ResponseModelT]
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["azure"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AzureCallParams | None = None,
) -> Callable[_P, Awaitable[AsyncIterable[_ResponseModelT]]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["azure"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AzureCallParams | None = None,
) -> Callable[_P, Iterable[_ResponseModelT]]: ...


# Bedrock Async/Iterable[_ResponseModelT]
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["bedrock"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | BedrockCallParams | None = None,
) -> Callable[_P, Awaitable[AsyncIterable[_ResponseModelT]]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["bedrock"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | BedrockCallParams | None = None,
) -> Callable[_P, Iterable[_ResponseModelT]]: ...


# Cohere Async/Iterable[_ResponseModelT]
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["cohere"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | CohereCallParams | None = None,
) -> Callable[_P, Awaitable[AsyncIterable[_ResponseModelT]]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["cohere"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | CohereCallParams | None = None,
) -> Callable[_P, Iterable[_ResponseModelT]]: ...


# Gemini Async/Iterable[_ResponseModelT]
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["gemini"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GeminiCallParams | None = None,
) -> Callable[_P, Awaitable[AsyncIterable[_ResponseModelT]]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["gemini"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GeminiCallParams | None = None,
) -> Callable[_P, Iterable[_ResponseModelT]]: ...


# Google Async/Iterable[_ResponseModelT]
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["google"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GoogleCallParams | None = None,
) -> Callable[_P, Awaitable[AsyncIterable[_ResponseModelT]]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["google"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GoogleCallParams | None = None,
) -> Callable[_P, Iterable[_ResponseModelT]]: ...


# Groq Async/Iterable[_ResponseModelT]
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["groq"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GroqCallParams | None = None,
) -> Callable[_P, Awaitable[AsyncIterable[_ResponseModelT]]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["groq"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GroqCallParams | None = None,
) -> Callable[_P, Iterable[_ResponseModelT]]: ...


# LiteLLM Async/Iterable[_ResponseModelT]
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["litellm"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | LiteLLMCallParams | None = None,
) -> Callable[_P, Awaitable[AsyncIterable[_ResponseModelT]]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["litellm"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | LiteLLMCallParams | None = None,
) -> Callable[_P, Iterable[_ResponseModelT]]: ...


# Mistral Async/Iterable[_ResponseModelT]
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["mistral"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | MistralCallParams | None = None,
) -> Callable[_P, Awaitable[AsyncIterable[_ResponseModelT]]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["mistral"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | MistralCallParams | None = None,
) -> Callable[_P, Iterable[_ResponseModelT]]: ...


# OpenAI Async/Iterable[_ResponseModelT]
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["openai"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | OpenAICallParams | None = None,
) -> Callable[_P, Awaitable[AsyncIterable[_ResponseModelT]]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["openai"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | OpenAICallParams | None = None,
) -> Callable[_P, Iterable[_ResponseModelT]]: ...


# Vertex Async/Iterable[_ResponseModelT]
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["vertex"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | VertexCallParams | None = None,
) -> Callable[_P, Awaitable[AsyncIterable[_ResponseModelT]]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["vertex"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | VertexCallParams | None = None,
) -> Callable[_P, Iterable[_ResponseModelT]]: ...


# XAI Async/Iterable[_ResponseModelT]
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["xai"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | XAICallParams | None = None,
) -> Callable[_P, Awaitable[AsyncIterable[_ResponseModelT]]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["xai"],
    model: str,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | XAICallParams | None = None,
) -> Callable[_P, Iterable[_ResponseModelT]]: ...


# Generic Async/Iterable[_ResponseModelT] (for when provider is None or a LocalProvider)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: LocalProvider | None = None,
    model: str | None = None,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | None = None,
) -> Callable[_P, Awaitable[AsyncIterable[_ResponseModelT]]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: LocalProvider | None = None,
    model: str | None = None,
    stream: Literal[True],
    tools: Literal[None] = None,
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | None = None,
) -> Callable[_P, Iterable[_ResponseModelT]]: ...


### (_ResponseModelT | CallResponse) ###
# Anthropic (_ResponseModelT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["anthropic"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AnthropicCallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["anthropic"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AnthropicCallParams | None = None,
) -> Callable[_P, _ResponseModelT | CallResponse]: ...


# Azure (_ResponseModelT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["azure"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AzureCallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["azure"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AzureCallParams | None = None,
) -> Callable[_P, _ResponseModelT | CallResponse]: ...


# Bedrock (_ResponseModelT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["bedrock"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | BedrockCallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["bedrock"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | BedrockCallParams | None = None,
) -> Callable[_P, _ResponseModelT | CallResponse]: ...


# Cohere (_ResponseModelT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["cohere"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | CohereCallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["cohere"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | CohereCallParams | None = None,
) -> Callable[_P, _ResponseModelT | CallResponse]: ...


# Gemini (_ResponseModelT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["gemini"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GeminiCallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["gemini"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GeminiCallParams | None = None,
) -> Callable[_P, _ResponseModelT | CallResponse]: ...


# Google (_ResponseModelT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["google"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GoogleCallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["google"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GoogleCallParams | None = None,
) -> Callable[_P, _ResponseModelT | CallResponse]: ...


# Groq (_ResponseModelT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["groq"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GroqCallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["groq"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GroqCallParams | None = None,
) -> Callable[_P, _ResponseModelT | CallResponse]: ...


# LiteLLM (_ResponseModelT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["litellm"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | LiteLLMCallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["litellm"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | LiteLLMCallParams | None = None,
) -> Callable[_P, _ResponseModelT | CallResponse]: ...


# Mistral (_ResponseModelT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["mistral"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | MistralCallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["mistral"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | MistralCallParams | None = None,
) -> Callable[_P, _ResponseModelT | CallResponse]: ...


# OpenAI (_ResponseModelT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["openai"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | OpenAICallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["openai"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | OpenAICallParams | None = None,
) -> Callable[_P, _ResponseModelT | CallResponse]: ...


# Vertex (_ResponseModelT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["vertex"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | VertexCallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["vertex"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | VertexCallParams | None = None,
) -> Callable[_P, _ResponseModelT | CallResponse]: ...


# XAI (_ResponseModelT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["xai"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | XAICallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["xai"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | XAICallParams | None = None,
) -> Callable[_P, _ResponseModelT | CallResponse]: ...


# Generic (_ResponseModelT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: LocalProvider | None = None,
    model: str | None = None,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | None = None,
) -> Callable[_P, Awaitable[_ResponseModelT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: LocalProvider | None = None,
    model: str | None = None,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Literal[None] = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | None = None,
) -> Callable[_P, _ResponseModelT | CallResponse]: ...


### (_ParsedOutputT | CallResponse) ###
# Anthropic (_ParsedOutputT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["anthropic"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AnthropicCallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["anthropic"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AnthropicCallParams | None = None,
) -> Callable[_P, _ParsedOutputT | CallResponse]: ...


# Azure (_ParsedOutputT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["azure"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AzureCallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["azure"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AzureCallParams | None = None,
) -> Callable[_P, _ParsedOutputT | CallResponse]: ...


# Bedrock (_ParsedOutputT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["bedrock"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | BedrockCallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["bedrock"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | BedrockCallParams | None = None,
) -> Callable[_P, _ParsedOutputT | CallResponse]: ...


# Cohere (_ParsedOutputT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["cohere"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | CohereCallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["cohere"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | CohereCallParams | None = None,
) -> Callable[_P, _ParsedOutputT | CallResponse]: ...


# Gemini (_ParsedOutputT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["gemini"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GeminiCallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["gemini"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GeminiCallParams | None = None,
) -> Callable[_P, _ParsedOutputT | CallResponse]: ...


# Google (_ParsedOutputT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["google"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GoogleCallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["google"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GoogleCallParams | None = None,
) -> Callable[_P, _ParsedOutputT | CallResponse]: ...


# Groq (_ParsedOutputT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["groq"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GroqCallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["groq"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GroqCallParams | None = None,
) -> Callable[_P, _ParsedOutputT | CallResponse]: ...


# LiteLLM (_ParsedOutputT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["litellm"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | LiteLLMCallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["litellm"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | LiteLLMCallParams | None = None,
) -> Callable[_P, _ParsedOutputT | CallResponse]: ...


# Mistral (_ParsedOutputT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["mistral"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | MistralCallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["mistral"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | MistralCallParams | None = None,
) -> Callable[_P, _ParsedOutputT | CallResponse]: ...


# OpenAI (_ParsedOutputT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["openai"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | OpenAICallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["openai"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | OpenAICallParams | None = None,
) -> Callable[_P, _ParsedOutputT | CallResponse]: ...


# Vertex (_ParsedOutputT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["vertex"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | VertexCallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["vertex"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | VertexCallParams | None = None,
) -> Callable[_P, _ParsedOutputT | CallResponse]: ...


# XAI (_ParsedOutputT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: Literal["xai"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | XAICallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["xai"],
    model: str,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | XAICallParams | None = None,
) -> Callable[_P, _ParsedOutputT | CallResponse]: ...


# Generic (_ParsedOutputT | CallResponse)
@overload
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]],
    *,
    provider: LocalProvider | None = None,
    model: str | None = None,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | None = None,
) -> Callable[_P, Awaitable[_ParsedOutputT | CallResponse]]: ...


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: LocalProvider | None = None,
    model: str | None = None,
    stream: Literal[None, False] = None,
    tools: list[type[BaseTool] | Callable],
    response_model: type[_ResponseModelT],
    output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | None = None,
) -> Callable[_P, _ParsedOutputT | CallResponse]: ...


### ORIGINAL DEFINITION ###
def override(
    provider_agnostic_call: Callable[_P, Awaitable[_R]] | Callable[_P, _R],
    *,
    provider: Provider | LocalProvider | None = None,
    model: str | None = None,
    stream: bool | StreamConfig | None = None,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT] | None = None,
    json_mode: bool | None = None,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams
    | AnthropicCallParams
    | AzureCallParams
    | BedrockCallParams
    | CohereCallParams
    | GeminiCallParams
    | GoogleCallParams
    | GroqCallParams
    | MistralCallParams
    | OpenAICallParams
    | VertexCallParams
    | XAICallParams
    | None = None,
) -> Callable[
    _P,
    Awaitable[_R]
    | Awaitable[CallResponse]
    | Awaitable[Stream]
    | Awaitable[_ResponseModelT]
    | Awaitable[_ParsedOutputT]
    | Awaitable[AsyncIterable[_ResponseModelT]]
    | Awaitable[_ResponseModelT | CallResponse]
    | Awaitable[_ParsedOutputT | CallResponse]
    | _R
    | CallResponse
    | Stream
    | _ResponseModelT
    | _ParsedOutputT
    | Iterable[_ResponseModelT]
    | (_ResponseModelT | CallResponse)
    | (_ParsedOutputT | CallResponse),
]:
    """Overrides the provider-specific call with the specified provider.

    This function creates a new function that wraps the original function
    and temporarily sets a context with the specified overrides when called.
    It supports both setting overrides (provider, model, client, call_params)
    and structural overrides (stream, tools, response_model, output_parser).

    Example:
        ```python
        @llm.call(provider="openai", model="gpt-4o-mini")
        def recommend_book(genre: str) -> str:
            return f"Recommend a {genre} book"

        # Override the model for all calls to the function
        recommend_claude_book = override(
            recommend_book,
            provider="anthropic",
            model="claude-3-5-sonnet-20240620"
        )
        response = recommend_claude_book("fantasy")  # Uses claude-3-5-sonnet

        # Override to use streaming
        stream_book = override(
            recommend_book,
            stream=True
        )
        stream = stream_book("fantasy")  # Returns a Stream object
        ```

    Args:
        provider_agnostic_call: The provider-agnostic call to override.
        provider: The provider to override with.
        model: The model to override with.
        stream: Whether to stream the response.
        tools: The tools to use for the LLM API call.
        response_model: The response model to structure the response into.
        output_parser: A function to parse the response.
        json_mode: Whether to use JSON mode.
        client: The client to override with.
        call_params: The call params to override with.

    Returns:
        The overridden function with appropriate return type.
    """
    if (provider and not model) or (model and not provider):
        raise ValueError(
            "Provider and model must both be overridden if either is overridden."
        )

    if fn_is_async(provider_agnostic_call):

        @wraps(provider_agnostic_call)
        async def inner_async(
            *args: _P.args, **kwargs: _P.kwargs
        ) -> (
            Awaitable[_R]
            | Awaitable[CallResponse]
            | Awaitable[Stream]
            | Awaitable[_ResponseModelT]
            | Awaitable[_ParsedOutputT]
            | Awaitable[AsyncIterable[_ResponseModelT]]
            | Awaitable[_ResponseModelT | CallResponse]
            | Awaitable[_ParsedOutputT | CallResponse]
        ):
            # THIS IS NOT TYPE SAFE BUT WILL WORK SO WE IGNORE
            with _context(
                provider=provider,
                model=model,
                stream=stream,
                tools=tools,
                response_model=response_model,
                output_parser=output_parser,
                json_mode=json_mode,
                client=client,
                call_params=call_params,
            ):
                return await provider_agnostic_call(*args, **kwargs)  # pyright: ignore [reportReturnType]

        return inner_async  # pyright: ignore [reportReturnType]
    else:

        @wraps(provider_agnostic_call)
        def inner(
            *args: _P.args, **kwargs: _P.kwargs
        ) -> (
            _R
            | CallResponse
            | Stream
            | _ResponseModelT
            | _ParsedOutputT
            | Iterable[_ResponseModelT]
            | (_ResponseModelT | CallResponse)
            | (_ParsedOutputT | CallResponse)
        ):
            # THIS IS NOT TYPE SAFE BUT WILL WORK SO WE IGNORE
            with _context(
                provider=provider,
                model=model,
                stream=stream,
                tools=tools,
                response_model=response_model,
                output_parser=output_parser,
                json_mode=json_mode,
                client=client,
                call_params=call_params,
            ):
                return provider_agnostic_call(*args, **kwargs)

        return inner
