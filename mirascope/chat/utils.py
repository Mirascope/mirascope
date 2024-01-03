"""Utility functions for mirascope chat."""

from typing import cast

from openai.types.chat import ChatCompletionMessageParam

from ..prompts import Prompt


def get_openai_chat_messages(
    prompt: Prompt,
) -> list[ChatCompletionMessageParam]:
    """Returns a list of messages parsed from the prompt."""
    return [
        cast(ChatCompletionMessageParam, {"role": role, "content": content})
        for role, content in prompt.messages
    ]
