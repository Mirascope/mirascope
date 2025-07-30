"""The `BaseCall` class for LLM calls."""

from abc import ABC
from dataclasses import dataclass
from typing import Generic

from ..context import Context, DepsT
from ..formatting import FormatT
from ..messages import UserMessagePromotable
from ..models import LLM
from ..prompts import PromptT
from ..responses import AsyncStreamResponse, BaseStreamResponse, Response
from ..tools import ContextToolkit, ContextToolT, Toolkit, ToolkitT, ToolT
from ..types import P


@dataclass
class BC(Generic[P, PromptT, ToolkitT, FormatT], ABC):
    """A base class for generating responses using LLMs."""

    model: LLM
    """The LLM model used for generating responses."""

    toolkit: ToolkitT
    """The toolkit containing this call's tools."""

    format: type[FormatT] | None
    """The response format for the generated response."""

    fn: PromptT
    """The Prompt function that generates the Prompt."""


@dataclass
class BaseCall(
    BC[P, PromptT, Toolkit[ToolT], FormatT], Generic[P, PromptT, ToolT, FormatT]
):
    async def resume_async(
        self,
        output: Response[FormatT] | BaseStreamResponse,
        content: UserMessagePromotable,
    ) -> Response[FormatT]:
        """Generate a new response asynchronously by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    async def resume_stream_async(
        self,
        output: Response[FormatT] | BaseStreamResponse,
        content: UserMessagePromotable,
    ) -> AsyncStreamResponse[FormatT]:
        """Generate a new async stream by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    async def call_async(self, *args: P.args, **kwargs: P.kwargs) -> Response[FormatT]:
        """Generates an asynchronous response using the LLM."""
        raise NotImplementedError()

    async def stream_async(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStreamResponse[FormatT]:
        """Generates an asynchronous streaming response using the LLM."""
        raise NotImplementedError()


@dataclass
class BaseContextCall(
    BC[P, PromptT, ContextToolkit[ContextToolT, DepsT], FormatT],
    Generic[P, PromptT, ContextToolT, FormatT, DepsT],
):
    async def call_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[FormatT]:
        """Generates an asynchronous response using the LLM."""
        raise NotImplementedError()

    async def stream_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStreamResponse[FormatT]:
        """Generates an asynchronous streaming response using the LLM."""
        raise NotImplementedError()

    async def resume_async(
        self,
        ctx: Context[DepsT],
        output: Response[FormatT] | BaseStreamResponse,
        content: UserMessagePromotable,
    ) -> Response[FormatT]:
        """Generate a new response asynchronously by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    async def resume_stream_async(
        self,
        ctx: Context[DepsT],
        output: Response[FormatT] | BaseStreamResponse,
        content: UserMessagePromotable,
    ) -> AsyncStreamResponse[FormatT]:
        """Generate a new async stream by continuing from a previous output, plus new user content."""
        raise NotImplementedError()
