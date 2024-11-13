from typing import cast

from ...base.call_params import CommonCallParams
from ..call_params import GroqCallParams

GROQ_PARAM_MAPPING = {
    "temperature": "temperature",
    "max_tokens": "max_tokens",
    "top_p": "top_p",
    "frequency_penalty": "frequency_penalty",
    "presence_penalty": "presence_penalty",
    "seed": "seed",
    "stop": "stop",
}


def convert_common_call_params(common_params: CommonCallParams) -> GroqCallParams:
    """Convert CommonCallParams to Groq parameters."""
    return cast(
        GroqCallParams,
        {
            GROQ_PARAM_MAPPING[key]: value
            for key, value in common_params.items()
            if key in GROQ_PARAM_MAPPING and value is not None
        },
    )
