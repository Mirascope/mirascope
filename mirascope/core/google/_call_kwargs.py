"""This module contains the type definition for the Google call keyword arguments."""

from collections.abc import Sequence

from google.genai.types import ContentOrDict, Tool

from ..base import BaseCallKwargs
from .call_params import GoogleCallParams


class GoogleCallKwargs(GoogleCallParams, BaseCallKwargs[Tool]):
    model: str
    contents: Sequence[ContentOrDict]
