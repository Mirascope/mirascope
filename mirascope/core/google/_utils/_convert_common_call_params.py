from typing import Any, cast

from google.genai.types import (
    GenerationConfigDict,
)

from ...base.call_params import CommonCallParams
from ..call_params import GoogleCallParams

GOOGLE_PARAM_MAPPING = {
    "temperature": "temperature",
    "max_tokens": "max_output_tokens",
    "top_p": "top_p",
    "stop": "stop_sequences",
}


def convert_common_call_params(common_params: CommonCallParams) -> GoogleCallParams:
    """Convert CommonCallParams to Google parameters."""
    generation_config: dict[str, Any] = {}

    for key, value in common_params.items():
        if key not in GOOGLE_PARAM_MAPPING or value is None:
            continue

        if key == "stop":
            # Google API expects a list of strings for stop sequences
            if isinstance(value, str):
                generation_config["stop_sequences"] = [value]
            elif isinstance(value, list):
                generation_config["stop_sequences"] = value
        else:
            generation_config[GOOGLE_PARAM_MAPPING[key]] = value

    if not generation_config:
        return cast(GoogleCallParams, {})

    return cast(
        GoogleCallParams,
        {"generation_config": cast(GenerationConfigDict, generation_config)},
    )
