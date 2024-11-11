"""usage docs: learn/calls.md#provider-specific-parameters"""

from __future__ import annotations

from typing import Any

from azure.ai.inference.models import (
    ChatCompletionsNamedToolChoice,
    ChatCompletionsResponseFormat,
    ChatCompletionsToolChoicePreset,
)
from typing_extensions import NotRequired, Unpack

from ..base import BaseCallParams
from ..base.call_params import CommonCallParams, convert_params, convert_stop_to_list


class AzureCallParams(BaseCallParams):
    """The parameters to use when calling the Azure API.

    [Azure API Reference](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-inference)

    Attributes:
        frequency_penalty: ...
        max_tokens: ...
        model_extras: ...
        presence_penalty: ...
        response_format: ...
        seed: ...
        stop: ...
        temperature: ...
        tool_choice: ...
        top_p: ...
    """

    frequency_penalty: NotRequired[float | None]
    max_tokens: NotRequired[int | None]
    model_extras: NotRequired[dict[str, Any] | None]
    presence_penalty: NotRequired[float | None]
    response_format: NotRequired[ChatCompletionsResponseFormat | None]
    seed: NotRequired[int | None]
    stop: NotRequired[list[str] | None]
    temperature: NotRequired[float | None]
    tool_choice: NotRequired[
        str | ChatCompletionsToolChoicePreset | ChatCompletionsNamedToolChoice | None
    ]
    top_p: NotRequired[float | None]


def get_azure_call_params_from_common(
    **params: Unpack[CommonCallParams],
) -> AzureCallParams:
    """Converts common call parameters to Azure-specific call parameters."""
    mapping = {
        "temperature": "temperature",
        "max_tokens": "max_tokens",
        "top_p": "top_p",
        "frequency_penalty": "frequency_penalty",
        "presence_penalty": "presence_penalty",
        "seed": "seed",
        "stop": "stop",
    }
    transforms = [
        ("stop", convert_stop_to_list),
    ]
    return convert_params(params, mapping, AzureCallParams, transforms)
