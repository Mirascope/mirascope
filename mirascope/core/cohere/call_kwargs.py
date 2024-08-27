"""This module contains the type definition for the Cohere call keyword arguments."""

from ..base import BaseCallKwargs
from .call_params import CohereCallParams
from .tool import CohereTool


class CohereCallKwargs(CohereCallParams, BaseCallKwargs[CohereTool]):
    model: str
    message: str
