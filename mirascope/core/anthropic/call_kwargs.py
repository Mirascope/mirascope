"""This module contains the type definition for the Anthropic call keyword arguments."""

from anthropic.types import MessageParam
from typing_extensions import NotRequired

from mirascope.core.base.call_kwargs import BaseCallKwargs

from .call_params import AnthropicCallParams
from .tool import AnthropicTool


class AnthropicCallKwargs(AnthropicCallParams, BaseCallKwargs[AnthropicTool]):
    model: NotRequired[str]
    messages: NotRequired[list[MessageParam]]
