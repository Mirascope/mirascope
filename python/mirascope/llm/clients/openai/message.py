"""OpenAI message types."""

from typing import TypeAlias

from openai.types.chat import ChatCompletionMessageParam

OpenAIMessage: TypeAlias = ChatCompletionMessageParam
