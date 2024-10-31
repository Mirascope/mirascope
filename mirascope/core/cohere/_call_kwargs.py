"""This module contains the type definition for the Cohere call keyword arguments."""

from cohere.types import Tool

from ..base import BaseCallKwargs
from .call_params import CohereCallParams


class CohereCallKwargs(CohereCallParams, BaseCallKwargs[Tool]):
    model: str
    message: str
