"""usage docs: learn/calls.md#provider-specific-parameters"""

from __future__ import annotations

from google.generativeai.types import (
    GenerationConfig,
    GenerationConfigDict,
    RequestOptions,
)
from google.generativeai.types.content_types import ToolConfigType
from google.generativeai.types.safety_types import SafetySettingOptions
from typing_extensions import NotRequired

from ..base import BaseCallParams

GenerationConfigType = GenerationConfigDict | GenerationConfig


class GeminiCallParams(BaseCallParams):
    """The parameters to use when calling the Gemini API.

    [Gemini API Reference](https://ai.google.dev/gemini-api/docs/text-generation?lang=python)

    Attributes:
        generation_config: ...
        safety_settings: ...
        request_options: ...
        tool_config: ...
    """

    generation_config: NotRequired[GenerationConfigType]
    safety_settings: NotRequired[SafetySettingOptions]
    request_options: NotRequired[RequestOptions]
    tool_config: NotRequired[ToolConfigType]
