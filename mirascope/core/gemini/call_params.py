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
from ..base.call_params import CommonCallParams, convert_params, convert_stop_to_list


class GeminiCallParams(BaseCallParams):
    """The parameters to use when calling the Gemini API.

    [Gemini API Reference](https://ai.google.dev/gemini-api/docs/text-generation?lang=python)

    Attributes:
        generation_config: ...
        safety_settings: ...
        request_options: ...
        tool_config: ...
    """

    generation_config: NotRequired[GenerationConfigDict | GenerationConfig]
    safety_settings: NotRequired[SafetySettingOptions]
    request_options: NotRequired[RequestOptions]
    tool_config: NotRequired[ToolConfigType]


def get_gemini_call_params_from_common(params: CommonCallParams) -> GeminiCallParams:
    """Converts common call parameters to Gemini-specific call parameters."""
    mapping = {
        "temperature": "temperature",
        "max_tokens": "max_output_tokens",
        "top_p": "top_p",
        "stop": "stop_sequences",
    }
    transforms = [
        ("stop", convert_stop_to_list),
    ]
    return convert_params(
        params, mapping, GeminiCallParams, transforms=transforms, wrap_in_config=True
    )
