"""usage docs: learn/calls.md#provider-specific-parameters"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from mypy_boto3_bedrock_runtime.type_defs import (
    GuardrailConfigurationTypeDef,
    InferenceConfigurationTypeDef,
    SystemContentBlockTypeDef,
    ToolConfigurationTypeDef,
)
from typing_extensions import NotRequired

from ..base import BaseCallParams


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
