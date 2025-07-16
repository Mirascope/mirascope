"""The `BaseCall` class for LLM calls."""

from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic

from ..content import UserContent
from ..context import DepsT
from ..models import LLM
from ..prompts import PromptT
from ..response_formatting import FormatT
from ..responses import Response
from ..streams import AsyncStream, BaseStream, Stream
from ..tools import ToolkitT
from ..types import P


@dataclass
class BaseCall(Generic[P, PromptT, ToolkitT, FormatT], ABC):
    """A base class for generating responses using LLMs."""

    model: LLM
    """The LLM model used for generating responses."""

    toolkit: ToolkitT
    """The toolkit containing this call's tools."""

    response_format: type[FormatT] | None
    """The response format for the generated response."""

    fn: PromptT
    """The Prompt function that generates the Prompt."""


@dataclass
class BaseSyncCall(
    BaseCall[P, PromptT, ToolkitT, FormatT],
    Generic[P, PromptT, ToolkitT, FormatT, DepsT],
    ABC,
):
    def resume(
        self,
        output: Response[DepsT, FormatT] | BaseStream[DepsT, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> Response[DepsT, FormatT]:
        """Generate a new response by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    async def resume_async(
        self,
        output: Response[DepsT, FormatT] | BaseStream[DepsT, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> Response[DepsT, FormatT]:
        """Generate a new response asynchronously by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    def resume_stream(
        self,
        output: Response[DepsT, FormatT] | BaseStream[DepsT, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> Stream[DepsT, FormatT]:
        """Generate a new stream by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    async def resume_stream_async(
        self,
        output: Response[DepsT, FormatT] | BaseStream[DepsT, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> AsyncStream[DepsT, FormatT]:
        """Generate a new async stream by continuing from a previous output, plus new user content."""
        raise NotImplementedError()


@dataclass
class BaseAsyncCall(
    BaseCall[P, PromptT, ToolkitT, FormatT],
    Generic[P, PromptT, ToolkitT, FormatT, DepsT],
    ABC,
):
    async def resume(
        self,
        output: Response[DepsT, FormatT] | BaseStream[DepsT, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> Response[DepsT, FormatT]:
        """Generate a new response by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    async def resume_async(
        self,
        output: Response[DepsT, FormatT] | BaseStream[DepsT, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> Response[DepsT, FormatT]:
        """Generate a new response asynchronously by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    async def resume_stream(
        self,
        output: Response[DepsT, FormatT] | BaseStream[DepsT, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> AsyncStream[DepsT, FormatT]:
        """Generate a new stream by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    async def resume_stream_async(
        self,
        output: Response[DepsT, FormatT] | BaseStream[DepsT, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> AsyncStream[DepsT, FormatT]:
        """Generate a new async stream by continuing from a previous output, plus new user content."""
        raise NotImplementedError()
