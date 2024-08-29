"""This module contains the type definition for the Mistral call keyword arguments."""

from typing import Any

from mistralai.models.chat_completion import ChatMessage

from ..base import BaseCallKwargs
from .call_params import MistralCallParams


class MistralCallKwargs(MistralCallParams, BaseCallKwargs[dict[str, Any]]):
    model: str
    messages: list[ChatMessage]
