from typing import cast

from mirascope.core.azure import AzureCallParams
from mirascope.core.base.call_params import CommonCallParams

AZURE_PARAM_MAPPING = {
    "temperature": "temperature",
    "max_tokens": "max_tokens",
    "top_p": "top_p",
    "frequency_penalty": "frequency_penalty",
    "presence_penalty": "presence_penalty",
    "seed": "seed",
    "stop": "stop",
}


def convert_common_params(common_params: CommonCallParams) -> AzureCallParams:
    """Convert CommonCallParams to Azure parameters."""
    return cast(
        AzureCallParams,
        {
            AZURE_PARAM_MAPPING[key]: [value] if isinstance(value, str) else value
            for key, value in common_params.items()
            if key in AZURE_PARAM_MAPPING and AZURE_PARAM_MAPPING[key] is not None
        },
    )
