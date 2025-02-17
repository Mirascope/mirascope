"""usage docs: learn/calls.md#provider-specific-parameters"""

from __future__ import annotations

from typing import Any, Literal, TypeAlias

from azure.ai.inference.models import (
    ChatCompletionsNamedToolChoice,
    ChatCompletionsToolChoicePreset,
)

try:
    from azure.ai.inference.models import (
        ChatCompletionsResponseFormatJSON,
    )

    ResponseFormatJSON: TypeAlias = ChatCompletionsResponseFormatJSON  # pyright: ignore [reportRedeclaration]
except ImportError:  # pragma: no cover
    from azure.ai.inference.models import (
        JsonSchemaFormat,  # pyright: ignore [reportAttributeAccessIssue]
    )

    ResponseFormatJSON: TypeAlias = JsonSchemaFormat | Literal["json_object"]  # pyright: ignore [reportRedeclaration]

from typing_extensions import NotRequired

from ..base import BaseCallParams


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
    response_format: NotRequired[ResponseFormatJSON | None]
    seed: NotRequired[int | None]
    stop: NotRequired[list[str] | None]
    temperature: NotRequired[float | None]
    tool_choice: NotRequired[
        str | ChatCompletionsToolChoicePreset | ChatCompletionsNamedToolChoice | None
    ]
    top_p: NotRequired[float | None]
