from typing import cast

from ...base.call_params import CommonCallParams
from ..call_params import CohereCallParams

COHERE_PARAM_MAPPING = {
    "temperature": "temperature",
    "max_tokens": "max_tokens",
    "top_p": "p",
    "frequency_penalty": "frequency_penalty",
    "presence_penalty": "presence_penalty",
    "seed": "seed",
    "stop": "stop_sequences",
}


def convert_common_call_params(common_params: CommonCallParams) -> CohereCallParams:
    """Convert CommonCallParams to Cohere parameters."""
    return cast(
        CohereCallParams,
        {
            COHERE_PARAM_MAPPING[key]: [value] if isinstance(value, str) else value
            for key, value in common_params.items()
            if key in COHERE_PARAM_MAPPING and COHERE_PARAM_MAPPING[key] is not None
        },
    )
