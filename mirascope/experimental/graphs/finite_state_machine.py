"""The `FiniteStateMachine` Class Implementation."""

import contextvars
import inspect
from collections.abc import Callable, Coroutine
from functools import wraps
from types import TracebackType
from typing import Any, Generic, ParamSpec, Protocol, overload

from typing_extensions import TypeVar

NoneType = type(None)
_DepsT = TypeVar("_DepsT", default=None)


class RunContext(Generic[_DepsT]):
    """The runtime context for the Finite State Machine (FSM).

    This class is used to store the state of the FSM and the data that is passed between
    nodes. Consumers of the FSM can update the context as needed to change the state of
    the FSM or pass information between nodes.

    At a minimum the `RunContext` should know:
    - The necessary dependencies for running the FSM.
    - The current state of the FSM.
    - The inputs to the current node being run.
    - The transition edges of the FSM.
    - Data that is shared between nodes.
    - The state history of the FSM execution.
    - Error states and fallback handling.
    - The queue of incoming requests and their context.

    The last point is important. For the FSM to be efficient, we must enable running
    nodes in parallel. This means that we need to be able to queue incoming requests
    and their context, and then run the nodes in parallel up to the set thread limit.

    Attributes:
        state (...): The current state of the FSM.
        inputs (...): The inputs to the current node being run.
        transitions (...): The transition edges of the FSM.
        data (...): Data that is shared between nodes.
        state_history (...): The state history of the FSM execution.
        error_states (...): Error states and fallback handling.
    """

    deps: _DepsT

    def __init__(self, deps: _DepsT, **data: dict[str, Any]) -> None:
        self.deps = deps
        for key, value in data.items():
            setattr(self, key, value)


# Use ContextVar instead of thread-local for async compatibility
# This automatically propagates across async boundaries
_CONTEXT_VAR: contextvars.ContextVar[RunContext[Any] | None] = contextvars.ContextVar(
    "fsm_context", default=None
)


class FSMContextManager(Generic[_DepsT]):
    """Context manager for FSM contexts that supports both sync and async patterns.

    This class implements both the synchronous context manager protocol
    (__enter__/__exit__) and the asynchronous context manager protocol
    (__aenter__/__aexit__), allowing it to be used with both `with` and
    `async with` statements.

    The context manager handles setting and resetting the context variable
    that stores the RunContext, ensuring proper propagation through async code.

    NOTE: This simplified implementation has some limitations with complex nested
    async calls across context boundaries. For nested nodes calling other nodes
    asynchronously after a context exit, the context may not be properly preserved.
    In these cases, using a compiled machine is recommended.

    NOTE: We implement stubs using the sync case because the async case is currently
    the same and does not require separate implementations. In the future we may update
    this to handle more complex async cases where the context e.g. pulls from an
    external source or something.

    Attributes:
        ctx: The RunContext that will be set as active during the context.
        token: The token returned by _CONTEXT_VAR.set() that is used to restore
            the previous context when exiting.
    """

    ctx: RunContext[_DepsT]
    token: contextvars.Token | None = None

    def __init__(self, ctx: RunContext[_DepsT]) -> None:
        """Initialize a new FSMContextManager.

        Args:
            ctx: The RunContext to use during this context.
        """
        self.ctx = ctx

    def __enter__(self) -> RunContext[_DepsT]:
        """Enter the context manager (synchronous).

        Sets the RunContext as the current context and returns it.

        Returns:
            The RunContext for use within the `with` block.
        """
        self.token = _CONTEXT_VAR.set(self.ctx)
        return self.ctx

    def __exit__(
        self,
        exc_type: type[BaseException],
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the context manager (synchronous).

        Restores the previous context that was active before entering.

        Args:
            exc_type: The exception type if an exception was raised in the with block.
            exc_val: The exception value if an exception was raised in the with block.
            exc_tb: The traceback if an exception was raised in the with block.
        """
        if self.token is not None:
            _CONTEXT_VAR.reset(self.token)
            self.token = None

    async def __aenter__(self) -> RunContext[_DepsT]:
        """Enter the context manager (asynchronous).

        Same as __enter__ but for use with `async with`.

        Returns:
            The RunContext for use within the `async with` block.
        """
        return self.__enter__()

    async def __aexit__(
        self,
        exc_type: type[BaseException],
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the context manager (asynchronous).

        Same as __exit__ but for use with `async with`.

        Args:
            exc_type: The exception type if an exception was raised in the with block.
            exc_val: The exception value if an exception was raised in the with block.
            exc_tb: The traceback if an exception was raised in the with block.
        """
        self.__exit__(exc_type, exc_val, exc_tb)


class FSMContextError(Exception):
    """Raised when a node is executed outside of a context manager."""

    pass


_NodeDecoratedFunctionP = ParamSpec("_NodeDecoratedFunctionP")
_NodeDecoratedFunctionR = TypeVar("_NodeDecoratedFunctionR", covariant=True)


class NodeDecoratedFunction(
    Protocol[_NodeDecoratedFunctionP, _NodeDecoratedFunctionR, _DepsT]
):
    """The protocol for functions decorated with the `node` decorator.

    This protocol enables enforcing that the first argument of any `node` decorated
    function must be `ctx: RunContext` to ensure that the function can access the global
    context of the FSM.
    """

    __name__: str

    def __call__(
        self,
        ctx: RunContext[_DepsT],
        *args: _NodeDecoratedFunctionP.args,
        **kwargs: _NodeDecoratedFunctionP.kwargs,
    ) -> _NodeDecoratedFunctionR: ...


_NodeDecoratorP = ParamSpec("_NodeDecoratorP")
_NodeDecoratorR = TypeVar("_NodeDecoratorR")


class NodeDecorator(Protocol[_DepsT]):
    """The `node` decorator protocol.

    This protocol enables overloading the `node` function such that it can detect and
    type async functions correctly. The `node` decorator is used to register a function
    as a node in the FSM, so the resulting function when run uncompiled should run just
    as the original function would (and thus required matching type hints).
    """

    @overload
    def __call__(
        self,
        fn: NodeDecoratedFunction[
            _NodeDecoratorP, Coroutine[Any, Any, _NodeDecoratorR], _DepsT
        ],
    ) -> Callable[_NodeDecoratorP, Coroutine[Any, Any, _NodeDecoratorR]]: ...

    @overload
    def __call__(
        self, fn: NodeDecoratedFunction[_NodeDecoratorP, _NodeDecoratorR, _DepsT]
    ) -> Callable[_NodeDecoratorP, _NodeDecoratorR]: ...

    def __call__(
        self,
        fn: NodeDecoratedFunction[
            _NodeDecoratorP,
            _NodeDecoratorR | Coroutine[Any, Any, _NodeDecoratorR],
            _DepsT,
        ],
    ) -> Callable[
        _NodeDecoratorP, _NodeDecoratorR | Coroutine[Any, Any, _NodeDecoratorR]
    ]: ...


_P = ParamSpec("_P")
_R = TypeVar("_R")


class FiniteStateMachine(Generic[_DepsT]):
    '''Automatical Finite State Machine (FSM) compiled from the code execution graph.

    This class provides a global `RunContext` and a `node` decorator that gives function
    it decorates access to the global context. The context is used to store the state
    of the FSM and the data that is passed between nodes. This means that the consumer
    of this class can update the context as needed to change the state of the FSM or
    pass information between nodes.

    Let's consider a very simple example of a FSM that increments a given value until it
    is divisible by a given divisor. The FSM has two nodes: `increment` and
    `divisible_by`. The `increment` node increments the given value by 1, and the
    `divisible_by` node checks if the value is divisible by the given divisor. If it is,
    the FSM returns the number of increments, otherwise it increments and divides again.

    The FSM might look something like this:

        +-----------+       +-----------+
        | increment | ----> |  divide   | <---- start value
        |           | <---- |           | ----> number of increments
        +-----------+       +-----------+

    The FSM has two nodes:
    - `increment`: Increments the given value by 1.
    - `divisible_by`: Checks if the value is divisible by the given divisor.

    Now, it would be fairly straightforward to implement this FSM by defining the nodes
    and the edges between them. However, the FSM can get very complex very quickly, and
    it would be nice to have a way to automatically compile the FSM from the code so
    that we can build arbitrarily complex systems without having to worry how to
    structure them. Once compiled, the code can be run as a finite state machine.

    What if we could just define the code?

    Example:

        ```python
        from dataclasses import dataclass

        @dataclass
        class Deps:
            operations: int = 0

        fsm = FiniteStateMachine(deps_type=Deps)

        @fsm.node()
        async def increment(ctx: RunContext[Deps], value: int) -> int:
            ctx.deps.operations += 1
            return value + 1

        @fsm.node()
        async def divide(ctx: RunContext[Deps], value: int, divisor: int) -> int:
            ctx.deps.operations += 1
            return value // divisor

        @fsm.node()
        async def reach_zero(ctx: RunContext[Deps], value: int, divisor: int) -> int:
            while value != 0:
                value = await increment(value)
                value = await divide(value, divisor)
            return ctx.deps.operations

        # in async running loop
        async with fsm.context(deps=Deps(0)) as ctx:
            operations = await reach_zero(5, 3)
            print(f"Operations: {operations}")
        ```

    What about an FSM that represents a librarian?

    Example:

        ```python
        import asyncio
        from dataclasses import dataclass

        from mirascope import BaseMessageParam, Messages, llm
        from mirascope import graphs as g


        @dataclass
        class Book
            title: str
            author: str


        @dataclass
        class Library:
            librarian: str
            messages: list[BaseMessageParam]
            all_books: list[Book]
            available_books: dict[str, bool]


        machine = g.FiniteStateMachine(deps_type=Library)


        @machine.node()
        @llm.tool()
        def all_books(ctx: g.RunContext[Library]) -> list[Book]:
            """Returns the titles of all books the library owns."""
            return ctx.deps.all_books


        @machine.node()
        @llm.tool()
        def book_is_available(ctx: g.RunContext[Library], title: str) -> str:
            """Returns the author of the book with the given title."""
            return ctx.deps.available_books[title]


        @machine.node()
        @llm.call("openai", "gpt-4o-mini", tools=[all_books, book_is_available])
        async def answer_question(ctx: g.RunContext[Library]) -> str:
            return f"You are a librarian named {ctx.deps.librarian}"


        @machine.node()
        async def handle_tools(ctx: g.RunContext[Library], tools: list[Tool]) -> None:
            tool_tasks = [tool.call() for tool in tools]
            tool_outputs = asyncio.gather(*tool_tasks)
            tools_and_outputs = [(tool, output) for tool, output in zip(tools, tools_outputs, strict=True)]
            ctx.deps.messages += llm.CallResponse.tool_message_params(tools_and_outputs)

        @machine.node()
        async def librarian(ctx: g.RunContext[Library], question: str) -> llm.CallResponse:
            response = await answer_question(question)
            if response.user_message_param:
                ctx.deps.messages.append(response.user_message_param)
            ctx.deps.messages.append(response.message_param)
            if tools := response.tools:
                await handle_tools(tools)
                return await answer_question("")
            return response


        agent = machine.compile(start=librarian)

        response = agent.run(
            "Do you carry The Name of the Wind? Is it available?",
            deps=Library(
                librarian="Mira",
                all_books=[
                    Book("The Name of the Wind", "Patrick Rothfuss"),
                    Book("Mistborn: The Final Empire", "Brandon Sanderson"),
                ],
                available_books={
                    "The Name of the Wind": True,
                    "Mistborn: The Final Empire": False,
                },
            )
        )
        print(response.content)
        ```

    Ultimately each node is fairly self-contained except for `librarian`, which can be
    thought of as it's own little sub-FSM or controller. The `librarian` node is the
    entry point to the FSM and is responsible for handling the incoming question,
    calling the `answer_question` node, and then handling the tools that are returned.
    The `answer_question` node is responsible for answering the question, and the
    `handle_tools` node is responsible for calling the tools and then returning the
    results.

    The compiled graph might look something like this:

                     +-----------------+       +-------------------+
        question --> | answer_question | ----> | _handle_response_ | --> response
                     +-----------------+       +-------------------+
                                    ^            |
                                    |            v
                                 +-------------------+
                                 |   handle_tools    |
                                 +-------------------+


    Inside the `librarian` function, really all we're doing is calling `answer_question`
    and then handling the response such that we either call any requested tools and call
    `answer_question` again, or we return the response. This is a very simple example,
    but it shows how we can build an efficient FSM without having to worry about the
    nitty gritty details of how the FSM is structured.

    We get to code. The FSM then builds itself.
    '''

    _deps_type: type[_DepsT]

    def __init__(self, *, deps_type: type[_DepsT] = NoneType) -> None:
        """Initializes an instance of `FiniteStateMachine`."""
        self._deps_type = deps_type

    def context(self, *, deps: _DepsT) -> FSMContextManager[_DepsT]:
        """Creates a context manager for the FSM that handles both sync and async.

        This method returns an instance of FSMContextManager which can be used with both
        `with` and `async with` statements. The context manager sets up a RunContext
        that all node-decorated functions will use while the context is active. The
        context is stored using contextvars.ContextVar which properly propagates through
        async code, allowing context to be maintained across await points and between
        nodes so long as each node is called within the context.

        Example:

            Synchronous usage:
            ```python
            with fsm.context(deps=Deps()) as ctx:
                result = increment(5)  # ctx is automatically passed
            ```

        Example:

            Asynchronous usage:
            ```python
            async with fsm.context(deps=Deps()) as ctx:
                result = await async_increment(5)  # ctx is automatically passed
            ```

        Args:
            deps: The dependencies for the FSM.

        Returns:
            An FSMContextManager instance that supports both `with` and `async with`.
        """
        ctx = RunContext(deps=deps)
        return FSMContextManager(ctx)

    def node(self) -> NodeDecorator[_DepsT]:
        """Registers the given function as a node in the FSM.

        This decorator transforms a function that requires a RunContext as its first
        parameter into a function that can be called without explicitly passing the
        context. The context is retrieved from contextvars.ContextVar which properly
        propagates through async code, ensuring that context is maintained across
        await points.

        This means that when a node calls another node, even asynchronously, the context
        is automatically propagated without any special handling. This allows for
        building complex node graphs with proper context flow.

        If the decorated function is called outside of a context manager, a
        FSMContextError will be raised.

        Returns:
            A decorator that registers the given function as a node in the FSM.
        """

        @overload
        def decorator(
            fn: NodeDecoratedFunction[_P, Coroutine[Any, Any, _R], _DepsT],
        ) -> Callable[_P, Coroutine[Any, Any, _R]]: ...

        @overload
        def decorator(
            fn: NodeDecoratedFunction[_P, _R, _DepsT],
        ) -> Callable[_P, _R]: ...

        def decorator(
            fn: NodeDecoratedFunction[_P, _R | Coroutine[Any, Any, _R], _DepsT],
        ) -> Callable[_P, _R | Coroutine[Any, Any, _R]]:
            @wraps(fn)
            def context_wrapper(
                *args: _P.args, **kwargs: _P.kwargs
            ) -> _R | Coroutine[Any, Any, _R]:
                context = _CONTEXT_VAR.get()
                if context is None:
                    raise FSMContextError(
                        f"Node `{fn.__name__}` called outside of a context manager. "
                        f"Use 'with fsm.context(deps=...)' to provide a context."
                    )

                if inspect.iscoroutinefunction(fn):
                    # For async functions, just create and return a coroutine with the
                    # context management inside so we handle contextvars correctly
                    @wraps(fn)
                    async def inner_async() -> _R:
                        async with FSMContextManager(context):
                            return await fn(context, *args, **kwargs)  # pyright: ignore [reportGeneralTypeIssues]

                    return inner_async()

                return fn(context, *args, **kwargs)

            return context_wrapper

        return decorator

    def compile(
        self,
        start: Callable[_P, _R],
        *,
        deps: _DepsT = None,
    ) -> "CompiledMachine[_P, _R, _DepsT]":
        """Returns the compiled FSM.

        Compiles the FSM and returns a CompiledMachine that can be used to run the FSM.
        The CompiledMachine will use the provided start function as the entry point to
        the FSM and will create a RunContext with the provided dependencies.

        Args:
            start: The entry point to the FSM.
            deps: The dependencies for the FSM.

        Returns:
            A CompiledMachine that can be used to run the FSM.
        """
        return CompiledMachine(fsm=self, start=start, deps=deps)


class CompiledMachine(Generic[_P, _R, _DepsT]):
    """The compiled Finite State Machine (FSM).

    This class represents a compiled FSM that can be run with a specific start function.
    The FSM will use the provided start function as the entry point and will create a
    RunContext with the provided dependencies when run.

    Attributes:
        fsm: The FiniteStateMachine that was compiled.
        start: The entry point to the FSM.
        deps: The dependencies for the FSM.
    """

    fsm: FiniteStateMachine[_DepsT]
    start: Callable[_P, _R]
    deps: _DepsT

    def __init__(
        self,
        *,
        fsm: FiniteStateMachine[_DepsT],
        start: Callable[_P, _R],
        deps: _DepsT = None,
    ) -> None:
        """Initializes an instance of `CompiledMachine`."""
        self.fsm = fsm
        self.start = start
        self.deps = deps

    def run(self, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        """Runs the FSM synchronously.

        This method runs the FSM using the specified start function and dependencies.
        It sets up a context manager to provide the RunContext for all node-decorated
        functions called during the execution of the FSM.

        This method should only be used with synchronous start functions. For async
        functions, use `run_async` instead.

        Args:
            *args: The positional arguments to pass to the start function.
            **kwargs: The keyword arguments to pass to the start function.

        Returns:
            The result of running the FSM.

        Raises:
            FSMContextError: If the start function or any node-decorated function is
                called outside of a context manager.
            RuntimeError: If called with an async function as the start function.
        """
        if inspect.iscoroutinefunction(self.start):
            raise RuntimeError(
                f"Cannot use run() with async function {self.start.__name__}. "
                f"Use run_async() instead."
            )

        with self.fsm.context(deps=self.deps):
            return self.start(*args, **kwargs)

    async def run_async(self, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        """Runs the FSM asynchronously.

        This method runs the FSM using the specified start function and dependencies.
        It sets up an async context manager to provide the RunContext for all node-decorated
        functions called during the execution of the FSM.

        This method should only be used with asynchronous start functions. For synchronous
        functions, use `run` instead.

        Args:
            *args: The positional arguments to pass to the start function.
            **kwargs: The keyword arguments to pass to the start function.

        Returns:
            The result of running the FSM.

        Raises:
            FSMContextError: If the start function or any node-decorated function is
                called outside of a context manager.
            RuntimeError: If called with a sync function as the start function.
        """
        async with self.fsm.context(deps=self.deps):
            result = self.start(*args, **kwargs)
            if inspect.isawaitable(result):
                return await result
            return result


async def main() -> None:
    from dataclasses import dataclass

    @dataclass
    class Deps:
        operations: int = 0

    fsm = FiniteStateMachine(deps_type=Deps)

    # Example 1: Using the FSM with synchronous functions
    print("Example 1: Using the FSM with synchronous functions")

    @fsm.node()
    def increment(ctx: RunContext[Deps], value: int) -> int:
        ctx.deps.operations += 1
        return value + 1

    @fsm.node()
    def divide(ctx: RunContext[Deps], value: int, divisor: int) -> int:
        ctx.deps.operations += 1
        return value // divisor

    @fsm.node()
    def reach_zero(ctx: RunContext[Deps], value: int, divisor: int) -> int:
        while value != 0:
            value = increment(value)
            value = divide(value, divisor)
        return ctx.deps.operations

    with fsm.context(deps=Deps(0)):
        operations = reach_zero(5, 3)
        print(f"Operations: {operations}")

    # Example 2: Run the compiled sync machine
    print("\nExample 2:  Run the compiled sync machine")
    machine = fsm.compile(start=reach_zero, deps=Deps(0))
    num_operations = machine.run(value=5, divisor=3)
    print(f"Compiled sync operations: {num_operations}")

    # # Define async nodes
    @fsm.node()
    async def async_increment(ctx: RunContext[Deps], value: int) -> int:
        ctx.deps.operations += 1
        return value + 1

    @fsm.node()
    async def async_divide(ctx: RunContext[Deps], value: int, divisor: int) -> int:
        ctx.deps.operations += 1
        return value // divisor

    @fsm.node()
    async def async_reach_zero(ctx: RunContext[Deps], value: int, divisor: int) -> int:
        while value != 0:
            value = await async_increment(value)
            value = await async_divide(value, divisor)
        return ctx.deps.operations

    # Example 3: Using synchronous context with async functions within boundaries
    print("\nExample 3: Synchronous context with async functions")
    with fsm.context(deps=Deps(0)):
        operations = await async_reach_zero(5, 3)
        print(f"Async operations in sync context: {operations}")

    # Example 3.5: Using asynchronous context with async functions within boundaries
    print("\nExample 3.5: Asynchronous context with async functions")
    async with fsm.context(deps=Deps(0)):
        operations = await async_reach_zero(5, 3)
        print(f"Async operations in async context: {operations}")

    # Example 4: Demonstrate context preservation across await boundaries
    print("\nContext preservation example:")
    async with fsm.context(deps=Deps(0)):
        # Create the coroutine task inside the context
        operations_task = async_reach_zero(5, 3)
        print("Task created inside context manager")
    # But await it outside the context - this will work because we preserve the context
    operations = await operations_task
    print(f"Task awaited outside context, operations: {operations}")

    # Example 5: Run the compiled async machine
    print("\nCompiled async machine example:")
    async_machine = fsm.compile(start=async_reach_zero, deps=Deps(0))
    async_num_operations = await async_machine.run_async(value=5, divisor=3)
    print(f"Compiled async operations: {async_num_operations}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
