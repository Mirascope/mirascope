from typing import cast

from mypy_boto3_bedrock_runtime.type_defs import (
    InferenceConfigurationTypeDef,
)

from ...base.call_params import CommonCallParams
from ..call_params import BedrockCallParams

BEDROCK_PARAM_MAPPING = {
    "temperature": "temperature",
    "max_tokens": "maxTokens",
    "top_p": "topP",
    "stop": "stopSequences",
}


def convert_common_call_params(common_params: CommonCallParams) -> BedrockCallParams:
    """Convert CommonCallParams to Bedrock parameters."""
    inference_config = {}

    for key, value in common_params.items():
        if key not in BEDROCK_PARAM_MAPPING or value is None:
            continue

        if key == "stop":
            inference_config["stopSequences"] = (
                [value] if isinstance(value, str) else value
            )
        else:
            inference_config[BEDROCK_PARAM_MAPPING[key]] = value

    if not inference_config:
        return cast(BedrockCallParams, {})

    return cast(
        BedrockCallParams,
        {"inferenceConfig": cast(InferenceConfigurationTypeDef, inference_config)},
    )
