"""Base abstract converter for provider-specific message conversions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Generic, TypeVar

from ...content import AssistantContentPart, ContentPart
from ...messages import AssistantMessage, Message
from ...responses import FinishReason

# Type variables for provider-specific types
ProviderContentT = TypeVar("ProviderContentT")
ProviderMessagesInputT = TypeVar("ProviderMessagesInputT")
ProviderMessageResponseT = TypeVar("ProviderMessageResponseT")
ProviderContentBlockT = TypeVar("ProviderContentBlockT")
ProviderFinishReasonT = TypeVar("ProviderFinishReasonT")


class BaseConverter(
    ABC,
    Generic[
        ProviderContentT,
        ProviderMessagesInputT,
        ProviderMessageResponseT,
        ProviderContentBlockT,
        ProviderFinishReasonT,
    ],
):
    """Base abstract converter for provider-specific message conversions."""

    @classmethod
    @abstractmethod
    def encode_content(cls, content: Sequence[ContentPart]) -> ProviderContentT:
        """Convert mirascope content to provider-specific content format."""
        ...

    @classmethod
    @abstractmethod
    def encode_messages(cls, messages: Sequence[Message]) -> ProviderMessagesInputT:
        """Convert mirascope messages to provider-specific message format."""
        ...

    @classmethod
    @abstractmethod
    def decode_assistant_message(
        cls, message: ProviderMessageResponseT
    ) -> AssistantMessage:
        """Convert provider response message to mirascope AssistantMessage."""
        ...

    @classmethod
    @abstractmethod
    def decode_assistant_content(
        cls, content: ProviderContentBlockT
    ) -> AssistantContentPart:
        """Convert provider content to mirascope AssistantContentPart."""
        ...

    @classmethod
    @abstractmethod
    def decode_finish_reason(cls, reason: ProviderFinishReasonT | None) -> FinishReason:
        """Convert provider finish reason to mirascope FinishReason."""
        ...
