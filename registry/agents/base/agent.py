"""Mirascope Registry: Agent decorator with agentic loop and hooks.

This module provides an `@agent` decorator that transforms a prompt function into an
agent with an agentic loop. The agent automatically handles tool execution and supports
middleware hooks for observability and control.

Example:
    ```python
    from dataclasses import dataclass
    from mirascope import llm
    from ai.agents import agent, AgentHooks

    @dataclass
    class Library:
        librarian: str
        books: list[str]

    @llm.tool
    def get_books(ctx: llm.Context[Library]) -> list[str]:
        return ctx.deps.books

    @agent("openai/gpt-4", tools=[get_books])
    def librarian(ctx: llm.Context[Library]):
        return f"You are {ctx.deps.librarian}, the librarian."

    ctx = llm.Context(deps=Library(librarian="Nancy", books=["Dune"]))
    response = librarian(ctx, "What books do you have?")
    ```
"""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import AsyncIterator, Callable, Iterator, Sequence
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    Coroutine,
    Literal,
    Protocol,
    TypeVar,
    cast,
    get_type_hints,
    overload,
    runtime_checkable,
)

from typing_extensions import Concatenate, ParamSpec

from mirascope import llm

if TYPE_CHECKING:
    pass

P = ParamSpec("P")

DepsT = TypeVar("DepsT")

StopReason = Literal["no_tools", "max_turns", "should_stop", "format"]


# =============================================================================
# Hook Protocols
# =============================================================================


@runtime_checkable
class BeforeCallHook(Protocol):
    """Called before each LLM call in the agentic loop."""

    def __call__(
        self,
        messages: Sequence[llm.Message],
        turn: int,
    ) -> Sequence[llm.Message] | None:
        """Process messages before the LLM call.

        Args:
            messages: The messages that will be sent to the LLM.
            turn: The current turn number (0-indexed).

        Returns:
            Modified messages to use, or None to use the original messages.
        """
        ...


@runtime_checkable
class AfterCallHook(Protocol):
    """Called after each LLM call in the agentic loop."""

    def __call__(
        self,
        response: Any,
        turn: int,
    ) -> None:
        """Process the response after an LLM call.

        Args:
            response: The response from the LLM.
            turn: The current turn number (0-indexed).
        """
        ...


@runtime_checkable
class BeforeToolHook(Protocol):
    """Called before each tool execution."""

    def __call__(
        self,
        tool_call: llm.ToolCall,
        turn: int,
    ) -> llm.ToolCall | None:
        """Process a tool call before execution.

        Args:
            tool_call: The tool call to execute.
            turn: The current turn number (0-indexed).

        Returns:
            Modified tool call to use, or None to use the original.
        """
        ...


@runtime_checkable
class AfterToolHook(Protocol):
    """Called after each tool execution."""

    def __call__(
        self,
        tool_call: llm.ToolCall,
        tool_output: llm.ToolOutput[llm.Jsonable],
        turn: int,
    ) -> llm.ToolOutput[llm.Jsonable] | None:
        """Process a tool output after execution.

        Args:
            tool_call: The tool call that was executed.
            tool_output: The output from the tool.
            turn: The current turn number (0-indexed).

        Returns:
            Modified tool output to use, or None to use the original.
        """
        ...


@runtime_checkable
class OnErrorHook(Protocol):
    """Called when an error occurs during the agentic loop."""

    def __call__(
        self,
        error: Exception,
        turn: int,
        phase: Literal["call", "tool"],
    ) -> Exception | None:
        """Handle an error that occurred during the agentic loop.

        Args:
            error: The exception that was raised.
            turn: The current turn number (0-indexed).
            phase: Whether the error occurred during "call" or "tool" execution.

        Returns:
            Modified exception to raise, or None to suppress the error.
        """
        ...


@runtime_checkable
class OnStreamChunkHook(Protocol):
    """Called for each chunk during streaming."""

    def __call__(
        self,
        chunk: llm.StreamResponseChunk,
        turn: int,
    ) -> None:
        """Process a streaming chunk.

        Args:
            chunk: The streaming chunk.
            turn: The current turn number (0-indexed).
        """
        ...


@runtime_checkable
class OnFinishHook(Protocol):
    """Called when the agentic loop completes."""

    def __call__(
        self,
        response: Any,
        total_turns: int,
        stop_reason: StopReason,
    ) -> None:
        """Process the final response when the agent finishes.

        Args:
            response: The final response from the agent.
            total_turns: The total number of turns completed.
            stop_reason: Why the agent stopped.
        """
        ...


@dataclass
class AgentHooks:
    """Container for agent lifecycle hooks.

    All hooks can be either a single callable or a sequence of callables.
    When multiple hooks are provided, they are executed in order.

    Example:
        ```python
        def log_call(response, turn):
            print(f"Turn {turn}: {len(response.tool_calls)} tool calls")

        hooks = AgentHooks(
            after_call=log_call,
            on_finish=lambda r, t, reason: print(f"Done: {reason}")
        )

        @agent("openai/gpt-4", tools=[...], hooks=hooks)
        def my_agent(query: str):
            return f"Process: {query}"
        ```
    """

    before_call: BeforeCallHook | Sequence[BeforeCallHook] | None = None
    """Hook(s) called before each LLM call."""

    after_call: AfterCallHook | Sequence[AfterCallHook] | None = None
    """Hook(s) called after each LLM call."""

    before_tool: BeforeToolHook | Sequence[BeforeToolHook] | None = None
    """Hook(s) called before each tool execution."""

    after_tool: AfterToolHook | Sequence[AfterToolHook] | None = None
    """Hook(s) called after each tool execution."""

    on_error: OnErrorHook | Sequence[OnErrorHook] | None = None
    """Hook(s) called when an error occurs."""

    on_stream_chunk: OnStreamChunkHook | Sequence[OnStreamChunkHook] | None = None
    """Hook(s) called for each streaming chunk."""

    on_finish: OnFinishHook | Sequence[OnFinishHook] | None = None
    """Hook(s) called when the agent finishes."""

    def chain(self, other: AgentHooks) -> AgentHooks:
        """Compose two AgentHooks, running both in sequence.

        Args:
            other: Another AgentHooks to chain after this one.

        Returns:
            A new AgentHooks that runs both sets of hooks.
        """

        def merge(
            a: Any | Sequence[Any] | None, b: Any | Sequence[Any] | None
        ) -> Sequence[Any] | None:
            if a is None and b is None:
                return None
            a_list = (
                [] if a is None else ([a] if not isinstance(a, Sequence) else list(a))
            )
            b_list = (
                [] if b is None else ([b] if not isinstance(b, Sequence) else list(b))
            )
            return a_list + b_list or None

        return AgentHooks(
            before_call=merge(self.before_call, other.before_call),
            after_call=merge(self.after_call, other.after_call),
            before_tool=merge(self.before_tool, other.before_tool),
            after_tool=merge(self.after_tool, other.after_tool),
            on_error=merge(self.on_error, other.on_error),
            on_stream_chunk=merge(self.on_stream_chunk, other.on_stream_chunk),
            on_finish=merge(self.on_finish, other.on_finish),
        )


# =============================================================================
# Detection Utilities
# =============================================================================


def _is_context_fn(fn: Callable[..., Any]) -> bool:
    """Check if a function has a context parameter as its first argument."""
    sig = inspect.signature(fn)
    params = list(sig.parameters.values())
    if not params:
        return False
    first_param = params[0]
    if first_param.name != "ctx":
        return False
    # Check type hint
    try:
        hints = get_type_hints(fn)
        ctx_hint = hints.get("ctx")
        if ctx_hint is None:
            return False
        # Check if it's llm.Context or Context[T]
        origin = getattr(ctx_hint, "__origin__", None)
        if origin is llm.Context:
            return True
        return ctx_hint is llm.Context
    except Exception:
        return False


def _is_async_fn(fn: Callable[..., Any]) -> bool:
    """Check if a function is async."""
    return asyncio.iscoroutinefunction(fn)


# =============================================================================
# Hook Runners
# =============================================================================


def _run_before_call_hooks(
    hooks: AgentHooks | None,
    messages: Sequence[llm.Message],
    turn: int,
) -> Sequence[llm.Message]:
    """Run before_call hooks and return potentially modified messages."""
    if hooks is None or hooks.before_call is None:
        return messages
    hook_list: Sequence[BeforeCallHook] = (
        [hooks.before_call]
        if not isinstance(hooks.before_call, Sequence)
        else hooks.before_call
    )
    for hook in hook_list:
        result = hook(messages, turn)
        if result is not None:
            messages = result
    return messages


def _run_after_call_hooks(
    hooks: AgentHooks | None,
    response: Any,
    turn: int,
) -> None:
    """Run after_call hooks."""
    if hooks is None or hooks.after_call is None:
        return
    hook_list: Sequence[AfterCallHook] = (
        [hooks.after_call]
        if not isinstance(hooks.after_call, Sequence)
        else hooks.after_call
    )
    for hook in hook_list:
        hook(response, turn)


def _run_before_tool_hooks(
    hooks: AgentHooks | None,
    tool_call: llm.ToolCall,
    turn: int,
) -> llm.ToolCall:
    """Run before_tool hooks and return potentially modified tool call."""
    if hooks is None or hooks.before_tool is None:
        return tool_call
    hook_list: Sequence[BeforeToolHook] = (
        [hooks.before_tool]
        if not isinstance(hooks.before_tool, Sequence)
        else hooks.before_tool
    )
    for hook in hook_list:
        result = hook(tool_call, turn)
        if result is not None:
            tool_call = result
    return tool_call


def _run_after_tool_hooks(
    hooks: AgentHooks | None,
    tool_call: llm.ToolCall,
    tool_output: llm.ToolOutput[llm.Jsonable],
    turn: int,
) -> llm.ToolOutput[llm.Jsonable]:
    """Run after_tool hooks and return potentially modified output."""
    if hooks is None or hooks.after_tool is None:
        return tool_output
    hook_list: Sequence[AfterToolHook] = (
        [hooks.after_tool]
        if not isinstance(hooks.after_tool, Sequence)
        else hooks.after_tool
    )
    for hook in hook_list:
        result = hook(tool_call, tool_output, turn)
        if result is not None:
            tool_output = result
    return tool_output


def _run_on_error_hooks(
    hooks: AgentHooks | None,
    error: Exception,
    turn: int,
    phase: Literal["call", "tool"],
) -> Exception | None:
    """Run on_error hooks and return exception to raise or None to suppress."""
    if hooks is None or hooks.on_error is None:
        return error
    hook_list: Sequence[OnErrorHook] = (
        [hooks.on_error]
        if not isinstance(hooks.on_error, Sequence)
        else hooks.on_error
    )
    current_error: Exception | None = error
    for hook in hook_list:
        if current_error is not None:
            current_error = hook(current_error, turn, phase)
    return current_error


def _run_on_finish_hooks(
    hooks: AgentHooks | None,
    response: Any,
    total_turns: int,
    stop_reason: StopReason,
) -> None:
    """Run on_finish hooks."""
    if hooks is None or hooks.on_finish is None:
        return
    hook_list: Sequence[OnFinishHook] = (
        [hooks.on_finish]
        if not isinstance(hooks.on_finish, Sequence)
        else hooks.on_finish
    )
    for hook in hook_list:
        hook(response, total_turns, stop_reason)


def _build_tool_result_content(
    outputs: Sequence[llm.ToolOutput[llm.Jsonable]],
) -> list[llm.ToolOutput[llm.Jsonable]]:
    """Build user content with tool outputs."""
    return list(outputs)


# =============================================================================
# Agent Classes
# =============================================================================


@dataclass(kw_only=True)
class Agent:
    """A synchronous agent without context dependencies.

    Created by decorating a function with `@agent`. Provides an agentic loop
    that automatically executes tools until the LLM stops requesting them.
    """

    model: llm.Model
    """The model to use for LLM calls."""

    fn: Callable[..., str | Sequence[llm.Message]]
    """The prompt function that generates initial messages."""

    toolkit: llm.Toolkit
    """The toolkit containing available tools."""

    format: Any
    """Optional response format for structured output on final response."""

    max_turns: int
    """Maximum number of agentic turns."""

    should_stop: Callable[[Any], bool] | None
    """Optional callback to determine early stopping."""

    hooks: AgentHooks | None
    """Optional lifecycle hooks."""

    __name__: str = field(init=False, repr=False, default="")

    def __post_init__(self) -> None:
        self.__name__ = getattr(self.fn, "__name__", "")

    def _get_messages(self, *args: Any, **kwargs: Any) -> Sequence[llm.Message]:
        """Get messages from the prompt function."""
        result = self.fn(*args, **kwargs)
        if isinstance(result, str):
            return [llm.messages.system(result)]
        return result

    def __call__(
        self,
        user_message: str,
        *args: Any,
        **kwargs: Any,
    ) -> llm.Response[Any]:
        """Run the agent with a user message."""
        return self.run(user_message, *args, **kwargs)

    def run(
        self,
        user_message: str,
        *args: Any,
        **kwargs: Any,
    ) -> llm.Response[Any]:
        """Execute the agentic loop.

        Args:
            user_message: The user's input message.
            *args: Arguments to pass to the prompt function.
            **kwargs: Keyword arguments to pass to the prompt function.

        Returns:
            The final response from the agent.
        """
        # Build initial messages
        system_messages = list(self._get_messages(*args, **kwargs))
        messages: list[llm.Message] = system_messages + [
            llm.messages.user(user_message)
        ]

        turn = 0
        stop_reason: StopReason = "no_tools"
        response: llm.Response[Any] | None = None

        while turn < self.max_turns:
            # Run before_call hooks
            messages = list(_run_before_call_hooks(self.hooks, messages, turn))

            # Make LLM call (without format on intermediate turns)
            try:
                response = self.model.call(messages, tools=self.toolkit, format=None)
            except Exception as e:
                handled = _run_on_error_hooks(self.hooks, e, turn, "call")
                if handled is not None:
                    raise handled from None
                break

            # Run after_call hooks
            _run_after_call_hooks(self.hooks, response, turn)

            # Check stop conditions
            if not response.tool_calls:
                stop_reason = "no_tools"
                break

            if self.should_stop and self.should_stop(response):
                stop_reason = "should_stop"
                break

            # Execute tools with hooks
            outputs: list[llm.ToolOutput[llm.Jsonable]] = []
            for tool_call in response.tool_calls:
                try:
                    tool_call = _run_before_tool_hooks(self.hooks, tool_call, turn)
                    output = self.toolkit.execute(tool_call)
                    output = _run_after_tool_hooks(self.hooks, tool_call, output, turn)
                    outputs.append(output)
                except Exception as e:
                    handled = _run_on_error_hooks(self.hooks, e, turn, "tool")
                    if handled is not None:
                        raise handled from None

            # Build messages with tool results
            messages = list(response.messages) + [
                llm.messages.user(_build_tool_result_content(outputs))
            ]

            turn += 1

        if turn >= self.max_turns:
            stop_reason = "max_turns"

        # Final call with format if specified and we have a response
        if response is not None and self.format is not None:
            stop_reason = "format"
            messages = list(response.messages)
            response = self.model.call(messages, tools=None, format=self.format)

        if response is None:
            raise RuntimeError("Agent loop completed without generating a response")

        # Run on_finish hooks
        _run_on_finish_hooks(self.hooks, response, turn, stop_reason)

        return response

    def stream(
        self,
        user_message: str,
        *args: Any,
        **kwargs: Any,
    ) -> Iterator[llm.StreamResponseChunk]:
        """Execute the agentic loop with streaming.

        Yields chunks from each LLM call. Tool calls are accumulated and executed
        between streaming turns.

        Args:
            user_message: The user's input message.
            *args: Arguments to pass to the prompt function.
            **kwargs: Keyword arguments to pass to the prompt function.

        Yields:
            Streaming chunks from each turn.
        """
        system_messages = list(self._get_messages(*args, **kwargs))
        messages: list[llm.Message] = system_messages + [
            llm.messages.user(user_message)
        ]

        turn = 0
        stream_response: llm.StreamResponse[Any] | None = None

        while turn < self.max_turns:
            messages = list(_run_before_call_hooks(self.hooks, messages, turn))

            stream_response = self.model.stream(
                messages, tools=self.toolkit, format=None
            )

            for chunk in stream_response.chunk_stream():
                if self.hooks and self.hooks.on_stream_chunk:
                    hook_list: Sequence[OnStreamChunkHook] = (
                        [self.hooks.on_stream_chunk]
                        if not isinstance(self.hooks.on_stream_chunk, Sequence)
                        else self.hooks.on_stream_chunk
                    )
                    for hook in hook_list:
                        hook(chunk, turn)
                yield chunk

            # After consuming stream, the stream_response has the data
            _run_after_call_hooks(self.hooks, stream_response, turn)

            if not stream_response.tool_calls:
                _run_on_finish_hooks(self.hooks, stream_response, turn, "no_tools")
                return

            if self.should_stop and self.should_stop(stream_response):
                _run_on_finish_hooks(self.hooks, stream_response, turn, "should_stop")
                return

            # Execute tools
            outputs: list[llm.ToolOutput[llm.Jsonable]] = []
            for tool_call in stream_response.tool_calls:
                tool_call = _run_before_tool_hooks(self.hooks, tool_call, turn)
                output = self.toolkit.execute(tool_call)
                output = _run_after_tool_hooks(self.hooks, tool_call, output, turn)
                outputs.append(output)

            messages = list(stream_response.messages) + [
                llm.messages.user(_build_tool_result_content(outputs))
            ]
            turn += 1

        if stream_response is not None:
            _run_on_finish_hooks(self.hooks, stream_response, turn, "max_turns")


@dataclass(kw_only=True)
class AsyncAgent:
    """An asynchronous agent without context dependencies.

    Created by decorating an async function with `@agent`. Provides an agentic loop
    that automatically executes tools until the LLM stops requesting them.
    """

    model: llm.Model
    """The model to use for LLM calls."""

    fn: Callable[..., str | Sequence[llm.Message]]
    """The prompt function that generates initial messages."""

    toolkit: llm.AsyncToolkit
    """The toolkit containing available async tools."""

    format: Any
    """Optional response format for structured output on final response."""

    max_turns: int
    """Maximum number of agentic turns."""

    should_stop: Callable[[Any], bool] | None
    """Optional callback to determine early stopping."""

    hooks: AgentHooks | None
    """Optional lifecycle hooks."""

    __name__: str = field(init=False, repr=False, default="")

    def __post_init__(self) -> None:
        self.__name__ = getattr(self.fn, "__name__", "")

    def _get_messages(self, *args: Any, **kwargs: Any) -> Sequence[llm.Message]:
        """Get messages from the prompt function."""
        result = self.fn(*args, **kwargs)
        if isinstance(result, str):
            return [llm.messages.system(result)]
        return result

    async def __call__(
        self,
        user_message: str,
        *args: Any,
        **kwargs: Any,
    ) -> llm.AsyncResponse[Any]:
        """Run the agent with a user message."""
        return await self.run(user_message, *args, **kwargs)

    async def run(
        self,
        user_message: str,
        *args: Any,
        **kwargs: Any,
    ) -> llm.AsyncResponse[Any]:
        """Execute the agentic loop asynchronously.

        Args:
            user_message: The user's input message.
            *args: Arguments to pass to the prompt function.
            **kwargs: Keyword arguments to pass to the prompt function.

        Returns:
            The final response from the agent.
        """
        system_messages = list(self._get_messages(*args, **kwargs))
        messages: list[llm.Message] = system_messages + [
            llm.messages.user(user_message)
        ]

        turn = 0
        stop_reason: StopReason = "no_tools"
        response: llm.AsyncResponse[Any] | None = None

        while turn < self.max_turns:
            messages = list(_run_before_call_hooks(self.hooks, messages, turn))

            try:
                response = await self.model.call_async(
                    messages, tools=self.toolkit, format=None
                )
            except Exception as e:
                handled = _run_on_error_hooks(self.hooks, e, turn, "call")
                if handled is not None:
                    raise handled from None
                break

            _run_after_call_hooks(self.hooks, response, turn)

            if not response.tool_calls:
                stop_reason = "no_tools"
                break

            if self.should_stop and self.should_stop(response):
                stop_reason = "should_stop"
                break

            # Execute tools concurrently
            async def execute_tool(tc: llm.ToolCall) -> llm.ToolOutput[llm.Jsonable]:
                tc = _run_before_tool_hooks(self.hooks, tc, turn)
                output = await self.toolkit.execute(tc)
                return _run_after_tool_hooks(self.hooks, tc, output, turn)

            try:
                outputs = await asyncio.gather(
                    *[execute_tool(tc) for tc in response.tool_calls]
                )
            except Exception as e:
                handled = _run_on_error_hooks(self.hooks, e, turn, "tool")
                if handled is not None:
                    raise handled from None
                break

            messages = list(response.messages) + [
                llm.messages.user(_build_tool_result_content(list(outputs)))
            ]
            turn += 1

        if turn >= self.max_turns:
            stop_reason = "max_turns"

        if response is not None and self.format is not None:
            stop_reason = "format"
            messages = list(response.messages)
            response = await self.model.call_async(
                messages, tools=None, format=self.format
            )

        if response is None:
            raise RuntimeError("Agent loop completed without generating a response")

        _run_on_finish_hooks(self.hooks, response, turn, stop_reason)

        return response

    async def stream(
        self,
        user_message: str,
        *args: Any,
        **kwargs: Any,
    ) -> AsyncIterator[llm.StreamResponseChunk]:
        """Execute the agentic loop with async streaming.

        Yields chunks from each LLM call. Tool calls are accumulated and executed
        between streaming turns.

        Args:
            user_message: The user's input message.
            *args: Arguments to pass to the prompt function.
            **kwargs: Keyword arguments to pass to the prompt function.

        Yields:
            Streaming chunks from each turn.
        """
        system_messages = list(self._get_messages(*args, **kwargs))
        messages: list[llm.Message] = system_messages + [
            llm.messages.user(user_message)
        ]

        turn = 0
        stream_response: llm.AsyncStreamResponse[Any] | None = None

        while turn < self.max_turns:
            messages = list(_run_before_call_hooks(self.hooks, messages, turn))

            stream_response = await self.model.stream_async(
                messages, tools=self.toolkit, format=None
            )

            async for chunk in stream_response.chunk_stream():
                if self.hooks and self.hooks.on_stream_chunk:
                    hook_list: Sequence[OnStreamChunkHook] = (
                        [self.hooks.on_stream_chunk]
                        if not isinstance(self.hooks.on_stream_chunk, Sequence)
                        else self.hooks.on_stream_chunk
                    )
                    for hook in hook_list:
                        hook(chunk, turn)
                yield chunk

            _run_after_call_hooks(self.hooks, stream_response, turn)

            if not stream_response.tool_calls:
                _run_on_finish_hooks(self.hooks, stream_response, turn, "no_tools")
                return

            if self.should_stop and self.should_stop(stream_response):
                _run_on_finish_hooks(self.hooks, stream_response, turn, "should_stop")
                return

            async def execute_tool(tc: llm.ToolCall) -> llm.ToolOutput[llm.Jsonable]:
                tc = _run_before_tool_hooks(self.hooks, tc, turn)
                output = await self.toolkit.execute(tc)
                return _run_after_tool_hooks(self.hooks, tc, output, turn)

            outputs = await asyncio.gather(
                *[execute_tool(tc) for tc in stream_response.tool_calls]
            )

            messages = list(stream_response.messages) + [
                llm.messages.user(_build_tool_result_content(list(outputs)))
            ]
            turn += 1

        if stream_response is not None:
            _run_on_finish_hooks(self.hooks, stream_response, turn, "max_turns")


@dataclass(kw_only=True)
class ContextAgent:
    """A synchronous agent with context dependencies.

    Created by decorating a function with a `ctx: llm.Context[T]` first parameter
    with `@agent`. Provides an agentic loop with dependency injection.
    """

    model: llm.Model
    """The model to use for LLM calls."""

    fn: Callable[..., str | Sequence[llm.Message]]
    """The prompt function that generates initial messages."""

    toolkit: llm.ContextToolkit[Any]
    """The toolkit containing available context-aware tools."""

    format: Any
    """Optional response format for structured output on final response."""

    max_turns: int
    """Maximum number of agentic turns."""

    should_stop: Callable[[Any], bool] | None
    """Optional callback to determine early stopping."""

    hooks: AgentHooks | None
    """Optional lifecycle hooks."""

    __name__: str = field(init=False, repr=False, default="")

    def __post_init__(self) -> None:
        self.__name__ = getattr(self.fn, "__name__", "")

    def _get_messages(
        self, ctx: llm.Context[Any], *args: Any, **kwargs: Any
    ) -> Sequence[llm.Message]:
        """Get messages from the prompt function."""
        result = self.fn(ctx, *args, **kwargs)
        if isinstance(result, str):
            return [llm.messages.system(result)]
        return result

    def __call__(
        self,
        ctx: llm.Context[Any],
        user_message: str,
        *args: Any,
        **kwargs: Any,
    ) -> llm.ContextResponse[Any, Any]:
        """Run the agent with context and a user message."""
        return self.run(ctx, user_message, *args, **kwargs)

    def run(
        self,
        ctx: llm.Context[Any],
        user_message: str,
        *args: Any,
        **kwargs: Any,
    ) -> llm.ContextResponse[Any, Any]:
        """Execute the agentic loop with context.

        Args:
            ctx: The context containing dependencies.
            user_message: The user's input message.
            *args: Arguments to pass to the prompt function.
            **kwargs: Keyword arguments to pass to the prompt function.

        Returns:
            The final response from the agent.
        """
        system_messages = list(self._get_messages(ctx, *args, **kwargs))
        messages: list[llm.Message] = system_messages + [
            llm.messages.user(user_message)
        ]

        turn = 0
        stop_reason: StopReason = "no_tools"
        response: llm.ContextResponse[Any, Any] | None = None

        while turn < self.max_turns:
            messages = list(_run_before_call_hooks(self.hooks, messages, turn))

            try:
                response = self.model.context_call(
                    messages, ctx=ctx, tools=self.toolkit, format=None
                )
            except Exception as e:
                handled = _run_on_error_hooks(self.hooks, e, turn, "call")
                if handled is not None:
                    raise handled from None
                break

            _run_after_call_hooks(self.hooks, response, turn)

            if not response.tool_calls:
                stop_reason = "no_tools"
                break

            if self.should_stop and self.should_stop(response):
                stop_reason = "should_stop"
                break

            outputs: list[llm.ToolOutput[llm.Jsonable]] = []
            for tool_call in response.tool_calls:
                try:
                    tool_call = _run_before_tool_hooks(self.hooks, tool_call, turn)
                    output = self.toolkit.execute(ctx, tool_call)
                    output = _run_after_tool_hooks(self.hooks, tool_call, output, turn)
                    outputs.append(output)
                except Exception as e:
                    handled = _run_on_error_hooks(self.hooks, e, turn, "tool")
                    if handled is not None:
                        raise handled from None

            messages = list(response.messages) + [
                llm.messages.user(_build_tool_result_content(outputs))
            ]
            turn += 1

        if turn >= self.max_turns:
            stop_reason = "max_turns"

        if response is not None and self.format is not None:
            stop_reason = "format"
            messages = list(response.messages)
            response = self.model.context_call(
                messages, ctx=ctx, tools=None, format=self.format
            )

        if response is None:
            raise RuntimeError("Agent loop completed without generating a response")

        _run_on_finish_hooks(self.hooks, response, turn, stop_reason)

        return response

    def stream(
        self,
        ctx: llm.Context[Any],
        user_message: str,
        *args: Any,
        **kwargs: Any,
    ) -> Iterator[llm.StreamResponseChunk]:
        """Execute the agentic loop with streaming and context.

        Args:
            ctx: The context containing dependencies.
            user_message: The user's input message.
            *args: Arguments to pass to the prompt function.
            **kwargs: Keyword arguments to pass to the prompt function.

        Yields:
            Streaming chunks from each turn.
        """
        system_messages = list(self._get_messages(ctx, *args, **kwargs))
        messages: list[llm.Message] = system_messages + [
            llm.messages.user(user_message)
        ]

        turn = 0
        stream_response: llm.ContextStreamResponse[Any, Any] | None = None

        while turn < self.max_turns:
            messages = list(_run_before_call_hooks(self.hooks, messages, turn))

            stream_response = self.model.context_stream(
                messages, ctx=ctx, tools=self.toolkit, format=None
            )

            for chunk in stream_response.chunk_stream():
                if self.hooks and self.hooks.on_stream_chunk:
                    hook_list: Sequence[OnStreamChunkHook] = (
                        [self.hooks.on_stream_chunk]
                        if not isinstance(self.hooks.on_stream_chunk, Sequence)
                        else self.hooks.on_stream_chunk
                    )
                    for hook in hook_list:
                        hook(chunk, turn)
                yield chunk

            _run_after_call_hooks(self.hooks, stream_response, turn)

            if not stream_response.tool_calls:
                _run_on_finish_hooks(self.hooks, stream_response, turn, "no_tools")
                return

            if self.should_stop and self.should_stop(stream_response):
                _run_on_finish_hooks(self.hooks, stream_response, turn, "should_stop")
                return

            outputs: list[llm.ToolOutput[llm.Jsonable]] = []
            for tool_call in stream_response.tool_calls:
                tool_call = _run_before_tool_hooks(self.hooks, tool_call, turn)
                output = self.toolkit.execute(ctx, tool_call)
                output = _run_after_tool_hooks(self.hooks, tool_call, output, turn)
                outputs.append(output)

            messages = list(stream_response.messages) + [
                llm.messages.user(_build_tool_result_content(outputs))
            ]
            turn += 1

        if stream_response is not None:
            _run_on_finish_hooks(self.hooks, stream_response, turn, "max_turns")


@dataclass(kw_only=True)
class AsyncContextAgent:
    """An asynchronous agent with context dependencies.

    Created by decorating an async function with a `ctx: llm.Context[T]` first parameter
    with `@agent`. Provides an async agentic loop with dependency injection.
    """

    model: llm.Model
    """The model to use for LLM calls."""

    fn: Callable[..., str | Sequence[llm.Message]]
    """The prompt function that generates initial messages."""

    toolkit: llm.AsyncContextToolkit[Any]
    """The toolkit containing available async context-aware tools."""

    format: Any
    """Optional response format for structured output on final response."""

    max_turns: int
    """Maximum number of agentic turns."""

    should_stop: Callable[[Any], bool] | None
    """Optional callback to determine early stopping."""

    hooks: AgentHooks | None
    """Optional lifecycle hooks."""

    __name__: str = field(init=False, repr=False, default="")

    def __post_init__(self) -> None:
        self.__name__ = getattr(self.fn, "__name__", "")

    def _get_messages(
        self, ctx: llm.Context[Any], *args: Any, **kwargs: Any
    ) -> Sequence[llm.Message]:
        """Get messages from the prompt function."""
        result = self.fn(ctx, *args, **kwargs)
        if isinstance(result, str):
            return [llm.messages.system(result)]
        return result

    async def __call__(
        self,
        ctx: llm.Context[Any],
        user_message: str,
        *args: Any,
        **kwargs: Any,
    ) -> llm.AsyncContextResponse[Any, Any]:
        """Run the agent with context and a user message."""
        return await self.run(ctx, user_message, *args, **kwargs)

    async def run(
        self,
        ctx: llm.Context[Any],
        user_message: str,
        *args: Any,
        **kwargs: Any,
    ) -> llm.AsyncContextResponse[Any, Any]:
        """Execute the agentic loop asynchronously with context.

        Args:
            ctx: The context containing dependencies.
            user_message: The user's input message.
            *args: Arguments to pass to the prompt function.
            **kwargs: Keyword arguments to pass to the prompt function.

        Returns:
            The final response from the agent.
        """
        system_messages = list(self._get_messages(ctx, *args, **kwargs))
        messages: list[llm.Message] = system_messages + [
            llm.messages.user(user_message)
        ]

        turn = 0
        stop_reason: StopReason = "no_tools"
        response: llm.AsyncContextResponse[Any, Any] | None = None

        while turn < self.max_turns:
            messages = list(_run_before_call_hooks(self.hooks, messages, turn))

            try:
                response = await self.model.context_call_async(
                    messages, ctx=ctx, tools=self.toolkit, format=None
                )
            except Exception as e:
                handled = _run_on_error_hooks(self.hooks, e, turn, "call")
                if handled is not None:
                    raise handled from None
                break

            _run_after_call_hooks(self.hooks, response, turn)

            if not response.tool_calls:
                stop_reason = "no_tools"
                break

            if self.should_stop and self.should_stop(response):
                stop_reason = "should_stop"
                break

            async def execute_tool(tc: llm.ToolCall) -> llm.ToolOutput[llm.Jsonable]:
                tc = _run_before_tool_hooks(self.hooks, tc, turn)
                output = await self.toolkit.execute(ctx, tc)
                return _run_after_tool_hooks(self.hooks, tc, output, turn)

            try:
                outputs = await asyncio.gather(
                    *[execute_tool(tc) for tc in response.tool_calls]
                )
            except Exception as e:
                handled = _run_on_error_hooks(self.hooks, e, turn, "tool")
                if handled is not None:
                    raise handled from None
                break

            messages = list(response.messages) + [
                llm.messages.user(_build_tool_result_content(list(outputs)))
            ]
            turn += 1

        if turn >= self.max_turns:
            stop_reason = "max_turns"

        if response is not None and self.format is not None:
            stop_reason = "format"
            messages = list(response.messages)
            response = await self.model.context_call_async(
                messages, ctx=ctx, tools=None, format=self.format
            )

        if response is None:
            raise RuntimeError("Agent loop completed without generating a response")

        _run_on_finish_hooks(self.hooks, response, turn, stop_reason)

        return response

    async def stream(
        self,
        ctx: llm.Context[Any],
        user_message: str,
        *args: Any,
        **kwargs: Any,
    ) -> AsyncIterator[llm.StreamResponseChunk]:
        """Execute the agentic loop with async streaming and context.

        Args:
            ctx: The context containing dependencies.
            user_message: The user's input message.
            *args: Arguments to pass to the prompt function.
            **kwargs: Keyword arguments to pass to the prompt function.

        Yields:
            Streaming chunks from each turn.
        """
        system_messages = list(self._get_messages(ctx, *args, **kwargs))
        messages: list[llm.Message] = system_messages + [
            llm.messages.user(user_message)
        ]

        turn = 0
        stream_response: llm.AsyncContextStreamResponse[Any, Any] | None = None

        while turn < self.max_turns:
            messages = list(_run_before_call_hooks(self.hooks, messages, turn))

            stream_response = await self.model.context_stream_async(
                messages, ctx=ctx, tools=self.toolkit, format=None
            )

            async for chunk in stream_response.chunk_stream():
                if self.hooks and self.hooks.on_stream_chunk:
                    hook_list: Sequence[OnStreamChunkHook] = (
                        [self.hooks.on_stream_chunk]
                        if not isinstance(self.hooks.on_stream_chunk, Sequence)
                        else self.hooks.on_stream_chunk
                    )
                    for hook in hook_list:
                        hook(chunk, turn)
                yield chunk

            _run_after_call_hooks(self.hooks, stream_response, turn)

            if not stream_response.tool_calls:
                _run_on_finish_hooks(self.hooks, stream_response, turn, "no_tools")
                return

            if self.should_stop and self.should_stop(stream_response):
                _run_on_finish_hooks(self.hooks, stream_response, turn, "should_stop")
                return

            async def execute_tool(tc: llm.ToolCall) -> llm.ToolOutput[llm.Jsonable]:
                tc = _run_before_tool_hooks(self.hooks, tc, turn)
                output = await self.toolkit.execute(ctx, tc)
                return _run_after_tool_hooks(self.hooks, tc, output, turn)

            outputs = await asyncio.gather(
                *[execute_tool(tc) for tc in stream_response.tool_calls]
            )

            messages = list(stream_response.messages) + [
                llm.messages.user(_build_tool_result_content(list(outputs)))
            ]
            turn += 1

        if stream_response is not None:
            _run_on_finish_hooks(self.hooks, stream_response, turn, "max_turns")


# =============================================================================
# Decorator
# =============================================================================


@dataclass(kw_only=True)
class AgentDecorator:
    """Decorator class for creating agents from prompt functions."""

    model: llm.Model
    """The model to use for LLM calls."""

    tools: Sequence[Any] | None
    """Tools available to the agent."""

    format: Any
    """Response format for structured output on final response."""

    max_turns: int
    """Maximum number of agentic turns."""

    should_stop: Callable[[Any], bool] | None
    """Optional callback to determine early stopping."""

    hooks: AgentHooks | None
    """Optional lifecycle hooks."""

    @overload
    def __call__(  # pyright: ignore[reportOverlappingOverload]
        self,
        fn: Callable[
            Concatenate[llm.Context[Any], P],
            Coroutine[Any, Any, str | Sequence[llm.Message]],
        ],
    ) -> AsyncContextAgent: ...

    @overload
    def __call__(  # pyright: ignore[reportOverlappingOverload]
        self,
        fn: Callable[Concatenate[llm.Context[Any], P], str | Sequence[llm.Message]],
    ) -> ContextAgent: ...

    @overload
    def __call__(
        self,
        fn: Callable[P, Coroutine[Any, Any, str | Sequence[llm.Message]]],
    ) -> AsyncAgent: ...

    @overload
    def __call__(
        self,
        fn: Callable[P, str | Sequence[llm.Message]],
    ) -> Agent: ...

    def __call__(
        self,
        fn: Callable[..., str | Sequence[llm.Message] | Coroutine[Any, Any, str | Sequence[llm.Message]]],
    ) -> Agent | AsyncAgent | ContextAgent | AsyncContextAgent:
        """Decorate a function to create an agent."""
        is_context = _is_context_fn(fn)
        is_async = _is_async_fn(fn)

        # Cast fn to the expected type for each branch.
        # The runtime checks above ensure correctness.
        sync_fn = cast(Callable[..., str | Sequence[llm.Message]], fn)

        if is_context and is_async:
            toolkit = llm.AsyncContextToolkit(self.tools)
            return AsyncContextAgent(
                model=self.model,
                fn=sync_fn,
                toolkit=toolkit,
                format=self.format,
                max_turns=self.max_turns,
                should_stop=self.should_stop,
                hooks=self.hooks,
            )
        elif is_context:
            toolkit = llm.ContextToolkit(self.tools)
            return ContextAgent(
                model=self.model,
                fn=sync_fn,
                toolkit=toolkit,
                format=self.format,
                max_turns=self.max_turns,
                should_stop=self.should_stop,
                hooks=self.hooks,
            )
        elif is_async:
            toolkit = llm.AsyncToolkit(self.tools)
            return AsyncAgent(
                model=self.model,
                fn=sync_fn,
                toolkit=toolkit,
                format=self.format,
                max_turns=self.max_turns,
                should_stop=self.should_stop,
                hooks=self.hooks,
            )
        else:
            toolkit = llm.Toolkit(self.tools)
            return Agent(
                model=self.model,
                fn=sync_fn,
                toolkit=toolkit,
                format=self.format,
                max_turns=self.max_turns,
                should_stop=self.should_stop,
                hooks=self.hooks,
            )


def agent(
    model: llm.ModelId | llm.Model,
    *,
    tools: Sequence[Any] | None = None,
    format: Any = None,
    max_turns: int = 10,
    should_stop: Callable[[Any], bool] | None = None,
    hooks: AgentHooks | None = None,
) -> AgentDecorator:
    """Decorator that transforms a prompt function into an agent with an agentic loop.

    The agent automatically handles tool execution and continues the conversation
    until the LLM stops requesting tools, hits max_turns, or the should_stop
    callback returns True.

    Args:
        model: The model to use, either as a string ID or Model instance.
        tools: Optional sequence of tools available to the agent.
        format: Optional response format for structured output on the final response.
        max_turns: Maximum number of tool-use turns (default 10).
        should_stop: Optional callback that receives each response and returns True
            to stop the loop early.
        hooks: Optional AgentHooks for lifecycle callbacks.

    Returns:
        A decorator that creates an Agent from the prompt function.

    Example:
        ```python
        from mirascope import llm
        from ai.agents import agent

        @llm.tool
        def search(query: str) -> str:
            return f"Results for: {query}"

        @agent("openai/gpt-4", tools=[search])
        def researcher(topic: str):
            return f"Research everything about {topic}."

        response = researcher("quantum computing")
        print(response.text())
        ```
    """
    if isinstance(model, str):
        model = llm.Model(model)

    return AgentDecorator(
        model=model,
        tools=tools,
        format=format,
        max_turns=max_turns,
        should_stop=should_stop,
        hooks=hooks,
    )


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    # Main decorator
    "agent",
    "AgentDecorator",
    # Agent classes
    "Agent",
    "AsyncAgent",
    "ContextAgent",
    "AsyncContextAgent",
    # Hooks
    "AgentHooks",
    "BeforeCallHook",
    "AfterCallHook",
    "BeforeToolHook",
    "AfterToolHook",
    "OnErrorHook",
    "OnStreamChunkHook",
    "OnFinishHook",
    # Types
    "StopReason",
]
