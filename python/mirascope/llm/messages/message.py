"""The `Message` class and its utility constructors."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, TypeAlias

from ..content import AssistantContentPart, Text, UserContentPart
from ..types import Jsonable

if TYPE_CHECKING:
    from ..providers import ModelId, ProviderId


@dataclass(kw_only=True)
class SystemMessage:
    """A system message that sets context and instructions for the conversation."""

    role: Literal["system"] = "system"
    """The role of this message. Always "system"."""

    content: Text
    """The content of this `SystemMesssage`."""


@dataclass(kw_only=True)
class UserMessage:
    """A user message containing input from the user."""

    role: Literal["user"] = "user"
    """The role of this message. Always "user"."""

    content: Sequence[UserContentPart]
    """The content of the user message."""

    name: str | None = None
    """A name identifying the creator of this message."""


@dataclass(kw_only=True)
class AssistantMessage:
    """An assistant message containing the model's response."""

    role: Literal["assistant"] = "assistant"
    """The role of this message. Always "assistant"."""

    content: Sequence[AssistantContentPart]
    """The content of the assistant message."""

    name: str | None = None
    """A name identifying the creator of this message."""

    provider_id: ProviderId | None
    """The LLM provider that generated this assistant message, if available."""

    model_id: ModelId | None
    """The model identifier of the LLM that generated this assistant message, if available."""

    provider_model_name: str | None
    """The provider-specific model identifier (e.g. "gpt-5:responses"), if available."""

    raw_message: Jsonable | None
    """The provider-specific raw representation of this assistant message, if available.

    If raw_content is truthy, then it may be used for provider-specific behavior when
    resuming an LLM interaction that included this assistant message. For example, we can
    reuse the provider-specific raw encoding rather than re-encoding the message from it's
    Mirascope content representation. This may also take advantage of server-side provider
    context, e.g. identifiers of reasoning context tokens that the provider generated.
    
    If present, the content should be encoded as JSON-serializable data, and in a format
    that matches representation the provider expects representing the Mirascope data.
    This may involve e.g.  converting Pydantic `BaseModel`s into plain dicts via `model_dump`.

    Raw content is not required, as the Mirascope content can also be used to generate
    a valid input to the provider (potentially without taking advantage of provider-specific
    reasoning caches, etc). In that case raw content should be left empty.
    """


Message: TypeAlias = SystemMessage | UserMessage | AssistantMessage
"""A message in an LLM interaction.

Messages have a role (system, user, or assistant) and content that is a sequence
of content parts. The content can include text, images, audio, documents, and
tool interactions.

For most use cases, prefer the convenience functions `system()`, `user()`, and
`assistant()` instead of directly creating `Message` objects.

Example:

    ```python
    from mirascope import llm

    messages = [
        llm.messages.system("You are a helpful assistant."),
        llm.messages.user("Hello, how are you?"),
    ]
    ```
"""

UserContent: TypeAlias = str | UserContentPart | Sequence[str | UserContentPart]
"""Type alias for content that can fit into a `UserMessage`."""

AssistantContent: TypeAlias = (
    str | AssistantContentPart | Sequence[str | AssistantContentPart]
)
"""Type alias for content that can fit into an `AssistantMessage`."""

SystemContent: TypeAlias = str | Text
"""Type alias for content that can fit into a `SystemMessage`."""


def system(content: SystemContent) -> SystemMessage:
    """Creates a system message.

    Args:
        content: The content of the message, which must be a `str` or `Text` content.

    Returns:
        A `SystemMessage`.
    """
    promoted_content = Text(text=content) if isinstance(content, str) else content
    return SystemMessage(content=promoted_content)


def user(
    content: UserContent,
    *,
    name: str | None = None,
) -> UserMessage:
    """Creates a user message.

    Args:
        content: The content of the message, which can be `str` or any `UserContent`,
            or a sequence of such user content pieces.
        name: Optional name to identify a specific user in multi-party conversations.

    Returns:
        A `UserMessage`.
    """
    if isinstance(content, str) or not isinstance(content, Sequence):
        content = [content]
    promoted_content = [
        Text(text=part) if isinstance(part, str) else part for part in content
    ]
    return UserMessage(content=promoted_content, name=name)


def assistant(
    content: AssistantContent,
    *,
    model_id: ModelId | None,
    provider_id: ProviderId | None,
    provider_model_name: str | None = None,
    raw_message: Jsonable | None = None,
    name: str | None = None,
) -> AssistantMessage:
    """Creates an assistant message.

    Args:
        content: The content of the message, which can be `str` or any `AssistantContent`,
            or a sequence of assistant content pieces.
        model_id: Optional id of the model that produced this message.
        provider_id: Optional identifier of the provider that produced this message.
        provider_model_name: Optional provider-specific model name. May include
            provider-specific additional info (like api mode in "gpt-5:responses").
        raw_message: Optional Jsonable object that contains the provider-specific
            "raw" data representation of the content for this assistant message.
        name: Optional name to identify a specific assistant in multi-party conversations.

    Returns:
        An `AssistantMessage`.
    """

    if isinstance(content, str) or not isinstance(content, Sequence):
        content = [content]
    promoted_content = [
        Text(text=part) if isinstance(part, str) else part for part in content
    ]
    return AssistantMessage(
        content=promoted_content,
        provider_id=provider_id,
        model_id=model_id,
        provider_model_name=provider_model_name,
        raw_message=raw_message,
        name=name,
    )
