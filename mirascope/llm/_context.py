"""This module contains the context managers for LLM API calls."""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from types import TracebackType
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast, overload

from pydantic import BaseModel
from typing_extensions import TypedDict

from ..core.base import BaseTool, BaseType, CommonCallParams
from ..core.base.stream_config import StreamConfig
from ..core.base.types import LocalProvider, Provider

_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType | Enum)

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


class CallArgs(TypedDict):
    """TypedDict for call arguments."""

    provider: Provider | LocalProvider
    model: str
    stream: bool | StreamConfig
    tools: list[type[BaseTool] | Callable] | None
    response_model: type[BaseModel] | type[BaseType] | type[Enum] | None
    output_parser: Callable | None
    json_mode: bool
    client: Any | None
    call_params: CommonCallParams | Any | None


# We use a thread-local variable to store the current context, so that it's thread-safe
_current_context_local = threading.local()


@dataclass
class LLMContext:
    """Context for LLM API calls.

    This class is used to store the context for LLM API calls, including both
    setting overrides (provider, model, client, call_params) and
    structural overrides (stream, tools, response_model, etc.).
    """

    provider: Provider | LocalProvider | None = None
    model: str | None = None
    stream: bool | StreamConfig | None = None
    tools: list[type[BaseTool] | Callable] | None = None
    response_model: type[BaseModel] | type[BaseType] | type[Enum] | None = None
    output_parser: Callable | None = None
    json_mode: bool | None = None
    client: Any | None = None
    call_params: CommonCallParams | Any | None = None

    def __enter__(self) -> LLMContext:
        _current_context_local.context = self
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> Literal[False]:
        if hasattr(_current_context_local, "context"):
            del _current_context_local.context
        return False  # Don't suppress exceptions


def get_current_context() -> LLMContext | None:
    """Get the current context for LLM API calls.

    Returns:
        The current context, or None if there is no context.
    """
    if hasattr(_current_context_local, "context"):
        return cast(LLMContext, _current_context_local.context)
    return None


def _context(
    *,
    provider: Provider | LocalProvider | None,
    model: str | None,
    stream: bool | StreamConfig | None = None,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable | None = None,
    json_mode: bool | None = None,
    client: Any | None = None,  # noqa: ANN401
    call_params: CommonCallParams | Any | None = None,  # noqa: ANN401
) -> LLMContext:
    """Context manager for LLM API calls.

    This is an internal method that allows both setting and structural overrides
    for LLM functions.

    Unfortunately we have not yet identified a way to properly type hint this because
    providing no structural overrides means the return type is that of the original
    function. Of course, the `apply` method could pass through the return type, but
    we do not have a way to know whether it should be passthrough or not.

    For now, we use `_context` simply to implement `override` fully. The public facing
    `context` method only allows setting overrides.

    Args:
        provider: The provider to use for the LLM API call.
        model: The model to use for the LLM API call.
        stream: Whether to stream the response.
        tools: The tools to use for the LLM API call.
        response_model: The response model for the LLM API call.
        output_parser: The output parser for the LLM API call.
        json_mode: Whether to use JSON mode.
        client: The client to use for the LLM API call.
        call_params: The call parameters for the LLM API call.

    Returns:
        The context object that can be used to apply the context to a function.
    """
    old_context: LLMContext | None = getattr(_current_context_local, "context", None)
    if not old_context:
        return LLMContext(
            provider=provider,
            model=model,
            stream=stream,
            tools=tools,
            response_model=response_model,
            output_parser=output_parser,
            json_mode=json_mode,
            client=client,
            call_params=call_params,
        )
    else:
        # Ensure we properly set nested context settings. For example, we need to make
        # sure that calling override on an overridden function applies the context to
        # the overridden function's already overridden settings.
        return LLMContext(
            provider=provider or old_context.provider,
            model=model or old_context.model,
            stream=stream or old_context.stream,
            tools=tools or old_context.tools,
            response_model=response_model or old_context.response_model,
            output_parser=output_parser or old_context.output_parser,
            json_mode=json_mode or old_context.json_mode,
            client=client or old_context.client,
            call_params=call_params or old_context.call_params,
        )


def apply_context_overrides_to_call_args(
    call_args: CallArgs, context_override: LLMContext | None = None
) -> CallArgs:
    """Apply any active context overrides to the call arguments.

    Args:
        call_args: The original call arguments.
        context_override: Optional explicit context to use instead of the current thread context.

    Returns:
        The call arguments with any context overrides applied.
    """
    context = context_override or get_current_context()
    if not context:
        return call_args

    # Create a new dict with the original args
    overridden_args = CallArgs(call_args)

    # If any structural overrides are set, we have to force all others to take their
    # default values so the type hints match.
    if context.stream or context.response_model or context.output_parser:
        overridden_args["stream"] = False
        overridden_args["response_model"] = None
        overridden_args["output_parser"] = None
    if context.response_model:
        overridden_args["tools"] = None

    # Apply context overrides
    if context.provider is not None:
        overridden_args["provider"] = context.provider
    if context.model is not None:
        overridden_args["model"] = context.model
    if context.stream is not None:
        overridden_args["stream"] = context.stream
    if context.tools is not None:
        overridden_args["tools"] = context.tools
    if context.response_model is not None:
        overridden_args["response_model"] = context.response_model
    if context.output_parser is not None:
        overridden_args["output_parser"] = context.output_parser
    if context.json_mode is not None:
        overridden_args["json_mode"] = context.json_mode
    if context.client is not None:
        overridden_args["client"] = context.client
    if context.call_params is not None:
        overridden_args["call_params"] = context.call_params

    return overridden_args


@overload
def context(
    *,
    provider: Literal["anthropic"],
    model: str,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AnthropicCallParams | None = None,  # noqa: ANN401
) -> LLMContext: ...


@overload
def context(
    *,
    provider: Literal["azure"],
    model: str,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | AzureCallParams | None = None,  # noqa: ANN401
) -> LLMContext: ...


@overload
def context(
    *,
    provider: Literal["bedrock"],
    model: str,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | BedrockCallParams | None = None,  # noqa: ANN401
) -> LLMContext: ...


@overload
def context(
    *,
    provider: Literal["cohere"],
    model: str,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | CohereCallParams | None = None,  # noqa: ANN401
) -> LLMContext: ...


@overload
def context(
    *,
    provider: Literal["gemini"],
    model: str,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GeminiCallParams | None = None,  # noqa: ANN401
) -> LLMContext: ...


@overload
def context(
    *,
    provider: Literal["google"],
    model: str,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GoogleCallParams | None = None,  # noqa: ANN401
) -> LLMContext: ...


@overload
def context(
    *,
    provider: Literal["groq"],
    model: str,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | GroqCallParams | None = None,  # noqa: ANN401
) -> LLMContext: ...


@overload
def context(
    *,
    provider: Literal["litellm"],
    model: str,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | LiteLLMCallParams | None = None,  # noqa: ANN401
) -> LLMContext: ...


@overload
def context(
    *,
    provider: Literal["mistral"],
    model: str,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | MistralCallParams | None = None,  # noqa: ANN401
) -> LLMContext: ...


@overload
def context(
    *,
    provider: Literal["openai"],
    model: str,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | OpenAICallParams | None = None,  # noqa: ANN401
) -> LLMContext: ...


@overload
def context(
    *,
    provider: Literal["vertex"],
    model: str,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | VertexCallParams | None = None,  # noqa: ANN401
) -> LLMContext: ...


@overload
def context(
    *,
    provider: Literal["xai"],
    model: str,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | XAICallParams | None = None,  # noqa: ANN401
) -> LLMContext: ...


def context(
    *,
    provider: Provider | LocalProvider,
    model: str,
    client: Any | None = None,
    call_params: CommonCallParams | Any | None = None,  # noqa: ANN401
) -> LLMContext:
    """Context manager for LLM API calls.

    This method only allows setting overrides (provider, model, client, call_params)
    and does not allow structural overrides (stream, tools, response_model, etc.).

    Example:
        ```python
        @llm.call(provider="openai", model="gpt-4o-mini")
        def recommend_book(genre: str) -> str:
            return f"Recommend a {genre} book"

        # Override the model for a specific call
        with llm.context(provider="anthropic", model="claude-3-5-sonnet-20240620") as ctx:
            response = recommend_book("fantasy")  # Uses claude-3-5-sonnet
        ```

    Args:
        provider: The provider to use for the LLM API call.
        model: The model to use for the LLM API call.
        client: The client to use for the LLM API call.
        call_params: The call parameters for the LLM API call.

    Yields:
        The context object.
    """
    if (provider and not model) or (model and not provider):
        raise ValueError(
            "Provider and model must both be specified if either is specified."
        )

    return _context(
        provider=provider, model=model, client=client, call_params=call_params
    )
