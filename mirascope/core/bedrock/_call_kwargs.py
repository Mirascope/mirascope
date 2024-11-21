"""This module contains the type definition for the Bedrock call keyword arguments."""

from collections.abc import Sequence

from ..base import BaseCallKwargs
from ._types import InternalBedrockMessageParam, ToolTypeDef
from .call_params import BedrockCallParams


class BedrockCallKwargs(BedrockCallParams, BaseCallKwargs[ToolTypeDef]):
    modelId: str
    messages: Sequence[InternalBedrockMessageParam]
