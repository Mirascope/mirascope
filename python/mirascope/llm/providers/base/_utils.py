import logging
from collections.abc import Generator, Sequence
from contextlib import contextmanager
from typing import TYPE_CHECKING, TypeAlias, cast, get_type_hints

from ...content import Text
from ...messages import AssistantMessage, Message, SystemMessage, UserMessage
from ..provider_id import ProviderId
from .params import Params

if TYPE_CHECKING:
    from ..model_id import ModelId

logger = logging.getLogger(__name__)

SystemMessageContent: TypeAlias = str | None


def ensure_additional_properties_false(obj: object) -> None:
    """Recursively adds additionalProperties = False to a schema, required for strict mode."""
    if isinstance(obj, dict):
        obj = cast(dict[str, object], obj)
        if obj.get("type") == "object" and "additionalProperties" not in obj:
            obj["additionalProperties"] = False
        for value in obj.values():
            ensure_additional_properties_false(value)
    elif isinstance(obj, list):
        obj = cast(list[object], obj)
        for item in obj:
            ensure_additional_properties_false(item)


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
    system_message_content: SystemMessageContent = None
    remaining_messages: list[UserMessage | AssistantMessage] = []

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


class SafeParamsAccessor:
    """A wrapper around Params that tracks which parameters have been accessed."""

    def __init__(self, params: Params) -> None:
        self._params = params
        self._unaccessed = set(get_type_hints(Params).keys())

    @property
    def temperature(self) -> float | None:
        """Access the temperature parameter."""
        self._unaccessed.discard("temperature")
        return self._params.get("temperature")

    @property
    def max_tokens(self) -> int | None:
        """Access the max_tokens parameter."""
        self._unaccessed.discard("max_tokens")
        return self._params.get("max_tokens")

    @property
    def top_p(self) -> float | None:
        """Access the top_p parameter."""
        self._unaccessed.discard("top_p")
        return self._params.get("top_p")

    @property
    def top_k(self) -> int | None:
        """Access the top_k parameter."""
        self._unaccessed.discard("top_k")
        return self._params.get("top_k")

    @property
    def seed(self) -> int | None:
        """Access the seed parameter."""
        self._unaccessed.discard("seed")
        return self._params.get("seed")

    @property
    def stop_sequences(self) -> list[str] | None:
        """Access the stop_sequences parameter."""
        self._unaccessed.discard("stop_sequences")
        return self._params.get("stop_sequences")

    @property
    def thinking(self) -> bool | None:
        """Access the thinking parameter."""
        self._unaccessed.discard("thinking")
        return self._params.get("thinking")

    @property
    def encode_thoughts_as_text(self) -> bool | None:
        """Access the encode_thoughts_as_text parameter."""
        self._unaccessed.discard("encode_thoughts_as_text")
        return self._params.get("encode_thoughts_as_text")

    def emit_warning_for_unused_param(
        self,
        param_name: str,
        param_value: object,
        provider_id: "ProviderId",
        model_id: "ModelId | None" = None,
    ) -> None:
        unsupported_by = f"provider: {provider_id}"
        if model_id:
            unsupported_by += f" with model_id: {model_id}"
        logger.warning(
            f"Skipping unsupported parameter: {param_name}={param_value} ({unsupported_by})"
        )

    def check_access_integrity(self, unsupported_params: list[str]) -> None:
        """Verify that all used parameters have been accessed, and none of the unsupported have been."""
        assert self._unaccessed == set(unsupported_params), (
            "Mismatch between unsupported and unaccessed params"
        )


@contextmanager
def ensure_all_params_accessed(
    *,
    params: Params,
    provider_id: "ProviderId",
    unsupported_params: list[str] | None = None,
) -> Generator[SafeParamsAccessor, None, None]:
    """Context manager that ensures all parameters are accessed.

    Yields a wrapper around params that tracks which parameters have been accessed.
    On context exit, raises a `RuntimeError` if any parameters were not accessed.

    Args:
        params: The parameters to wrap
        provider: The provider that is accessing these params (required for logging)
        unsupported_params: A list of params keys it does not support, for auto-warning
            of unsupported params as boilerplate reduction. Or None, to disable this
            optional feature.

    Yields:
        A SafeParamsAccessor instance if params is not None, else None

    Raises:
        RuntimeError: If any parameters were not accessed before context exit
    """

    accessor = SafeParamsAccessor(params)
    unsupported_params = unsupported_params or []
    for unsupported in unsupported_params:
        if (val := params.get(unsupported)) is not None:
            accessor.emit_warning_for_unused_param(
                unsupported, val, provider_id=provider_id
            )
    try:
        yield accessor
    finally:
        accessor.check_access_integrity(unsupported_params=unsupported_params)
