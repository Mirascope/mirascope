"""OpenAI message types."""

from typing import TypeAlias

from openai.types.chat import ChatCompletionMessageParam

from ...messages import Message

OpenAIMessage: TypeAlias = Message | ChatCompletionMessageParam
