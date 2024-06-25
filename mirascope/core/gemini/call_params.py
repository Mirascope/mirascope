"""The parameters to use when calling the Gemini API."""

from __future__ import annotations

from google.generativeai.types import GenerationConfig, RequestOptions
from google.generativeai.types.content_types import ToolConfigType
from google.generativeai.types.safety_types import SafetySettingOptions
from typing_extensions import NotRequired

from ..base import BaseCallParams


class GeminiCallParams(BaseCallParams):
    """The parameters to use when calling the Gemini API."""

    generation_config: NotRequired[GenerationConfig]
    safety_settings: NotRequired[SafetySettingOptions]
    request_options: NotRequired[RequestOptions]
    tool_config: NotRequired[ToolConfigType]
