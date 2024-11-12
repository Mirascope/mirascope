from typing import cast

from mirascope.core.base.call_params import CommonCallParams
from mirascope.core.mistral import MistralCallParams

MISTRAL_PARAM_MAPPING = {
    "temperature": "temperature",
    "max_tokens": "max_tokens",
    "top_p": "top_p",
    "seed": "random_seed",
    "stop": "stop",
}


def convert_common_params(common_params: CommonCallParams) -> MistralCallParams:
    """Convert CommonCallParams to Mistral parameters."""
    return cast(
        MistralCallParams,
        {
            MISTRAL_PARAM_MAPPING[key]: value
            for key, value in common_params.items()
            if key in MISTRAL_PARAM_MAPPING and value is not None
        },
    )
