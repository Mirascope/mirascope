"""Overrides the provider-specific call with the specified provider."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Literal, ParamSpec, TypeVar, overload

from mirascope.core.base import CommonCallParams
from mirascope.llm._protocols import Provider
from mirascope.llm.llm_call import _call

if TYPE_CHECKING:
    from mirascope.core.anthropic import AnthropicCallParams
    from mirascope.core.azure import AzureCallParams
    from mirascope.core.bedrock import BedrockCallParams
    from mirascope.core.cohere import CohereCallParams
    from mirascope.core.gemini import GeminiCallParams
    from mirascope.core.groq import GroqCallParams
    from mirascope.core.litellm import LiteLLMCallParams
    from mirascope.core.mistral import MistralCallParams
    from mirascope.core.openai import OpenAICallParams
    from mirascope.core.vertex import VertexCallParams
else:
    AnthropicCallParams = AzureCallParams = BedrockCallParams = CohereCallParams = (
        GeminiCallParams
    ) = GroqCallParams = LiteLLMCallParams = MistralCallParams = OpenAICallParams = (
        VertexCallParams
    ) = None


_P = ParamSpec("_P")
_R = TypeVar("_R")


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["anthropic"],
    model: str,
    call_params: CommonCallParams | AnthropicCallParams | None = None,
    client: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]: ...
@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["azure"],
    model: str,
    call_params: CommonCallParams | AzureCallParams | None = None,
    client: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]: ...
@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["bedrock"],
    model: str,
    call_params: CommonCallParams | BedrockCallParams | None = None,
    client: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]: ...
@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["cohere"],
    model: str,
    call_params: CommonCallParams | CohereCallParams | None = None,
    client: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]: ...
@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["gemini"],
    model: str,
    call_params: CommonCallParams | GeminiCallParams | None = None,
    client: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]: ...
@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["groq"],
    model: str,
    call_params: CommonCallParams | GroqCallParams | None = None,
    client: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]: ...
@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["mistral"],
    model: str,
    call_params: CommonCallParams | MistralCallParams | None = None,
    client: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]: ...
@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["openai"],
    model: str,
    call_params: CommonCallParams | OpenAICallParams | None = None,
    client: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]: ...
@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["litellm"],
    model: str,
    call_params: CommonCallParams | LiteLLMCallParams | None = None,
    client: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]: ...
@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Literal["vertex"],
    model: str,
    call_params: CommonCallParams | VertexCallParams | None = None,
    client: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]: ...
@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: None = None,
    model: None = None,
    call_params: CommonCallParams | None = None,
    client: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]: ...
@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Provider,
    model: str,
    call_params: CommonCallParams | None = None,
    client: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]: ...


def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider: Provider | None = None,
    model: str | None = None,
    call_params: CommonCallParams
    | AnthropicCallParams
    | GeminiCallParams
    | AzureCallParams
    | BedrockCallParams
    | CohereCallParams
    | GroqCallParams
    | MistralCallParams
    | OpenAICallParams
    | VertexCallParams
    | None = None,
    client: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]:
    """Overrides the provider-specific call with the specified provider.

    Args:
        provider_agnostic_call: The provider-agnostic call to override.
        provider: The provider to override with.
        model: The model to override with.
        call_params: The call params to override with.
        client: The client to override with.

    Returns:
        The overridden function.
    """
    _original_args = provider_agnostic_call._original_args  # pyright: ignore [reportFunctionMemberAccess]
    if provider is not None and not model and call_params is None and client is None:
        raise ValueError(
            "If provider is specified, model or call_params must also be specified."
        )

    return _call(  # pyright: ignore [reportReturnType]
        provider=provider or provider_agnostic_call._original_provider,  # pyright: ignore [reportFunctionMemberAccess]
        model=model or _original_args["model"],
        stream=_original_args["stream"],
        tools=_original_args["tools"],
        response_model=_original_args["response_model"],
        output_parser=_original_args["output_parser"],
        json_mode=_original_args["json_mode"],
        client=client or _original_args["client"],
        call_params=call_params or _original_args["call_params"],
    )(provider_agnostic_call._original_fn)  # pyright: ignore [reportFunctionMemberAccess]
