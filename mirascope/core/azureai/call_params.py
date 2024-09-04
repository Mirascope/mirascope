"""usage docs: learn/calls.md#provider-specific-parameters"""

from __future__ import annotations

from typing import Any

from azure.ai.inference.models import (
    ChatCompletionsNamedToolChoice,
    ChatCompletionsResponseFormat,
    ChatCompletionsToolChoicePreset,
)
from typing_extensions import NotRequired

from ..base import BaseCallParams


class AzureAICallParams(BaseCallParams):
    """The parameters to use when calling the AzureAI API.

    [AzureAI API Reference](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-inference)

    Attributes:
        body: ...
        messages: ...
        stream: ...
        frequency_penalty: ...
        presence_penalty: ...
        temperature: ...
        top_p: ...
        max_tokens: ...
        response_format: ...
        stop: ...
        tools: ...
        tool_choice: ...
        seed: ...
        model: ...
        model_extras: ...
    """

    # body: MutableMapping[str, Any] | IO[bytes]
    stream: NotRequired[bool | None]
    frequency_penalty: NotRequired[float | None]
    presence_penalty: NotRequired[float | None]
    temperature: NotRequired[float | None]
    top_p: NotRequired[float | None]
    max_tokens: NotRequired[int | None]
    response_format: NotRequired[ChatCompletionsResponseFormat | None]
    stop: NotRequired[list[str] | None]
    tool_choice: NotRequired[
        str | ChatCompletionsToolChoicePreset | ChatCompletionsNamedToolChoice | None
    ]
    seed: NotRequired[int | None]
    model_extras: NotRequired[dict[str, Any] | None]
