"""Base abstract converter for provider-specific message conversions."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Generic, TypeAlias, TypeVar

from ...messages import AssistantMessage, Message
from ...responses import FinishReason

ProviderMessagesInputT = TypeVar("ProviderMessagesInputT")
ProviderMessageResponseT = TypeVar("ProviderMessageResponseT")

OptionalSystemMessage: TypeAlias = str | None


class _BaseConverter(
    ABC,
    Generic[
        ProviderMessagesInputT,
        ProviderMessageResponseT,
    ],
):
    """Base abstract converter for provider-specific message conversions."""

    @classmethod
    @abstractmethod
    def encode_message(cls, message: Message) -> list[ProviderMessagesInputT]:
        """Convert a Mirascope message to a provider-specific representation.

        Some provider APIs may require converting a single Mirascope message into
        multiple distinct provider message inputs, e.g. the OpenAI Responses API
        which separates tool outputs from user messages.

        To maintain generality, this interface expects encode_message to return a list
        of provider message inputs (which may be a list containing a single item in
        many cases).

        If the client is only going to call encode_non_system_messages,
        then it is safe to assert message.role != system within this function.
        """
        ...

    @classmethod
    def encode_messages(
        cls, messages: Sequence[Message]
    ) -> list[ProviderMessagesInputT]:
        """Convert mirascope messages to provider-specific message format.

        This method will attempt to encode all messages, including the system message.
        It should be used when the system message itself corresponds to a
        ProviderMessagesInputT.
        """
        results: list[ProviderMessagesInputT] = []
        for message in messages:
            results.extend(cls.encode_message(message))
        return results

    @classmethod
    def encode_non_system_messages(
        cls, messages: Sequence[Message]
    ) -> tuple[OptionalSystemMessage, list[ProviderMessagesInputT]]:
        """Convert mirascope non-system messages to provider-specific message format.

        This method should be used when the system message does not correspond to a
        ProviderMessagesInputT, but rather is extra metadata. In this case, we will extract
        the system message as a string *if it is the first message* and return it separately.

        If there are any system messages that are not the first message, they will be
        skipped and a warning will be emitted.
        """
        system_message = None
        results: list[ProviderMessagesInputT] = []
        for i, message in enumerate(messages):
            if message.role != "system":
                results.extend(cls.encode_message(message))
            elif i == 0:
                system_message = message.content.text
            else:
                logging.warning(
                    "Skipping system message at index %d because it is not the first message",
                    i,
                )
        return system_message, results

    @classmethod
    @abstractmethod
    def decode_response(
        cls, response: ProviderMessageResponseT
    ) -> tuple[AssistantMessage, FinishReason]:
        """Convert provider response message to mirascope AssistantMessage and FinishReason."""
        ...
