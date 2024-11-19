"""This module contains the type definition for the Mistral call keyword arguments."""

from typing import Any

from mistralai.models import (
    AssistantMessage,
    SystemMessage,
    ToolMessage,
    UserMessage,
)

from ..base import BaseCallKwargs
from .call_params import MistralCallParams


class MistralCallKwargs(MistralCallParams, BaseCallKwargs[dict[str, Any]]):
    model: str
    messages: list[AssistantMessage | SystemMessage | ToolMessage | UserMessage]
