"""The parameters to use when calling the Mistral API."""

from __future__ import annotations

from mistralai.models.chat_completion import ResponseFormat, ToolChoice
from typing_extensions import NotRequired

from ..base import BaseCallParams


class MistralCallParams(BaseCallParams):
    """The parameters to use when calling the Mistral API."""

    endpoint: NotRequired[str | None]
    max_tokens: NotRequired[int | None]
    random_seed: NotRequired[int | None]
    response_format: NotRequired[ResponseFormat | None]
    safe_mode: NotRequired[bool | None]
    safe_prompt: NotRequired[bool | None]
    temperature: NotRequired[float | None]
    tool_choice: NotRequired[ToolChoice | None]
    top_p: NotRequired[float | None]
