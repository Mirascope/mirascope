from typing import cast

from google.generativeai.types import (
    GenerationConfigDict,
)

from ...base.call_params import CommonCallParams
from ..call_params import GeminiCallParams

GEMINI_PARAM_MAPPING = {
    "temperature": "temperature",
    "max_tokens": "max_output_tokens",
    "top_p": "top_p",
    "stop": "stop_sequences",
}


def convert_common_call_params(common_params: CommonCallParams) -> GeminiCallParams:
    """Convert CommonCallParams to Gemini parameters."""
    generation_config = {}

    for key, value in common_params.items():
        if key not in GEMINI_PARAM_MAPPING or value is None:
            continue

        if key == "stop":
            generation_config["stop_sequences"] = (
                [value] if isinstance(value, str) else value
            )
        else:
            generation_config[GEMINI_PARAM_MAPPING[key]] = value

    if not generation_config:
        return cast(GeminiCallParams, {})

    return cast(
        GeminiCallParams,
        {"generation_config": cast(GenerationConfigDict, generation_config)},
    )
