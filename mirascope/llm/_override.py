"""Overrides the provider-specific call with the specified provider."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from functools import wraps
from typing import TYPE_CHECKING, Any, Literal, ParamSpec, TypeVar, cast, overload

from ..core.base import CommonCallParams
from ..core.base._utils import fn_is_async
from ..core.base.types import LocalProvider, Provider
from ._context import _context, _context_async

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
else:
    AnthropicCallParams = AzureCallParams = BedrockCallParams = CohereCallParams = (
        GeminiCallParams
    ) = GoogleCallParams = GroqCallParams = LiteLLMCallParams = MistralCallParams = (
        OpenAICallParams
    ) = VertexCallParams = None


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
    provider: Literal["google"],
    model: str,
    call_params: CommonCallParams | GoogleCallParams | None = None,
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
    provider: Provider | LocalProvider | None = None,
    model: str | None = None,
    call_params: CommonCallParams
    | AnthropicCallParams
    | GeminiCallParams
    | GoogleCallParams
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

    This function creates a new function that wraps the original function
    and temporarily sets a context with the specified overrides when called.

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
        ```

    Args:
        provider_agnostic_call: The provider-agnostic call to override.
        provider: The provider to override with.
        model: The model to override with.
        call_params: The call params to override with.
        client: The client to override with.

    Returns:
        The overridden function.
    """
    if (provider and not model) or (model and not provider):
        raise ValueError(
            "Provider and model must both be overridden if either is overridden."
        )

    # Check if the original function is async and create the appropriate wrapper
    if fn_is_async(provider_agnostic_call):

        @wraps(provider_agnostic_call)
        async def async_wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            async with _context_async(
                provider=provider,
                model=model,
                client=client,
                call_params=call_params,
            ):  # pyright: ignore [reportGeneralTypeIssues]
                return await cast(Callable[..., Awaitable[_R]], provider_agnostic_call)(
                    *args, **kwargs
                )

        return async_wrapper
    else:

        @wraps(provider_agnostic_call)
        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            with _context(
                provider=provider,
                model=model,
                client=client,
                call_params=call_params,
            ):  # pyright: ignore [reportGeneralTypeIssues]
                return provider_agnostic_call(*args, **kwargs)

        return wrapper
