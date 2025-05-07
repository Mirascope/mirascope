"""usage docs: learn/calls.md#provider-specific-parameters"""

from __future__ import annotations

from typing import TYPE_CHECKING

from openai.types.chat import (
    ChatCompletionStreamOptionsParam,
    ChatCompletionToolChoiceOptionParam,
)
from openai.types.chat.completion_create_params import ResponseFormat
from typing_extensions import NotRequired

from ..base import BaseCallParams

if TYPE_CHECKING:
    from openai.types.chat.chat_completion_audio_param import (  # pyright: ignore [reportMissingImports]
        ChatCompletionAudioParam,
        ChatCompletionModality,  # pyright: ignore [reportAttributeAccessIssue]
    )
    from openai.types.chat.chat_completion_reasoning_effort import (  # pyright: ignore [reportMissingImports]
        ChatCompletionReasoningEffort,  # pyright: ignore [reportAttributeAccessIssue]
    )
else:
    try:
        from openai.types.chat.chat_completion_audio_param import (  # pyright: ignore [reportMissingImports]
            ChatCompletionAudioParam,
            ChatCompletionModality,
        )
    except ImportError:

        class ChatCompletionAudioParam: ...

        class ChatCompletionModality: ...

    try:
        from openai.types.chat.chat_completion_reasoning_effort import (  # pyright: ignore [reportMissingImports]
            ChatCompletionReasoningEffort,
        )
    except ImportError:

        class ChatCompletionReasoningEffort: ...


class OpenAICallParams(BaseCallParams):
    """The parameters to use when calling the OpenAI API.

    [OpenAI API Reference](https://platform.openai.com/docs/api-reference/chat/create)

    Attributes:
        audio: ...
        frequency_penalty: ...
        logit_bias: ...
        logprobs: ...
        max_tokens: ...
        modalities: ...
        n: ...
        parallel_tool_calls: ...
        presence_penalty: ...
        reasoning_effort: ...
        response_format: ...
        seed: ...
        stop: ...
        stream_options: ...
        temperature: ...
        tool_choice: ...
        top_logprobs: ...
        top_p: ...
        user: ...
    """

    audio: NotRequired[ChatCompletionAudioParam | None]
    extra_headers: NotRequired[dict[str, str] | None]
    frequency_penalty: NotRequired[float | None]
    logit_bias: NotRequired[dict[str, int] | None]
    logprobs: NotRequired[bool | None]
    max_tokens: NotRequired[int | None]
    metadata: NotRequired[dict[str, str] | None]
    modalities: NotRequired[list[ChatCompletionModality] | None]
    n: NotRequired[int | None]
    parallel_tool_calls: NotRequired[bool]
    presence_penalty: NotRequired[float | None]
    reasoning_effort: NotRequired[ChatCompletionReasoningEffort | None]
    response_format: NotRequired[ResponseFormat]
    seed: NotRequired[int | None]
    stop: NotRequired[str | list[str] | None]
    stream_options: NotRequired[ChatCompletionStreamOptionsParam | None]
    temperature: NotRequired[float | None]
    tool_choice: NotRequired[ChatCompletionToolChoiceOptionParam]
    top_logprobs: NotRequired[int | None]
    top_p: NotRequired[float | None]
    user: NotRequired[str]
