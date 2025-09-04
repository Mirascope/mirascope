"""The Call module for generating responses using LLMs."""

from dataclasses import dataclass
from typing import Generic, overload

from ..formatting import FormatT
from ..prompts import AsyncPrompt, Prompt, prompt
from ..responses import AsyncResponse, AsyncStreamResponse, Response, StreamResponse
from ..tools import (
    AsyncToolkit,
    Toolkit,
)
from ..types import P
from .base_call import BaseCall


@dataclass
class Call(BaseCall[P, Prompt, Toolkit, FormatT], Generic[P, FormatT]):
    """A class for generating responses using LLMs."""

    @overload
    def __call__(
        self: "Call[P, None]", *args: P.args, **kwargs: P.kwargs
    ) -> Response: ...

    @overload
    def __call__(
        self: "Call[P, FormatT]", *args: P.args, **kwargs: P.kwargs
    ) -> Response[FormatT]: ...

    def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Response | Response[FormatT]:
        """Generates a response using the LLM."""
        return self.call(*args, **kwargs)

    @overload
    def call(self: "Call[P, None]", *args: P.args, **kwargs: P.kwargs) -> Response: ...

    @overload
    def call(
        self: "Call[P, FormatT]", *args: P.args, **kwargs: P.kwargs
    ) -> Response[FormatT]: ...

    def call(self, *args: P.args, **kwargs: P.kwargs) -> Response | Response[FormatT]:
        """Generates a response using the LLM."""
        messages = prompt(self.fn)(*args, **kwargs)
        return self.model.call(
            messages=messages, tools=self.toolkit.tools, format=self.format
        )

    @overload
    def stream(
        self: "Call[P, None]", *args: P.args, **kwargs: P.kwargs
    ) -> StreamResponse: ...

    @overload
    def stream(
        self: "Call[P, FormatT]", *args: P.args, **kwargs: P.kwargs
    ) -> StreamResponse[FormatT]: ...

    def stream(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> StreamResponse | StreamResponse[FormatT]:
        """Generates a streaming response using the LLM."""
        messages = prompt(self.fn)(*args, **kwargs)
        return self.model.stream(
            messages=messages, tools=self.toolkit.tools, format=self.format
        )


@dataclass
class AsyncCall(
    BaseCall[P, AsyncPrompt, AsyncToolkit, FormatT],
    Generic[P, FormatT],
):
    """A class for generating responses using LLMs asynchronously."""

    @overload
    async def __call__(
        self: "AsyncCall[P, None]", *args: P.args, **kwargs: P.kwargs
    ) -> AsyncResponse: ...

    @overload
    async def __call__(
        self: "AsyncCall[P, FormatT]", *args: P.args, **kwargs: P.kwargs
    ) -> AsyncResponse[FormatT]: ...

    async def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncResponse | AsyncResponse[FormatT]:
        """Generates a Asyncresponse using the LLM asynchronously."""
        return await self.call(*args, **kwargs)

    @overload
    async def call(
        self: "AsyncCall[P, None]", *args: P.args, **kwargs: P.kwargs
    ) -> AsyncResponse: ...

    @overload
    async def call(
        self: "AsyncCall[P, FormatT]", *args: P.args, **kwargs: P.kwargs
    ) -> AsyncResponse[FormatT]: ...

    async def call(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncResponse | AsyncResponse[FormatT]:
        """Generates a response using the LLM asynchronously."""
        messages = await prompt(self.fn)(*args, **kwargs)
        return await self.model.call_async(
            messages=messages, tools=self.toolkit.tools, format=self.format
        )

    @overload
    async def stream(
        self: "AsyncCall[P, None]", *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStreamResponse: ...

    @overload
    async def stream(
        self: "AsyncCall[P, FormatT]", *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStreamResponse[FormatT]: ...

    async def stream(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStreamResponse[FormatT] | AsyncStreamResponse:
        """Generates a streaming response using the LLM asynchronously."""
        messages = await prompt(self.fn)(*args, **kwargs)
        return await self.model.stream_async(
            messages=messages, tools=self.toolkit.tools, format=self.format
        )
