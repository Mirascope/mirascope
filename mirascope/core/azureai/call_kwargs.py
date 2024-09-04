"""This module contains the type definition for the AzureAI call keyword arguments."""

from azureai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam

from ..base import BaseCallKwargs
from .call_params import AzureAICallParams


class AzureAICallKwargs(AzureAICallParams, BaseCallKwargs[ChatCompletionToolParam]):
    model: str
    messages: list[ChatCompletionMessageParam]
