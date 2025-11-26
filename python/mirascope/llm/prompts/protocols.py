"""Types for prompt functions."""

from typing import Any, Protocol, TypeVar

from ..context import Context, DepsT
from ..messages import Message, UserContent
from ..types import P

PromptT = TypeVar(
    "PromptT",
    bound="Prompt[...] | AsyncPrompt[...] | ContextPrompt[..., Any] | AsyncContextPrompt[..., Any]",
)
"""Type variable for prompt types.

This type var represents a resolved prompt, i.e. one that returns a list of messages.
"""


class Prompt(Protocol[P]):
    """Protocol for a `Prompt`, which returns `list[Message]`."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> list[Message]: ...


class Promptable(Protocol[P]):
    """Protocol for a `Promptable` that returns `UserContent` or `list[Message]`.

    May be be converted by the `prompt` decorator into a `Prompt`.
    """

    def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> UserContent | list[Message]: ...


class AsyncPrompt(Protocol[P]):
    """Protocol for an `AsyncPrompt`, which returns `list[Message]`."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> list[Message]: ...


class AsyncPromptable(Protocol[P]):
    """Protocol for an `AsyncPromptable` that returns `UserContent` or `list[Message]`.

    May be converted by the `prompt` decorator into an `AsyncPrompt`.
    """

    async def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> UserContent | list[Message]: ...


class ContextPrompt(Protocol[P, DepsT]):
    """Protocol for a `ContextPrompt`, which returns `list[Message]`."""

    def __call__(
        self,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> list[Message]: ...


class ContextPromptable(Protocol[P, DepsT]):
    """Protocol for a `ContextPromptable` that returns `UserContent` or `list[Message]`.

    May be converted by the `prompt` decorator into a `ContextPrompt`.
    """

    def __call__(
        self,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> UserContent | list[Message]: ...


class AsyncContextPrompt(Protocol[P, DepsT]):
    """Protocol for an `AsyncContextPrompt`, which returns `list[Message]`."""

    async def __call__(
        self,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> list[Message]: ...


class AsyncContextPromptable(Protocol[P, DepsT]):
    """Protocol for an `AsyncContextPromptable` that returns `UserContent` or `list[Message]`.

    May be converted by the `prompt` decorator into an `AsyncContextPrompt`.
    """

    async def __call__(
        self,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> UserContent | list[Message]: ...
