from typing import cast

from google.genai.types import GenerateContentConfig

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
    config = GenerateContentConfig()

    for key, value in common_params.items():
        if key not in GOOGLE_PARAM_MAPPING or value is None:
            continue

        if key == "stop":
            # Google API expects a list of strings for stop sequences
            if isinstance(value, str):
                config.stop_sequences = [value]
            elif isinstance(value, list):
                config.stop_sequences = value
        else:
            target_attr = GOOGLE_PARAM_MAPPING[key]
            setattr(config, target_attr, value)

    default_config = GenerateContentConfig()
    if config == default_config:
        return cast(GoogleCallParams, {})

    return cast(GoogleCallParams, {"config": config})
