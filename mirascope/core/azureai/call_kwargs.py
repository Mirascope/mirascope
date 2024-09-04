"""This module contains the type definition for the AzureAI call keyword arguments."""

from azure.ai.inference.models import ChatCompletionsToolDefinition, ChatRequestMessage

from ..base import BaseCallKwargs
from .call_params import AzureAICallParams


class AzureAICallKwargs(
    AzureAICallParams, BaseCallKwargs[ChatCompletionsToolDefinition]
):
    model: str
    messages: list[ChatRequestMessage]
