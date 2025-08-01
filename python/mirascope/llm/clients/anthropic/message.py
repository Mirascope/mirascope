"""Anthropic message types."""

from typing import TypeAlias

from anthropic.types import MessageParam

from ...messages import Message

AnthropicMessage: TypeAlias = Message | MessageParam
