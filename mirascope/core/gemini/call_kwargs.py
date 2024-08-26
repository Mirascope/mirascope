"""This module contains the type definition for the base call keyword arguments."""

from mirascope.core.base.call_kwargs import BaseCallKwargs

from .call_params import GeminiCallParams
from .tool import GeminiTool


class GeminiCallKwargs(GeminiCallParams, BaseCallKwargs[GeminiTool]): ...
