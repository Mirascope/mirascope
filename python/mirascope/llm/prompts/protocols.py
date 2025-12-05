"""Types for prompt functions."""

from collections.abc import Sequence
from typing import Protocol

from ..context import Context, DepsT
from ..messages import Message, UserContent
from ..types import P


class MessageTemplate(Protocol[P]):
    """Protocol for a prompt function that returns `UserContent` or `Sequence[Message]`.

    A `MessageTemplate` is a raw function that returns prompt content. It can be
    converted by the `llm.prompt` decorator into a `Prompt` (callable with a `Model`),
    or by the `llm.call` decorator into a `Call` (`Prompt` + `Model`).
    """

    def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> UserContent | Sequence[Message]: ...


class AsyncMessageTemplate(Protocol[P]):
    """Protocol for an async prompt function that returns `UserContent` or `Sequence[Message]`.

    An async `MessageTemplate` that can be converted by the `llm.prompt` decorator
    into an `AsyncPrompt`, or by the `llm.call` decorator into an `AsyncCall`.
    """

    async def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> UserContent | Sequence[Message]: ...


class ContextMessageTemplate(Protocol[P, DepsT]):
    """Protocol for a context-aware prompt function that returns `UserContent` or `Sequence[Message]`.

    A `MessageTemplate` with a first parameter named `'ctx'` of type `Context[DepsT]`.
    Can be converted by the `llm.prompt` decorator into a `ContextPrompt`, or by
    the `llm.call` decorator into a `ContextCall`.
    """

    def __call__(
        self,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> UserContent | Sequence[Message]: ...


class AsyncContextMessageTemplate(Protocol[P, DepsT]):
    """Protocol for an async context-aware prompt function that returns `UserContent` or `Sequence[Message]`.

    An async `MessageTemplate` with a first parameter named `'ctx'` of type `Context[DepsT]`.
    Can be converted by the `llm.prompt` decorator into an `AsyncContextPrompt`, or by
    the `llm.call` decorator into an `AsyncContextCall`.
    """

    async def __call__(
        self,
        ctx: Context[DepsT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> UserContent | Sequence[Message]: ...
