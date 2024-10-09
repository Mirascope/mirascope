"""This module contains the type definition for the Bedrock call keyword arguments."""

from mypy_boto3_bedrock_runtime.type_defs import ToolTypeDef

from ..base import BaseCallKwargs
from ._types import InternalBedrockMessageParam
from .call_params import BedrockCallParams


class BedrockCallKwargs(BedrockCallParams, BaseCallKwargs[ToolTypeDef]):
    modelId: str
    messages: list[InternalBedrockMessageParam]
