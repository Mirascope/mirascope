"""This module contains the type definition for the Cohere call keyword arguments."""

from cohere.types import ChatMessage

from mirascope.core.base.call_kwargs import BaseCallKwargs

from .call_params import CohereCallParams
from .tool import CohereTool


class CohereCallKwargs(CohereCallParams, BaseCallKwargs[CohereTool]):
    model: str
    message: ChatMessage
