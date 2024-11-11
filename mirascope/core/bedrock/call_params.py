"""usage docs: learn/calls.md#provider-specific-parameters"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from mypy_boto3_bedrock_runtime.type_defs import (
    GuardrailConfigurationTypeDef,
    InferenceConfigurationTypeDef,
    SystemContentBlockTypeDef,
    ToolConfigurationTypeDef,
)
from typing_extensions import NotRequired

from ..base import BaseCallParams
from ..base.call_params import CommonCallParams, convert_stop_to_list


class BedrockCallParams(BaseCallParams):
    """The parameters to use when calling the Bedrock API.

    [Bedrock converse API Reference](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime/client/converse.html)

    Attributes:
        system (Sequence[SystemContentBlockTypeDef]): The system content blocks to use in the API call.
        inferenceConfig (InferenceConfigurationTypeDef): The inference configuration to use in the API call.
        toolConfig (ToolConfigurationTypeDef): The tool configuration to use in the API call.
        guardrailConfig (GuardrailConfigurationTypeDef): The guardrail configuration to use in the API call.
        additionalModelRequestFields (Mapping[str, Any]): Additional model request fields to use in the API call.
        additionalModelResponseFieldPaths (Sequence[str]): Additional model response field paths to use in the API call.
    """

    system: NotRequired[list[SystemContentBlockTypeDef]]
    inferenceConfig: NotRequired[InferenceConfigurationTypeDef]
    toolConfig: NotRequired[ToolConfigurationTypeDef]
    guardrailConfig: NotRequired[GuardrailConfigurationTypeDef]
    additionalModelRequestFields: NotRequired[Mapping[str, Any]]
    additionalModelResponseFieldPaths: NotRequired[list[str]]


def _create_inference_config(params: CommonCallParams) -> InferenceConfigurationTypeDef:
    """Creates inference configuration from common parameters.

    Args:
        params: Common parameters to convert.

    Returns:
        Bedrock inference configuration.
    """
    config: dict[str, Any] = {}

    if temperature := params.get("temperature"):
        config["temperature"] = temperature
    if max_tokens := params.get("max_tokens"):
        config["maxTokens"] = max_tokens
    if top_p := params.get("top_p"):
        config["topP"] = top_p
    if stop := params.get("stop"):
        config["stopSequences"] = convert_stop_to_list(stop)

    return cast(InferenceConfigurationTypeDef, config)


def get_bedrock_call_params_from_common(params: CommonCallParams) -> BedrockCallParams:
    """Converts common call parameters to Bedrock-specific call parameters.

    Args:
        params: Common parameters to convert.

    Returns:
        Bedrock-specific call parameters.
    """
    inference_config = _create_inference_config(params)
    result: BedrockCallParams = {}

    if inference_config:
        result["inferenceConfig"] = inference_config

    return result
