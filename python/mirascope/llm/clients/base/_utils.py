import logging
from collections.abc import Sequence
from typing import TypeAlias, TypedDict

from ...content import Text
from ...messages import AssistantMessage, Message, SystemMessage, UserMessage
from .kwargs import KwargsT
from .params import Params

logger = logging.getLogger(__name__)

SystemMessageContent: TypeAlias = str | None


def add_system_instructions(
    messages: Sequence[Message], additional_system_instructions: str
) -> Sequence[Message]:
    """Add system instructions to a sequence of messages.

    If the first message is a system message, appends the additional instructions
    to it with a newline separator. If the instructions already exist at the end
    of the system message, returns the original messages unchanged. Otherwise,
    creates a new system message at the beginning of the sequence.

    Args:
        messages: The sequence of messages to modify.
        additional_system_instructions: The system instructions to add.

    Returns:
        A new sequence of messages with the system instructions added.
    """
    if messages and messages[0].role == "system":
        if messages[0].content.text.endswith(additional_system_instructions):
            return messages
        modified = Text(
            text=messages[0].content.text + "\n" + additional_system_instructions
        )
        return [SystemMessage(role="system", content=modified), *messages[1:]]
    else:
        return [
            SystemMessage(
                role="system", content=Text(text=additional_system_instructions)
            ),
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


class ParamsToKwargs(TypedDict, total=True):
    """A provider-specific map that defines how to process every key in Params"""

    temperature: str | None
    max_tokens: str | None
    top_p: str | None
    top_k: str | None
    seed: str | None
    stop_sequences: str | None


def map_params_to_kwargs(
    params: Params | None,
    kwargs: KwargsT,
    mapping: ParamsToKwargs,
    provider: str,
) -> KwargsT:
    """Map params into a provider-specific kwarg dict.

    Takes the params to map, the kwargs to update, and a mapping on how to handle params.
    The mapping must map from every parameter to one of three possible values, either:
    - a string key to map the parameter to in the kwargs dict, unchanged
    - None, if the parameter is unsupported

    If any used param is unsupported (not present in the mapping dict), then a runtime error will
    be raised.

    Logs a warning when a parameter is unsupported.
    """
    if not params:
        return kwargs
    kwargs = kwargs.copy()
    for param, value in params.items():
        if param not in mapping:
            raise RuntimeError(
                f"Parameter mapping missing parameter: {param}"
            )  # pragma: no cover
        kwarg = mapping[param]
        if kwarg is None:
            logger.warning(
                f"Skipping unsupported parameter: {param}={value} for provider {provider}"
            )
        else:
            kwargs[kwarg] = value

    return kwargs
