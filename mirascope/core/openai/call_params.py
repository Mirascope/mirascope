"""The parameters to use when calling the OpenAI API."""

from __future__ import annotations

from openai.types.chat import (
    ChatCompletionStreamOptionsParam,
    ChatCompletionToolChoiceOptionParam,
)
from openai.types.chat.completion_create_params import ResponseFormat
from typing_extensions import NotRequired

from ..base import BaseCallParams


class OpenAICallParams(BaseCallParams):
    """The parameters to use when calling the OpenAI API."""

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
    stream_options: NotRequired[ChatCompletionStreamOptionsParam | None]
    temperature: NotRequired[float | None]
    tool_choice: NotRequired[ChatCompletionToolChoiceOptionParam]
    top_logprobs: NotRequired[int | None]
    top_p: NotRequired[float | None]
    user: NotRequired[str]
