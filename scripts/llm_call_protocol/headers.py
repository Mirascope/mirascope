"""Protocols for reusable type hints."""

from typing import (
    TypeVar,
)

_ParsedOutputT = TypeVar("_ParsedOutputT")
_ResponseModelT = TypeVar("_ResponseModelT")


try:
    from openai import AsyncAzureOpenAI, AsyncOpenAI, AzureOpenAI, OpenAI
    from openai.types.chat import (
        ChatCompletion,
        ChatCompletionChunk,
        ChatCompletionMessageParam,
        ChatCompletionUserMessageParam,
    )

    from mirascope.core.openai import (
        AsyncOpenAIDynamicConfig,
        OpenAIDynamicConfig,
        OpenAITool,
    )
except ImportError:
    AsyncOpenAIDynamicConfig = OpenAITool = OpenAIDynamicConfig = None
    AsyncAzureOpenAI = AsyncOpenAI = AzureOpenAI = OpenAI = None
    ChatCompletion = ChatCompletionChunk = ChatCompletionMessageParam = (
        ChatCompletionUserMessageParam
    ) = None
