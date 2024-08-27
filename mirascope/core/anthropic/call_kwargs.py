"""This module contains the type definition for the Anthropic call keyword arguments."""

from anthropic.types import MessageParam

from ..base import BaseCallKwargs
from .call_params import AnthropicCallParams
from .tool import AnthropicTool


class AnthropicCallKwargs(AnthropicCallParams, BaseCallKwargs[AnthropicTool]):
    model: str
    messages: list[MessageParam]
