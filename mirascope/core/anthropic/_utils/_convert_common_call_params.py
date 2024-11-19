from typing import cast

from ...base.call_params import CommonCallParams
from ..call_params import AnthropicCallParams

ANTHROPIC_PARAM_MAPPING = {
    "temperature": "temperature",
    "max_tokens": "max_tokens",
    "top_p": "top_p",
    "stop": "stop_sequences",
}


def convert_common_call_params(common_params: CommonCallParams) -> AnthropicCallParams:
    """Convert CommonCallParams to Anthropic parameters."""
    return cast(
        AnthropicCallParams,
        {"max_tokens": 1024}
        | {
            ANTHROPIC_PARAM_MAPPING[key]: [value] if isinstance(value, str) else value
            for key, value in common_params.items()
            if key in ANTHROPIC_PARAM_MAPPING
            and ANTHROPIC_PARAM_MAPPING[key] is not None
        },
    )
