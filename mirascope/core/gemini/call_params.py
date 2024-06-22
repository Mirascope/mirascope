"""The parameters to use when calling the Gemini API."""

from __future__ import annotations

from typing import Any

from typing_extensions import NotRequired

from ..base import BaseCallParams


class GeminiCallParams(BaseCallParams):
    """The parameters to use when calling the Gemini API."""

    generation_config: NotRequired[dict[str, Any]]
    safety_settings: NotRequired[Any]
    request_options: NotRequired[dict[str, Any]]
