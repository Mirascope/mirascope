"""This module contains the type definition for the base call keyword arguments."""

from openai.types.chat import ChatCompletionMessageParam
from typing_extensions import NotRequired

from mirascope.core.base.call_kwargs import BaseCallKwargs
from mirascope.core.openai import OpenAICallParams, OpenAITool


class OpenAICallKwargs(OpenAICallParams, BaseCallKwargs[OpenAITool]):
    model: NotRequired[str]
    messages: NotRequired[list[ChatCompletionMessageParam]]
