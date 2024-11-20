"""usage docs: learn/calls.md#provider-specific-parameters"""

from __future__ import annotations

from mistralai.models import ResponseFormat, ToolChoice, ToolChoiceEnum
from typing_extensions import NotRequired

from ..base import BaseCallParams


class MistralCallParams(BaseCallParams):
    """The parameters to use when calling the Mistral API.

    [Mistral API Reference](https://docs.mistral.ai/api/)

    Attributes:
        endpoint: ...
        max_tokens: ...
        random_seed: ...
        response_format: ...
        safe_mode: ...
        safe_prompt: ...
        temperature: ...
        tool_choice: ...
        top_p: ...
    """

    endpoint: NotRequired[str | None]
    max_tokens: NotRequired[int | None]
    random_seed: NotRequired[int | None]
    response_format: NotRequired[ResponseFormat | None]
    safe_mode: NotRequired[bool | None]
    safe_prompt: NotRequired[bool | None]
    temperature: NotRequired[float | None]
    tool_choice: NotRequired[ToolChoice | ToolChoiceEnum | None]
    top_p: NotRequired[float | None]
