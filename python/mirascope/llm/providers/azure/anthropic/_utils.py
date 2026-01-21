"""Azure Anthropic provider utilities."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from typing import TYPE_CHECKING, Any, cast

from ....formatting import Format, FormattableT, OutputParser
from ....messages import AssistantMessage, Message
from ....responses import FinishReason, Usage
from ....tools import AnyToolSchema, BaseToolkit
from ...anthropic import _utils as anthropic_utils
from ...anthropic._utils import beta_decode, beta_encode
from .. import _utils as azure_utils
from ..model_id import AzureModelId

is_awaitable_str = azure_utils.is_awaitable_str
normalize_base_url = azure_utils.normalize_base_url
wrap_async_token_provider = azure_utils.wrap_async_token_provider
wrap_sync_token_provider = azure_utils.wrap_sync_token_provider

if TYPE_CHECKING:
    from anthropic import types as anthropic_types
    from anthropic.lib.foundry import AsyncAzureADTokenProvider, AzureADTokenProvider
    from anthropic.types.beta.parsed_beta_message import ParsedBetaMessage

    from ....models import Params
    from ...anthropic._utils.beta_encode import BetaParseKwargs
    from ...anthropic._utils.encode import MessageCreateKwargs

AZURE_ANTHROPIC_PROVIDER_ID = "azure:anthropic"


def azure_model_name(model_id: AzureModelId) -> str:
    """Extract the Azure deployment name from the model ID."""
    if model_id.startswith("azure/"):
        return model_id.split("/", 1)[1]
    return model_id


def coerce_sync_token_provider(
    azure_ad_token_provider: AzureADTokenProvider | AsyncAzureADTokenProvider | None,
) -> AzureADTokenProvider | None:
    """Coerce Azure AD token providers for synchronous Anthropic clients.

    Args:
        azure_ad_token_provider: Azure AD token provider.

    Returns:
        A wrapped sync token provider.

    Raises:
        ValueError: If the provider returns an awaitable or non-string token.
    """
    if azure_ad_token_provider is None:
        return None

    provider = cast(Callable[[], str | Awaitable[str]], azure_ad_token_provider)
    return wrap_sync_token_provider(provider)


def coerce_async_token_provider(
    azure_ad_token_provider: AzureADTokenProvider | AsyncAzureADTokenProvider | None,
) -> AsyncAzureADTokenProvider | None:
    """Coerce Azure AD token providers for asynchronous Anthropic clients.

    Args:
        azure_ad_token_provider: Azure AD token provider.

    Returns:
        A wrapped async token provider.

    Raises:
        ValueError: If the provider returns an empty or non-string token.
    """
    if azure_ad_token_provider is None:
        return None

    provider = cast(Callable[[], str | Awaitable[str]], azure_ad_token_provider)
    return wrap_async_token_provider(provider)


def encode_request(
    *,
    model_id: AzureModelId,
    messages: Sequence[Message],
    tools: Sequence[AnyToolSchema] | BaseToolkit[AnyToolSchema] | None,
    format: type[FormattableT]
    | Format[FormattableT]
    | OutputParser[FormattableT]
    | None,
    params: Params,
) -> tuple[Sequence[Message], Format[FormattableT] | None, MessageCreateKwargs]:
    """Prepare a request for the Azure Anthropic messages.create method."""
    input_messages, resolved_format, kwargs = anthropic_utils.encode_request(
        model_id=model_id,
        messages=messages,
        tools=tools,
        format=format,
        params=params,
    )
    kwargs["model"] = azure_model_name(model_id)
    return input_messages, resolved_format, kwargs


def beta_encode_request(
    *,
    model_id: AzureModelId,
    messages: Sequence[Message],
    tools: Sequence[AnyToolSchema] | BaseToolkit[AnyToolSchema] | None,
    format: type[FormattableT]
    | Format[FormattableT]
    | OutputParser[FormattableT]
    | None,
    params: Params,
) -> tuple[Sequence[Message], Format[FormattableT] | None, BetaParseKwargs]:
    """Prepare a request for the Azure Anthropic beta.messages.parse method."""
    return beta_encode.beta_encode_request(
        model_id=azure_model_name(model_id),
        messages=messages,
        tools=tools,
        format=format,
        params=params,
    )


def decode_response(
    response: anthropic_types.Message,
    model_id: AzureModelId,
    *,
    include_thoughts: bool,
    provider_id: str = AZURE_ANTHROPIC_PROVIDER_ID,
) -> tuple[AssistantMessage, FinishReason | None, Usage]:
    """Decode an Azure Anthropic message response."""
    assistant_message, finish_reason, usage = anthropic_utils.decode_response(
        response, model_id, include_thoughts=include_thoughts
    )
    assistant_message = AssistantMessage(
        content=assistant_message.content,
        name=assistant_message.name,
        provider_id=provider_id,
        model_id=model_id,
        provider_model_name=azure_model_name(model_id),
        raw_message=assistant_message.raw_message,
    )
    return assistant_message, finish_reason, usage


def beta_decode_response(
    response: ParsedBetaMessage[Any],
    model_id: AzureModelId,
    *,
    include_thoughts: bool,
    provider_id: str = AZURE_ANTHROPIC_PROVIDER_ID,
) -> tuple[AssistantMessage, FinishReason | None, Usage]:
    """Decode an Azure Anthropic beta message response."""
    assistant_message, finish_reason, usage = beta_decode.beta_decode_response(
        response, model_id, include_thoughts=include_thoughts
    )
    assistant_message = AssistantMessage(
        content=assistant_message.content,
        name=assistant_message.name,
        provider_id=provider_id,
        model_id=model_id,
        provider_model_name=azure_model_name(model_id),
        raw_message=assistant_message.raw_message,
    )
    return assistant_message, finish_reason, usage
