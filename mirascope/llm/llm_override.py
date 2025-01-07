from collections.abc import Callable
from typing import Any, Literal, ParamSpec, TypeVar, overload

from mirascope.core.anthropic import AnthropicCallParams
from mirascope.core.azure import AzureCallParams
from mirascope.core.base import CommonCallParams
from mirascope.core.bedrock import BedrockCallParams
from mirascope.core.cohere import CohereCallParams
from mirascope.core.gemini import GeminiCallParams
from mirascope.core.groq import GroqCallParams
from mirascope.core.mistral import MistralCallParams
from mirascope.core.openai import OpenAICallParams
from mirascope.core.vertex import VertexCallParams
from mirascope.llm._protocols import Provider
from mirascope.llm.llm_call import _call

_P = ParamSpec("_P")
_R = TypeVar("_R")


@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider_override: Literal["anthropic"],
    model_override: str | None = None,
    call_params_override: CommonCallParams | AnthropicCallParams | None = None,
    client_override: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]: ...
@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider_override: Literal["azure"],
    model_override: str | None = None,
    call_params_override: CommonCallParams | AzureCallParams | None = None,
    client_override: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]: ...
@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider_override: Literal["bedrock"],
    model_override: str | None = None,
    call_params_override: CommonCallParams | BedrockCallParams | None = None,
    client_override: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]: ...
@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider_override: Literal["cohere"],
    model_override: str | None = None,
    call_params_override: CommonCallParams | CohereCallParams | None = None,
    client_override: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]: ...
@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider_override: Literal["gemini"],
    model_override: str | None = None,
    call_params_override: CommonCallParams | GeminiCallParams | None = None,
    client_override: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]: ...
@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider_override: Literal["groq"],
    model_override: str | None = None,
    call_params_override: CommonCallParams | GroqCallParams | None = None,
    client_override: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]: ...
@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider_override: Literal["mistral"],
    model_override: str | None = None,
    call_params_override: CommonCallParams | MistralCallParams | None = None,
    client_override: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]: ...
@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider_override: Literal["openai"],
    model_override: str | None = None,
    call_params_override: CommonCallParams | OpenAICallParams | None = None,
    client_override: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]: ...
@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider_override: Literal["litellm"],
    model_override: str | None = None,
    call_params_override: CommonCallParams | OpenAICallParams | None = None,
    client_override: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]: ...
@overload
def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider_override: Literal["vertex"],
    model_override: str | None = None,
    call_params_override: CommonCallParams | VertexCallParams | None = None,
    client_override: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]: ...


def override(
    provider_agnostic_call: Callable[_P, _R],
    *,
    provider_override: Provider | None = None,
    model_override: str | None = None,
    call_params_override: CommonCallParams
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
    client_override: Any = None,  # noqa: ANN401
) -> Callable[_P, _R]:
    """Overrides the provider-specific call with the specified provider.

    Args:
        provider_agnostic_call: The provider-agnostic call to override.
        provider_override: The provider to override with.
        model_override: The model to override with.
        call_params_override: The call params to override with.
        client_override: The client to override with.

    Returns:
        The overridden function.
    """
    _original_args = provider_agnostic_call._original_args  # pyright: ignore [reportFunctionMemberAccess]
    if (
        provider_override is not None
        and not model_override
        and call_params_override is None
        and client_override is None
    ):
        raise ValueError(
            "If provider_override is specified, model_override or call_params_override must also be specified."
        )

    return _call(
        provider=provider_override or provider_agnostic_call._original_provider,  # pyright: ignore [reportFunctionMemberAccess]
        model=model_override or _original_args["model"],
        stream=_original_args["stream"],
        tools=_original_args["tools"],
        response_model=_original_args["response_model"],
        output_parser=_original_args["output_parser"],
        json_mode=_original_args["json_mode"],
        client=client_override or _original_args["client"],
        call_params=call_params_override or _original_args["call_params"],
    )(provider_agnostic_call._original_fn)  # pyright: ignore [reportFunctionMemberAccess]
