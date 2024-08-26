"""This module contains the type definition for the base call keyword arguments."""

from anthropic.types import MessageParam
from typing_extensions import NotRequired

from mirascope.core.anthropic import AnthropicCallParams, AnthropicTool
from mirascope.core.base.call_kwargs import BaseCallKwargs


class AnthropicCallKwargs(AnthropicCallParams, BaseCallKwargs[AnthropicTool]):
    model: NotRequired[str]
    messages: NotRequired[list[MessageParam]]
