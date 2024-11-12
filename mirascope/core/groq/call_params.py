"""usage docs: learn/calls.md#provider-specific-parameters"""

from __future__ import annotations

from groq.types.chat.chat_completion_tool_choice_option_param import (
    ChatCompletionToolChoiceOptionParam,
)
from groq.types.chat.completion_create_params import ResponseFormat
from typing_extensions import NotRequired

from ..base import BaseCallParams


class GroqCallParams(BaseCallParams):
    """The parameters to use when calling the Groq API.

    [Groq API Reference](https://console.groq.com/docs/api-reference#chat-create)

    Attributes:
        frequency_penalty: ...
        logit_bias: ...
        logprobs: ...
        max_tokens: ...
        n: ...
        parallel_tool_calls: ...
        presence_penalty: ...
        response_format: ...
        seed: ...
        stop: ...
        temperature: ...
        tool_choice: ...
        top_logprobs: ...
        top_p: ...
        user: ...
    """

    extra_headers: NotRequired[dict[str, str] | None]
    frequency_penalty: NotRequired[float | None]
    logit_bias: NotRequired[dict[str, int] | None]
    logprobs: NotRequired[bool | None]
    max_tokens: NotRequired[int | None]
    n: NotRequired[int | None]
    parallel_tool_calls: NotRequired[bool]
    presence_penalty: NotRequired[float | None]
    response_format: NotRequired[ResponseFormat]
    seed: NotRequired[int | None]
    stop: NotRequired[str | list[str] | None]
    temperature: NotRequired[float | None]
    tool_choice: NotRequired[ChatCompletionToolChoiceOptionParam]
    top_logprobs: NotRequired[int | None]
    top_p: NotRequired[float | None]
    user: NotRequired[str]
