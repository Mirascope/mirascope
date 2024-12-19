from __future__ import annotations

from collections.abc import Awaitable, Callable
from enum import Enum
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    ParamSpec,
    TypeAlias,
    TypeVar,
)

from pydantic import BaseModel

from mirascope.core import BaseTool
from mirascope.core.base import (
    BaseCallResponse,
    BaseCallResponseChunk,
    BaseStream,
    BaseType,
    CommonCallParams,
)
from mirascope.core.base._utils import fn_is_async
from mirascope.core.base.stream_config import StreamConfig
from mirascope.llm.call_response import CallResponse
from mirascope.llm.stream import Stream

_P = ParamSpec("_P")
_R = TypeVar("_R", contravariant=True)
_ParsedOutputT = TypeVar("_ParsedOutputT")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType | Enum)
_CallResponseT = TypeVar("_CallResponseT", bound=BaseCallResponse)
_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", bound=BaseCallResponseChunk
)
_AsyncBaseDynamicConfigT = TypeVar("_AsyncBaseDynamicConfigT", contravariant=True)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", contravariant=True)


if TYPE_CHECKING:
    from mirascope.core.anthropic import AnthropicModels
    from mirascope.core.azure import AzureModels
    from mirascope.core.bedrock import BedrockModels
    from mirascope.core.cohere import CohereModels
    from mirascope.core.gemini import GeminiModels
    from mirascope.core.groq import GroqModels
    from mirascope.core.litellm import LiteLLMModels
    from mirascope.core.mistral import MistralModels
    from mirascope.core.openai import OpenAIModels
    from mirascope.core.vertex import VertexModels

    Models: TypeAlias = (
        AnthropicModels
        | AzureModels
        | BedrockModels
        | CohereModels
        | GeminiModels
        | GroqModels
        | LiteLLMModels
        | MistralModels
        | OpenAIModels
        | VertexModels
    )
else:
    _BaseToolT = None
    Models = None


def _get_provider_call(provider: str) -> Callable[..., Any]:
    if provider == "anthropic":
        from mirascope.core.anthropic import anthropic_call

        return anthropic_call
    elif provider == "azure":
        from mirascope.core.azure import azure_call

        return azure_call
    elif provider == "bedrock":
        from mirascope.core.bedrock import bedrock_call

        return bedrock_call
    elif provider == "cohere":
        from mirascope.core.cohere import cohere_call

        return cohere_call
    elif provider == "gemini":
        from mirascope.core.gemini import gemini_call

        return gemini_call
    elif provider == "groq":
        from mirascope.core.groq import groq_call

        return groq_call
    elif provider == "litellm":
        from mirascope.core.litellm import litellm_call

        return litellm_call
    elif provider == "mistral":
        from mirascope.core.mistral import mistral_call

        return mistral_call
    elif provider == "openai":
        from mirascope.core.openai import openai_call

        return openai_call
    elif provider == "vertex":
        from mirascope.core.vertex import vertex_call

        return vertex_call
    raise ValueError(f"Unsupported provider: {provider}")


def call(
    model: Models,
    stream: bool | StreamConfig = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[_CallResponseT], _ParsedOutputT]
    | Callable[[_BaseCallResponseChunkT], _ParsedOutputT]
    | Callable[[_ResponseModelT], _ParsedOutputT]
    | None = None,
    json_mode: bool = False,
    call_params: CommonCallParams | None = None,
) -> Callable[
    [Callable[_P, _R | Awaitable[_R]]],
    Callable[_P, CallResponse | Stream | Awaitable[CallResponse | Stream]],
]:
    provider, model_name = model.split(":", 1)
    provider_call = _get_provider_call(provider)

    def wrapper(
        fn: Callable[_P, _R | Awaitable[_R]],
    ) -> Callable[_P, CallResponse | Stream | Awaitable[CallResponse | Stream]]:
        decorated = provider_call(
            model=model_name,
            stream=stream,
            tools=tools,
            response_model=response_model,
            output_parser=output_parser,
            json_mode=json_mode,
            call_params=call_params,
        )(fn)

        @wraps(decorated)
        def inner(
            *args: _P.args, **kwargs: _P.kwargs
        ) -> CallResponse | Stream | Awaitable[CallResponse | Stream]:
            result = decorated(*args, **kwargs)
            if fn_is_async(decorated):

                async def async_wrapper() -> CallResponse | Stream:
                    final = await result
                    return _wrap_result(final)

                return async_wrapper()
            else:
                return _wrap_result(result)

        return inner

    def _wrap_result(result: BaseCallResponse | Stream) -> CallResponse | Stream:
        if isinstance(result, BaseCallResponse):
            return CallResponse(response=result)  # pyright: ignore [reportAbstractUsage]
        elif isinstance(result, BaseStream):
            return Stream(  # pyright: ignore [reportAbstractUsage]
                stream=result,
            )
        else:
            raise ValueError(f"Unsupported result type: {type(result)}")

    return wrapper
