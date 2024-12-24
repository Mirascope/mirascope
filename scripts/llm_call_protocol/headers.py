"""Protocols for reusable type hints."""

from collections.abc import (
    AsyncIterable,
    Callable,
    Iterable,
)
from typing import (
    Any,
    Literal,
    NoReturn,
    Protocol,
    TypeVar,
    overload,
)

from mirascope.core import BaseTool
from mirascope.core.base import BaseCallParams
from mirascope.core.base.stream_config import StreamConfig
from mirascope.llm._protocols import (
    AsyncLLMFunctionDecorator,
    LLMFunctionDecorator,
    SyncLLMFunctionDecorator,
)
from mirascope.llm.call_response import CallResponse
from mirascope.llm.call_response_chunk import CallResponseChunk
from mirascope.llm.stream import Stream

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


