"""The ContextCall module for generating responses using LLMs with context."""

from collections.abc import Sequence
from dataclasses import dataclass

from ..content import ToolCall, ToolOutput, UserContent
from ..context import Context, DepsT
from ..prompts import Prompt
from ..response_formatting import FormatT
from ..responses import Response
from ..streams import AsyncStream, BaseStream, Stream
from ..tools import ContextTool
from ..types import Jsonable, P
from .base_context_call import BaseContextCall


@dataclass
class ContextCall(BaseContextCall[P, Prompt, DepsT, FormatT]):
    """A class for generating responses using LLMs."""

    def __call__(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[DepsT, FormatT]:
        """Generates a response using the LLM."""
        raise NotImplementedError()

    def call(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[DepsT, FormatT]:
        """Generates a response using the LLM."""
        raise NotImplementedError()

    async def call_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Response[DepsT, FormatT]:
        """Generates an asynchronous response using the LLM."""
        raise NotImplementedError()

    def stream(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> Stream[DepsT, FormatT]:
        """Generates a streaming response using the LLM."""
        raise NotImplementedError()

    def stream_async(
        self, ctx: Context[DepsT], *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStream[DepsT, FormatT]:
        """Generates an asynchronous streaming response using the LLM."""
        raise NotImplementedError()

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

    def resume_stream_async(
        self,
        output: Response[DepsT, FormatT] | BaseStream[DepsT, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> AsyncStream[DepsT, FormatT]:
        """Generate a new async stream by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    def call_tool(self, ctx: Context[DepsT], tool_call: ToolCall) -> ToolOutput:
        """Call the tool specified by the LLM, returning a ToolOutput.

        May raise llm.ToolNotFoundError if there is no tool matching that name.
        May raise an exception from the tool call or tool validation."""
        raise NotImplementedError()

    def call_tools(
        self, ctx: Context[DepsT], tool_calls: Sequence[ToolCall]
    ) -> list[ToolOutput]:
        """Call the tools specified by the LLM, returning a list of ToolOutputs.

        May raise llm.ToolNotFoundError if there is no tool matching that name.
        May raise an exception from the tool call or tool validation."""
        raise NotImplementedError()

    def get_tool(self, tool_call: ToolCall) -> ContextTool[..., Jsonable, DepsT]:
        """Get the tool definition for the given tool call.

        May raise llm.ToolNotFoundError if there is no tool matching that name."""
        raise NotImplementedError()

    def get_tools(
        self, tool_calls: Sequence[ToolCall]
    ) -> list[ContextTool[..., Jsonable, DepsT]]:
        """Get the tool definitions for the given tool calls.

        May raise llm.ToolNotFoundError if there is no tool matching that name."""
        raise NotImplementedError()
