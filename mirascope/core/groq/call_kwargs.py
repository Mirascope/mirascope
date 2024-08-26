"""This module contains the type definition for the base call keyword arguments."""

from groq.types.chat import ChatCompletionMessageParam
from typing_extensions import NotRequired

from mirascope.core.base.call_kwargs import BaseCallKwargs
from mirascope.core.groq import GroqCallParams, GroqTool


class GroqCallKwargs(GroqCallParams, BaseCallKwargs[GroqTool]):
    model: NotRequired[str]
    messages: NotRequired[list[ChatCompletionMessageParam]]
