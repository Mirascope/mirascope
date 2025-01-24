"""usage docs: learn/calls.md#provider-specific-parameters"""

from __future__ import annotations

from google.genai.types import (
    GenerateContentConfigOrDict,
)
from typing_extensions import NotRequired

from ..base import BaseCallParams


class GoogleCallParams(BaseCallParams):
    """The parameters to use when calling the Google API.

    [Google API Reference](https://ai.google.dev/google-api/docs/text-generation?lang=python)

    Attributes:
        config: ...
    """

    config: NotRequired[GenerateContentConfigOrDict]
