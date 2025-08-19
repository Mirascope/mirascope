import json
import logging
from collections.abc import Iterable, Sequence
from typing import TypeAlias

from ...content import Text
from ...formatting import FormatInfo
from ...messages import AssistantMessage, Message, SystemMessage, UserMessage
from ...responses import FinishReason
from ...tools import FORMAT_TOOL_NAME

SystemMessageContent: TypeAlias = str | None


def add_system_instructions(
    messages: Sequence[Message], instructions: Iterable[str]
) -> Sequence[Message]:
    combined_instructions = "\n".join(instructions)
    if messages and messages[0].role == "system":
        if messages[0].content.text.endswith(combined_instructions):
            return messages
        modified = Text(text=messages[0].content.text + "\n" + combined_instructions)
        return [SystemMessage(role="system", content=modified), *messages[1:]]
    else:
        return [
            SystemMessage(role="system", content=Text(text=combined_instructions)),
            *messages,
        ]


def handle_format_tool_response(
    assistant_message: AssistantMessage,
    finish_reason: FinishReason,
) -> tuple[AssistantMessage, FinishReason]:
    """Process an `AssistantMessage` and `FinishReason`, converting calls to the canonical formatting tool.

    If the message contains a tool call to the special reserved FORMAT_TOOL_NAME, that
    tool call is re-written into text containing the args to the tool call. If the finish
    reason was FinishReason.TOOL_CALL, it is converted to FinishReason.END_TURN.

    Args:
        assistant_message: The original assistant message
        finish_reason: The original finish reason

    Returns:
        Tuple of (modified_message, modified_finish_reason)
    """
    new_content = []
    format_tool_found = False

    for part in assistant_message.content:
        if part.type == "tool_call" and part.name == FORMAT_TOOL_NAME:
            new_content.append(Text(text=part.args))
            format_tool_found = True
        else:
            new_content.append(part)

    if format_tool_found and finish_reason == FinishReason.TOOL_USE:
        finish_reason = FinishReason.END_TURN

    return AssistantMessage(content=new_content), finish_reason


def extract_system_message(
    messages: Sequence[Message],
) -> tuple[SystemMessageContent, Sequence[UserMessage | AssistantMessage]]:
    """Extract the system message(s) from a list of Messages.

    This takes a list of messages, and returns the list of messages with
    all system messages removed, as well as the textual contents of the first message,
    if that message was a system message. If there are any system messages that are
    not the first message, they will be dropped, and a warning will be emitted.

    This is intended for use in clients where the system message is not included in the
    input messages, but passed as an additional argument or metadata.
    """
    system_message_content = None
    remaining_messages = []

    for i, message in enumerate(messages):
        if message.role == "system":
            if i == 0:
                system_message_content = message.content.text
            else:
                logging.warning(
                    "Skipping system message at index %d because it is not the first message",
                    i,
                )
        else:
            remaining_messages.append(message)

    return system_message_content, remaining_messages


def create_json_mode_instructions(format_info: FormatInfo) -> str:
    """Create formatting instructions for JSON mode from `FormatInfo`.

    Args:
        format_info: The `FormatInfo` instance containing schema and metadata

    Returns:
        Instructions string for JSON mode formatting

    Note: This does not include `format_info.description`, under the assumption that
    this code path is only invoked in json mode, but the client code will separately add
    the description in all formatting code paths.
    """

    schema_str = json.dumps(format_info.schema, indent=2)
    instructions = f"Respond with valid JSON that matches this exact schema:\n\n```json\n{schema_str}\n```"

    return instructions
