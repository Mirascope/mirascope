"""This module contains the type definition for the Azure call keyword arguments."""

from collections.abc import Sequence

from azure.ai.inference.models import ChatCompletionsToolDefinition, ChatRequestMessage

from ..base import BaseCallKwargs
from .call_params import AzureCallParams


class AzureCallKwargs(AzureCallParams, BaseCallKwargs[ChatCompletionsToolDefinition]):
    model: str
    messages: Sequence[ChatRequestMessage]
