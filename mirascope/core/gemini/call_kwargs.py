"""This module contains the type definition for the Gemini call keyword arguments."""

from google.generativeai.types import ContentDict

from ..base import BaseCallKwargs
from .call_params import GeminiCallParams
from .tool import GeminiTool


class GeminiCallKwargs(GeminiCallParams, BaseCallKwargs[GeminiTool]):
    contents: list[ContentDict]
