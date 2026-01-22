"""Bedrock Anthropic provider utilities."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from ....formatting import Format, FormattableT, OutputParser
from ....messages import AssistantMessage, Message
from ....responses import FinishReason, Usage
from ....tools import AnyToolSchema, BaseToolkit
from ...anthropic import _utils as anthropic_utils
from .. import _utils as bedrock_utils
from ..model_id import BedrockModelId

if TYPE_CHECKING:
    from anthropic import types as anthropic_types

    from ....models import Params
    from ...anthropic._utils.encode import MessageCreateKwargs

BEDROCK_ANTHROPIC_PROVIDER_ID = "bedrock:anthropic"


def encode_request(
    *,
    model_id: BedrockModelId,
    messages: Sequence[Message],
    toolkit: BaseToolkit[AnyToolSchema],
    format: type[FormattableT]
    | Format[FormattableT]
    | OutputParser[FormattableT]
    | None,
    params: Params,
) -> tuple[Sequence[Message], Format[FormattableT] | None, MessageCreateKwargs]:
    """Prepare a request for the Bedrock Anthropic messages.create method."""
    input_messages, resolved_format, kwargs = anthropic_utils.encode_request(
        model_id=model_id,
        messages=messages,
        tools=toolkit,
        format=format,
        params=params,
        model_name_override=bedrock_utils.bedrock_model_name(model_id),
    )
    return input_messages, resolved_format, kwargs


def decode_response(
    response: anthropic_types.Message,
    model_id: BedrockModelId,
    *,
    include_thoughts: bool,
    provider_id: str = BEDROCK_ANTHROPIC_PROVIDER_ID,
) -> tuple[AssistantMessage, FinishReason | None, Usage]:
    """Decode a Bedrock Anthropic message response."""
    assistant_message, finish_reason, usage = anthropic_utils.decode_response(
        response, model_id, include_thoughts=include_thoughts
    )
    assistant_message = AssistantMessage(
        content=assistant_message.content,
        name=assistant_message.name,
        provider_id=provider_id,
        model_id=model_id,
        provider_model_name=bedrock_utils.bedrock_model_name(model_id),
        raw_message=assistant_message.raw_message,
    )
    return assistant_message, finish_reason, usage
