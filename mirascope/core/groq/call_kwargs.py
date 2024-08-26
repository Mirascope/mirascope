"""This module contains the type definition for the base call keyword arguments."""

from groq.types.chat import ChatCompletionMessageParam
from typing_extensions import NotRequired

from mirascope.core.base.call_kwargs import BaseCallKwargs

from .call_params import GroqCallParams
from .tool import GroqTool


class GroqCallKwargs(GroqCallParams, BaseCallKwargs[GroqTool]):
    model: NotRequired[str]
    messages: NotRequired[list[ChatCompletionMessageParam]]
