"""This module contains the type definition for the Gemini call keyword arguments."""

from collections.abc import Sequence

from google.generativeai.types import ContentDict, Tool

from ..base import BaseCallKwargs
from .call_params import GeminiCallParams


class GeminiCallKwargs(GeminiCallParams, BaseCallKwargs[Tool]):
    contents: Sequence[ContentDict]
