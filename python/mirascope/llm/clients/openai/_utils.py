"""OpenAI message types and conversion utilities."""

from collections.abc import Sequence

from openai.types.chat import (
    ChatCompletion,
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from ...content import (
    AssistantContentPart,
    ContentPart,
    Text,
)
from ...messages import AssistantMessage, Message, assistant
from ...responses import FinishReason

OPENAI_FINISH_REASON_MAP = {
    "stop": FinishReason.END_TURN,
    "length": FinishReason.MAX_TOKENS,
    "content_filter": FinishReason.REFUSAL,
    "tool_calls": FinishReason.TOOL_USE,
    "function_call": FinishReason.TOOL_USE,
}


def _encode_content(
    content: Sequence[ContentPart],
) -> str:
    """Convert mirascope content to OpenAI content format."""
    if len(content) == 1 and content[0].type == "text":
        return content[0].text
    raise NotImplementedError("Only single-content text responses are supported.")


def _decode_assistant_content(
    content: str,
) -> AssistantContentPart:
    """Convert OpenAI content to mirascope AssistantContentPart."""
    return Text(text=content)


def _encode_message(message: Message) -> ChatCompletionMessageParam:
    """Convert a Mirascope `Message` to OpenAI `ChatCompletionMessageParam` format.

    Args:
        message: A Mirascope message (system, user, or assistant)

    Returns:
        A list containing a single OpenAI `ChatCompletionMessageParam`
    """
    if message.role == "system":
        return ChatCompletionSystemMessageParam(
            role="system", content=message.content.text
        )

    elif message.role == "user":
        return ChatCompletionUserMessageParam(
            role="user", content=_encode_content(message.content)
        )

    elif message.role == "assistant":
        return ChatCompletionAssistantMessageParam(
            role="assistant", content=_encode_content(message.content)
        )

    else:
        raise ValueError(f"Unsupported role: {message.role}")  # pragma: no cover


def encode_messages(
    messages: Sequence[Message],
) -> Sequence[ChatCompletionMessageParam]:
    """Convert a sequence of Mirascope `Message` to OpenAI `ChatCompletionmessageParam`."""
    return [_encode_message(message) for message in messages]


def decode_response(response: ChatCompletion) -> tuple[AssistantMessage, FinishReason]:
    """Convert OpenAI ChatCompletion to mirascope AssistantMessage."""
    choice = response.choices[0]
    assistant_message = assistant(
        content=[_decode_assistant_content(choice.message.content or "")]
    )
    finish_reason = FinishReason.UNKNOWN
    if choice.finish_reason:
        finish_reason = OPENAI_FINISH_REASON_MAP.get(
            choice.finish_reason, FinishReason.UNKNOWN
        )
    return assistant_message, finish_reason
