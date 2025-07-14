"""The AsyncCall module for generating responses asynchronously using LLMs."""

from collections.abc import Sequence
from dataclasses import dataclass

from ..content import ToolCall, ToolOutput, UserContent
from ..prompts import AsyncPrompt
from ..response_formatting import FormatT
from ..responses import Response
from ..streams import AsyncStream, BaseStream
from ..tools import Tool
from ..types import P
from .base_call import BaseCall


@dataclass
class AsyncCall(BaseCall[P, AsyncPrompt, FormatT]):
    """A class for generating responses using LLMs asynchronously."""

    async def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Response[None, FormatT]:
        """Generates a response using the LLM asynchronously."""
        raise NotImplementedError()

    async def call(self, *args: P.args, **kwargs: P.kwargs) -> Response[None, FormatT]:
        """Generates a response using the LLM asynchronously."""
        raise NotImplementedError()

    async def call_async(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Response[None, FormatT]:
        """Generates an asynchronous response using the LLM."""
        raise NotImplementedError()

    def stream(self, *args: P.args, **kwargs: P.kwargs) -> AsyncStream[None, FormatT]:
        """Generates a streaming response using the LLM asynchronously."""
        raise NotImplementedError()

    def stream_async(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStream[None, FormatT]:
        """Generates an asynchronous streaming response using the LLM."""
        raise NotImplementedError()

    async def resume(
        self,
        output: Response[None, FormatT] | BaseStream[None, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> Response[None, FormatT]:
        """Generate a new response by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    async def resume_async(
        self,
        output: Response[None, FormatT] | BaseStream[None, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> Response[None, FormatT]:
        """Generate a new response asynchronously by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    def resume_stream(
        self,
        output: Response[None, FormatT] | BaseStream[None, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> AsyncStream[None, FormatT]:
        """Generate a new stream by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    def resume_stream_async(
        self,
        output: Response[None, FormatT] | BaseStream[None, FormatT],
        content: UserContent | Sequence[UserContent],
    ) -> AsyncStream[None, FormatT]:
        """Generate a new async stream by continuing from a previous output, plus new user content."""
        raise NotImplementedError()

    async def call_tool(self, tool_call: ToolCall) -> ToolOutput:
        """Call the tool specified by the LLM, returning a ToolOutput.

        May raise llm.ToolNotFoundError if there is no tool matching that name.
        May raise an exception from the tool call or tool validation."""
        raise NotImplementedError()

    async def call_tools(self, tool_calls: Sequence[ToolCall]) -> list[ToolOutput]:
        """Call the tools specified by the LLM, returning a list of ToolOutputs.

        May raise llm.ToolNotFoundError if there is no tool matching that name.
        May raise an exception from the tool call or tool validation."""
        raise NotImplementedError()

    def get_tool(self, tool_call: ToolCall) -> Tool:
        """Get the tool definition for the given tool call.

        May raise llm.ToolNotFoundError if there is no tool matching that name."""
        raise NotImplementedError()

    def get_tools(self, tool_calls: Sequence[ToolCall]) -> list[Tool]:
        """Get the tool definitions for the given tool calls.

        May raise llm.ToolNotFoundError if there is no tool matching that name."""
        raise NotImplementedError()
