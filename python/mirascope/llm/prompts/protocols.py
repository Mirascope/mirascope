"""Types for prompt functions."""

from collections.abc import Sequence
from typing import Any, Protocol, TypeVar

from ..context import Context, DepsT
from ..messages import Message, UserContent
from ..types import P

PromptT = TypeVar(
    "PromptT",
    bound="Prompt[...] | AsyncPrompt[...] | ContextPrompt[..., Any] | AsyncContextPrompt[..., Any]",
)
"""Type variable for prompt types.

This type var represents a resolved prompt, i.e. one that returns a Sequence of messages.
"""


class Prompt(Protocol[P]):
    """Protocol for a `Prompt`, which returns `Sequence[Message]`."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Sequence[Message]: ...


class Promptable(Protocol[P]):
    """Protocol for a `Promptable` that returns `UserContent` or `Sequence[Message]`.

    May be be converted by the `prompt` decorator into a `Prompt`.
    """

    def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> UserContent | Sequence[Message]: ...


class AsyncPrompt(Protocol[P]):
    """Protocol for an `AsyncPrompt`, which returns `Sequence[Message]`."""

    async def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Sequence[Message]: ...


class AsyncPromptable(Protocol[P]):
    """Protocol for an `AsyncPromptable` that returns `UserContent` or `Sequence[Message]`.

    May be converted by the `prompt` decorator into an `AsyncPrompt`.
    """

    async def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> UserContent | Sequence[Message]: ...


class ContextPrompt(Protocol[P, DepsT]):
    """Protocol for a `ContextPrompt`, which returns `Sequence[Message]`."""

    def __call__(
        self,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Sequence[Message]: ...


class ContextPromptable(Protocol[P, DepsT]):
    """Protocol for a `ContextPromptable` that returns `UserContent` or `Sequence[Message]`.

    May be converted by the `prompt` decorator into a `ContextPrompt`.
    """

    def __call__(
        self,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> UserContent | Sequence[Message]: ...


class AsyncContextPrompt(Protocol[P, DepsT]):
    """Protocol for an `AsyncContextPrompt`, which returns `Sequence[Message]`."""

    async def __call__(
        self,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Sequence[Message]: ...


class AsyncContextPromptable(Protocol[P, DepsT]):
    """Protocol for an `AsyncContextPromptable` that returns `UserContent` or `Sequence[Message]`.

    May be converted by the `prompt` decorator into an `AsyncContextPrompt`.
    """

    async def __call__(
        self,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> UserContent | Sequence[Message]: ...
