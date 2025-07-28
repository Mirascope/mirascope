"""Types for prompt functions."""

from typing import Protocol, TypeAlias, TypeVar

from ..context import Context, DepsT
from ..messages import Message, UserMessagePromotable
from ..types import P


class MessagesPrompt(Protocol[P]):
    """Protocol for a prompt function that returns a list of messages."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> list[Message]: ...


class ContentPrompt(Protocol[P]):
    """Protocol for a Prompt function that returns content for a single user message."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> UserMessagePromotable: ...


Prompt: TypeAlias = ContentPrompt[P] | MessagesPrompt[P]
"""A function that can be promoted to a prompt.

A `Prompt` function takes input arguments `P` and returns one of:
  - `UserMessagePromotable` content that will be rendered as a single user message
  - A list of `Message` objects that will be rendered as-is
"""


class AsyncMessagesPrompt(Protocol[P]):
    """Protocol for a prompt function that returns a list of messages."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> list[Message]: ...


class AsyncContentPrompt(Protocol[P]):
    """Protocol for a prompt function that returns content for a single user message."""

    async def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> UserMessagePromotable: ...


AsyncPrompt: TypeAlias = AsyncContentPrompt[P] | AsyncMessagesPrompt[P]
"""An asynchronous Prompt function.

An `AsyncPrompt` function takes input arguments `P` and returns one of:
  - `UserMessagePromotable` content that will be rendered as a single user message
  - A list of `Message` objects that will be rendered as-is
"""


class ContextMessagesPrompt(Protocol[P, DepsT]):
    """Protocol for a context prompt function that returns a list of messages."""

    def __call__(
        self,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> list[Message]: ...


class ContextContentPrompt(Protocol[P, DepsT]):
    """Protocol for a context Prompt function that returns content for a single user message."""

    def __call__(
        self,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> UserMessagePromotable: ...


ContextPrompt: TypeAlias = (
    ContextContentPrompt[P, DepsT] | ContextMessagesPrompt[P, DepsT]
)
"""A context Prompt function.

A `ContextPrompt` function takes input arguments `Context[DepsT]` and `P` and
returns one of:
  - `UserMessagePromotable` content that will be rendered as a single user message
  - A list of `Message` objects that will be rendered as-is
"""


class AsyncContextMessagesPrompt(Protocol[P, DepsT]):
    """Protocol for a context prompt function that returns a list of messages."""

    async def __call__(
        self,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> list[Message]: ...


class AsyncContextContentPrompt(Protocol[P, DepsT]):
    """Protocol for a context prompt function that returns content for a single user message."""

    async def __call__(
        self,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> UserMessagePromotable: ...


AsyncContextPrompt: TypeAlias = (
    AsyncContextContentPrompt[P, DepsT] | AsyncContextMessagesPrompt[P, DepsT]
)
"""An asynchronous context Prompt function.

An `AsyncContextPrompt` function takes input arguments `Context[DepsT]` and `P` and
returns one of:
  - `UserMessagePromotable` content that will be rendered as a single user message
  - A list of `Message` objects that will be rendered as-is
"""

PromptT = TypeVar("PromptT", bound=Prompt | AsyncPrompt)
"""Type variable for prompt types.

This TypeVar represents either synchronous Prompt or asynchronous AsyncPrompt
function types. It's used in generic classes and functions that work with
both prompt variants.
"""
