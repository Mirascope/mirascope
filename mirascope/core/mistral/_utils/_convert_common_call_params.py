from typing import cast

from ...base.call_params import CommonCallParams
from ..call_params import MistralCallParams

MISTRAL_PARAM_MAPPING = {
    "temperature": "temperature",
    "max_tokens": "max_tokens",
    "top_p": "top_p",
    "seed": "random_seed",
    "stop": "stop",
}


def convert_common_call_params(common_params: CommonCallParams) -> MistralCallParams:
    """Convert CommonCallParams to Mistral parameters."""
    return cast(
        MistralCallParams,
        {
            MISTRAL_PARAM_MAPPING[key]: value
            for key, value in common_params.items()
            if key in MISTRAL_PARAM_MAPPING and value is not None
        },
    )
