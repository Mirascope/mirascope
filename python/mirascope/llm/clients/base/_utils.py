import logging
from collections.abc import Sequence
from typing import TypeAlias

from ...content import Text
from ...messages import AssistantMessage, Message, SystemMessage, UserMessage

SystemMessageContent: TypeAlias = str | None


def add_system_instructions(
    messages: Sequence[Message], instructions: str
) -> Sequence[Message]:
    if messages and messages[0].role == "system":
        if messages[0].content.text.endswith(instructions):
            return messages
        modified = Text(text=messages[0].content.text + "\n" + instructions)
        return [SystemMessage(role="system", content=modified), *messages[1:]]
    else:
        return [
            SystemMessage(role="system", content=Text(text=instructions)),
            *messages,
        ]


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
