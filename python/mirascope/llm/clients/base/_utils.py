import logging
from collections.abc import Sequence
from typing import TypeAlias

from ...messages import AssistantMessage, Message, UserMessage

SystemMessage: TypeAlias = str | None


def _extract_system_message(
    messages: Sequence[Message],
) -> tuple[SystemMessage, Sequence[UserMessage | AssistantMessage]]:
    """Extract the system message(s) from a list of Messages.

    This takes a list of messages, and returns the list of messages with
    all system messages removed, as well as the system message if present.

    This is intended for use in clients where the system message is not included in the
    input messages, but passed as an additional argument or metadata.

    If there were multiple system messages, they will be concatenated together
    into a single system message, joined by newlines. In this case, a warning
    will be emitted.
    """
    system_message = None
    output = []

    for i, message in enumerate(messages):
        if message.role == "system":
            if i == 0:
                system_message = message.content.text
            else:
                logging.warning(
                    "Skipping system message at index %d because it is not the first message",
                    i,
                )
        else:
            output.append(message)

    return system_message, output
