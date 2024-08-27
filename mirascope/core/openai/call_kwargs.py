"""This module contains the type definition for the OpenAI call keyword arguments."""

from openai.types.chat import ChatCompletionMessageParam

from ..base import BaseCallKwargs
from .call_params import OpenAICallParams
from .tool import OpenAITool


class OpenAICallKwargs(OpenAICallParams, BaseCallKwargs[OpenAITool]):
    model: str
    messages: list[ChatCompletionMessageParam]
