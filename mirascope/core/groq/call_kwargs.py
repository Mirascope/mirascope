"""This module contains the type definition for the Groq call keyword arguments."""

from groq.types.chat import ChatCompletionMessageParam

from mirascope.core.base.call_kwargs import BaseCallKwargs

from .call_params import GroqCallParams
from .tool import GroqTool


class GroqCallKwargs(GroqCallParams, BaseCallKwargs[GroqTool]):
    model: str
    messages: list[ChatCompletionMessageParam]
