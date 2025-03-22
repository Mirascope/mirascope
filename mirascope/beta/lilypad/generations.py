"""The `generations` module for automatically versioning and tracing LLM generations."""

import inspect
import json
import os
import typing
from collections.abc import Callable, Coroutine, Generator
from contextlib import contextmanager
from contextvars import ContextVar, Token
from enum import Enum
from functools import wraps
from typing import (
    Any,
    Generic,
    Literal,
    ParamSpec,
    Protocol,
    TypeAlias,
    TypeVar,
    cast,
    overload,
)
from uuid import UUID

from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import get_tracer_provider
from opentelemetry.util.types import AttributeValue

from mirascope import llm
from mirascope.core import prompt_template
from mirascope.core.base import CommonCallParams
from mirascope.core.base.types import Provider
from mirascope.llm.call_response import CallResponse

from ._utils import (
    ArgTypes,
    ArgValues,
    Closure,
    DependencyInfo,
    call_safely,
    create_mirascope_middleware,
    fn_is_async,
    inspect_arguments,
    jsonable_encoder,
    load_config,
)
from ._utils.middleware import SpanContextHolder
from .ee.generations import (
    specific_generation_version_async_factory,
    specific_generation_version_sync_factory,
)
from .exceptions import LilypadNotFoundError
from .traces import TraceDecorator, _trace

_P = ParamSpec("_P")
_R = TypeVar("_R")
_R_CO = TypeVar("_R_CO", covariant=True)
T = TypeVar("T")


def _get_batch_span_processor() -> BatchSpanProcessor | None:
    """Get the BatchSpanProcessor from the current TracerProvider.

    Retrieve the BatchSpanProcessor from the current TracerProvider dynamically.
    This avoids using a global variable by inspecting the provider's _active_span_processors.
    """
    tracer_provider = get_tracer_provider()
    processor = getattr(tracer_provider, "_active_span_processor", None)
    if not processor:
        return None
    _span_processors = getattr(processor, "_span_processors", None)
    if _span_processors:
        for processor in _span_processors:
            if isinstance(processor, BatchSpanProcessor):
                return processor
    return None


class GenerationMode(str, Enum):
    """Enum for generation return mode."""

    NO_WRAP = "no-wrap"
    WRAP = "wrap"


T_co = TypeVar("T_co", covariant=True)


class Generation(Generic[T]):
    """Container for a generation output, its metadata, and the associated trace/span ID."""

    def __init__(
        self,
        output: T,
        metadata: GenerationPublic,
        trace_id: int | None = None,
        span_id: int | None = None,
    ) -> None:
        """Initialize a Generation instance.

        Args:
            output: The generated output.
            metadata: The generation metadata.
            trace_id: Optional trace ID for this specific run.
            span_id: Optional span ID for this specific run
        """
        self.output = output
        self.metadata = metadata
        self.trace_id = trace_id
        self.span_id = span_id

        self.uuid: UUID = metadata.uuid
        self.name: str = metadata.name
        self.signature: str = metadata.signature
        self.version_num: int | None = metadata.version_num
        self.model: str | None = metadata.model
        self.provider: str | None = metadata.provider

    def __repr__(self) -> str:
        """String representation of Generation."""
        return (
            f"Generation(name='{self.name}', version={self.version_num}, "
            f"trace_id='{self.trace_id}', span_id='{self.span_id}' , output={self.output})"
        )


GenerationDecorator: TypeAlias = TraceDecorator

current_generation: ContextVar[GenerationPublic | None] = ContextVar(
    "current_generation", default=None
)

# Type definitions for decorator registry
FunctionInfo: TypeAlias = tuple[
    str, str, int, str
]  # (file_path, function_name, line_number, module_name)
DecoratorRegistry: TypeAlias = dict[str, list[FunctionInfo]]

# Globals for decorator registry
_RECORDING_ENABLED: bool = False
_DECORATOR_REGISTRY: DecoratorRegistry = {}  # Maps decorator names to lists of function info


def enable_recording() -> None:
    """Enable recording of decorated functions."""
    global _RECORDING_ENABLED
    _RECORDING_ENABLED = True


def disable_recording() -> None:
    """Disable recording of decorated functions."""
    global _RECORDING_ENABLED
    _RECORDING_ENABLED = False


def clear_registry() -> None:
    """Clear the registry of decorated functions."""
    global _DECORATOR_REGISTRY
    _DECORATOR_REGISTRY = {}


def register_decorated_function(decorator_name: str, fn: Callable[..., Any]) -> None:
    """Register a function that has been decorated.

    Args:
        decorator_name: The name of the decorator
        fn: The decorated function
    """
    if not _RECORDING_ENABLED:
        return

    try:
        # Get function information
        file_path: str = inspect.getfile(fn)
        abs_path: str = os.path.abspath(file_path)
        lineno: int = inspect.getsourcelines(fn)[1]
        # Use Closure.from_fn to get the wrapped function name
        function_name: str = Closure.from_fn(fn).name
        module_name: str = fn.__module__

        # Add to registry
        if decorator_name not in _DECORATOR_REGISTRY:
            _DECORATOR_REGISTRY[decorator_name] = []

        # Store (file_path, function_name, line_number, module_name)
        _DECORATOR_REGISTRY[decorator_name].append(
            (abs_path, function_name, lineno, module_name)
        )
    except (TypeError, OSError):
        # Handle cases where inspect might fail (e.g., built-in functions)
        pass


def get_decorated_functions(decorator_name: str | None = None) -> DecoratorRegistry:
    """Get information about registered decorated functions.

    Args:
        decorator_name: Optional name of decorator to filter by

    Returns:
        Dictionary mapping decorator names to lists of function information tuples
    """
    if decorator_name:
        return {decorator_name: _DECORATOR_REGISTRY.get(decorator_name, [])}
    return _DECORATOR_REGISTRY.copy()


class SyncGenerationFunction(Protocol[_P, _R_CO]):
    """Protocol for the `generation` decorator return type."""

    def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R_CO:
        """Protocol for the `generation` decorator return type."""
        ...

    def version(
        self,
        forced_version: int,
        sandbox_runner: SandboxRunner | None = None,
    ) -> Callable[_P, _R_CO]:
        """Protocol for the `generation` decorator return type."""
        ...


class AsyncGenerationFunction(Protocol[_P, _R_CO]):
    """Protocol for the `generation` decorator return type."""

    def __call__(
        self, *args: _P.args, **kwargs: _P.kwargs
    ) -> Coroutine[Any, Any, _R_CO]:
        """Protocol for the `generation` decorator return type."""
        ...

    def version(
        self,
        forced_version: int,
        sandbox_runner: SandboxRunner | None = None,
    ) -> Coroutine[Any, Any, Callable[_P, Coroutine[Any, Any, _R_CO]]]:
        """Protocol for the `generation` decorator return type."""
        ...


class SyncGenerationWrapFunction(Protocol[_P, _R]):
    """Protocol for the `generation` decorator return type with wrap mode."""

    def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> Generation[_R]:
        """Protocol for the `generation` decorator return type."""
        ...

    def version(
        self,
        forced_version: int,
        sandbox_runner: SandboxRunner | None = None,
    ) -> Callable[_P, Generation[_R]]:
        """Protocol for the `generation` decorator return type."""
        ...


class AsyncGenerationWrapFunction(Protocol[_P, _R]):
    """Protocol for the `generation` decorator return type with wrap mode."""

    def __call__(
        self, *args: _P.args, **kwargs: _P.kwargs
    ) -> Coroutine[Any, Any, Generation[_R]]:
        """Protocol for the `generation` decorator return type."""
        ...

    def version(
        self,
        forced_version: int,
        sandbox_runner: SandboxRunner | None = None,
    ) -> Coroutine[Any, Any, Callable[_P, Coroutine[Any, Any, Generation[_R]]]]:
        """Protocol for the `generation` decorator return type."""
        ...


class GenerationVersioningDecorator(Protocol):
    """Protocol for the `generation` decorator return type."""

    @overload
    def __call__(  # pyright: ignore [reportOverlappingOverload]
        self, fn: Callable[_P, Coroutine[Any, Any, _R]]
    ) -> AsyncGenerationFunction[_P, _R]: ...

    @overload
    def __call__(self, fn: Callable[_P, _R]) -> SyncGenerationFunction[_P, _R]: ...

    def __call__(
        self, fn: Callable[_P, _R] | Callable[_P, Coroutine[Any, Any, _R]]
    ) -> SyncGenerationFunction[_P, _R] | AsyncGenerationFunction[_P, _R]:
        """Protocol `call` definition for `generation` decorator return type."""
        ...


class ManagedGenerationVersioningDecorator(Protocol):
    """Protocol for the `generation` decorator return type."""

    @overload
    def __call__(  # pyright: ignore [reportOverlappingOverload]
        self, fn: Callable[_P, Coroutine[Any, Any, _R]]
    ) -> AsyncGenerationFunction[_P, Message | Stream]: ...

    @overload
    def __call__(
        self, fn: Callable[_P, _R]
    ) -> SyncGenerationFunction[_P, Message | Stream]: ...

    def __call__(
        self, fn: Callable[_P, _R] | Callable[_P, Coroutine[Any, Any, _R]]
    ) -> (
        SyncGenerationFunction[_P, Message | Stream]
        | AsyncGenerationFunction[_P, Message | Stream]
    ):
        """Protocol `call` definition for `generation` decorator return type."""
        ...


class GenerationVersioningWrapDecorator(Protocol):
    """Protocol for the `generation` decorator return type with wrap mode."""

    @overload
    def __call__(  # pyright: ignore [reportOverlappingOverload]
        self, fn: Callable[_P, Coroutine[Any, Any, _R]]
    ) -> AsyncGenerationWrapFunction[_P, _R]: ...

    @overload
    def __call__(self, fn: Callable[_P, _R]) -> SyncGenerationWrapFunction[_P, _R]: ...

    def __call__(
        self, fn: Callable[_P, _R] | Callable[_P, Coroutine[Any, Any, _R]]
    ) -> SyncGenerationWrapFunction[_P, _R] | AsyncGenerationWrapFunction[_P, _R]:
        """Protocol `call` definition for `generation` decorator return type."""
        ...


class ManagedGenerationVersioningWrapDecorator(Protocol):
    """Protocol for the `generation` decorator return type with wrap mode."""

    @overload
    def __call__(  # pyright: ignore [reportOverlappingOverload]
        self, fn: Callable[_P, Coroutine[Any, Any, _R]]
    ) -> AsyncGenerationWrapFunction[_P, Message | Stream]: ...

    @overload
    def __call__(
        self, fn: Callable[_P, _R]
    ) -> SyncGenerationWrapFunction[_P, Message | Stream]: ...

    def __call__(
        self, fn: Callable[_P, _R] | Callable[_P, Coroutine[Any, Any, _R]]
    ) -> (
        SyncGenerationWrapFunction[_P, Message | Stream]
        | AsyncGenerationWrapFunction[_P, Message | Stream]
    ):
        """Protocol `call` definition for `generation` decorator return type."""
        ...


@contextmanager
def _outermost_lock_context(enable_lock: bool) -> Generator[None, None, None]:
    """Acquire the BatchSpanProcessor's condition lock if enable_lock is True.

    This context manager is intended for use in the outermost generation.
    When enable_lock is True, it retrieves the current BatchSpanProcessor and acquires its
    condition lock. This ensures that flush operations are synchronized and only executed
    at the outermost generation level.
    For inner generations (enable_lock is False), no lock is acquired.
    """
    if not enable_lock:
        yield
        return
    processor = _get_batch_span_processor()
    if not processor:
        yield
        return
    with processor.condition:
        yield


def _construct_trace_attributes(
    generation: GenerationPublic,
    arg_values: ArgValues,
) -> dict[str, AttributeValue]:
    jsonable_arg_values = {}
    for arg_name, arg_value in arg_values.items():
        try:
            serialized_arg_value = jsonable_encoder(arg_value)
        except ValueError:
            serialized_arg_value = "could not serialize"
        jsonable_arg_values[arg_name] = serialized_arg_value
    return {
        "lilypad.generation.uuid": str(generation.uuid),
        "lilypad.generation.name": generation.name,
        "lilypad.generation.signature": generation.signature,
        "lilypad.generation.code": generation.code,
        "lilypad.generation.arg_types": json.dumps(generation.arg_types),
        "lilypad.generation.arg_values": json.dumps(jsonable_arg_values),
        "lilypad.generation.prompt_template": "",
        "lilypad.generation.version": generation.version_num
        if generation.version_num
        else -1,
    }


_GenerationIsManaged: TypeAlias = bool


@contextmanager
def _generation_context(
    generation_: GenerationPublic,
) -> Generator[None, None, None]:
    token = current_generation.set(generation_)
    try:
        # Check if this is the outermost generation (no previous generation)
        is_outermost = token.old_value == Token.MISSING
        with _outermost_lock_context(is_outermost):
            yield
    finally:
        current_generation.reset(token)


@overload
def _build_mirascope_call(  # pyright: ignore [reportOverlappingOverload]
    generation_public: GenerationPublic, fn: Callable[_P, Coroutine[Any, Any, _R]]
) -> Callable[_P, Coroutine[Any, Any, Message | Stream]]: ...


@overload
def _build_mirascope_call(
    generation_public: GenerationPublic, fn: Callable[_P, _R]
) -> Callable[_P, Message | Stream]: ...


def _build_mirascope_call(
    generation_public: GenerationPublic,
    fn: Callable[_P, _R] | Callable[_P, Coroutine[Any, Any, _R]],
) -> (
    Callable[_P, Message | Stream] | Callable[_P, Coroutine[Any, Any, Message | Stream]]
):
    """Build a Mirascope call object."""
    mirascope_prompt = prompt_template(generation_public.prompt_template)(fn)  # pyright: ignore [reportCallIssue, reportArgumentType]

    if not generation_public.model:
        raise ValueError("Managed generation requires `model`")
    if not generation_public.provider:
        raise ValueError("Managed generation requires `provider`")
    mirascope_call = llm.call(
        provider=cast(Provider, generation_public.provider),
        model=generation_public.model,
        call_params=cast(CommonCallParams, generation_public.call_params.model_dump())
        if generation_public.call_params
        else None,
    )(mirascope_prompt)

    @wraps(mirascope_call)
    def inner(
        *args: _P.args, **kwargs: _P.kwargs
    ) -> Message | Coroutine[Any, Any, Message | Stream] | Stream:
        result = mirascope_call(*args, **kwargs)
        if fn_is_async(mirascope_call):

            async def async_wrapper() -> Message | Stream:
                final = await result
                if isinstance(final, CallResponse):
                    return Message(final)  # pyright: ignore [reportAbstractUsage]
                return Stream(stream=final)

            return async_wrapper()
        else:

            def sync_wrapper() -> Message | Stream:
                final = result
                if isinstance(final, CallResponse):
                    return Message(final)  # pyright: ignore [reportAbstractUsage]

                return Stream(stream=final)

            return sync_wrapper()

    return inner  # pyright: ignore [reportReturnType]


def _build_generation_call(
    generation: GenerationPublic,
    is_async: bool,
    sandbox_runner: SandboxRunner | None,
) -> Callable[..., Any] | Callable[..., Coroutine[Any, Any, Any]]:
    """Build a generation call object."""
    if sandbox_runner is None:
        sandbox_runner = SubprocessSandboxRunner(os.environ.copy())
    closure = Closure(
        name=generation.name,
        code=generation.code,
        signature=generation.signature,
        hash=generation.hash,
        dependencies={
            name: cast(DependencyInfo, dependency.model_dump())
            for name, dependency in generation.dependencies.items()
        }
        if generation.dependencies
        else {},
    )

    if is_async:

        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            return sandbox_runner.execute_function(closure, *args, **kwargs)

        return async_wrapper
    else:

        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            return sandbox_runner.execute_function(closure, *args, **kwargs)

        return sync_wrapper


_ArgTypes: typing.TypeAlias = dict[str, str]


@overload
def generation(  # pyright: ignore [reportOverlappingOverload]
    custom_id: str | None = None,
    managed: Literal[True] = True,
    mode: Literal[GenerationMode.WRAP] = GenerationMode.WRAP,
) -> ManagedGenerationVersioningWrapDecorator: ...


@overload
def generation(  # pyright: ignore [reportOverlappingOverload]
    custom_id: str | None = None,
    managed: Literal[False] = False,
    mode: Literal[GenerationMode.WRAP] = GenerationMode.WRAP,
) -> GenerationVersioningWrapDecorator: ...


@overload
def generation(  # pyright: ignore [reportOverlappingOverload]
    custom_id: str | None = None,
    managed: Literal[True] = True,
    mode: Literal[GenerationMode.NO_WRAP] = GenerationMode.NO_WRAP,
) -> ManagedGenerationVersioningDecorator: ...


@overload
def generation(
    custom_id: str | None = None,
    managed: Literal[False] = False,
    mode: Literal[GenerationMode.NO_WRAP] = GenerationMode.NO_WRAP,
) -> GenerationVersioningDecorator: ...


def generation(
    custom_id: str | None = None,
    playground: bool = False,
    mode: GenerationMode = GenerationMode.NO_WRAP,
) -> (
    GenerationVersioningDecorator
    | ManagedGenerationVersioningDecorator
    | GenerationVersioningWrapDecorator
    | ManagedGenerationVersioningWrapDecorator
):
    """The `generation` decorator for versioning and tracing LLM generations.

    The decorated function will be versioned according to it's runnable lexical closure,
    and any call to the function will be traced and logged automatically.

    Args:
        custom_id: Optional custom identifier for the generation
        managed: If True, uses managed mode that retrieves generation info from server
        mode: Controls whether to return the original output or wrap it in a Generation object
        sandbox_factory: Optional sandbox factory to use for running the generation

    Returns:
        GenerationDecorator: The `generation` decorator return protocol.
    """

    @overload
    def decorator(
        fn: Callable[_P, Coroutine[Any, Any, _R]],
    ) -> Callable[_P, Coroutine[Any, Any, _R]]: ...

    @overload
    def decorator(fn: Callable[_P, _R]) -> Callable[_P, _R]: ...

    def decorator(
        fn: Callable[_P, _R] | Callable[_P, Coroutine[Any, Any, _R]],
    ) -> (
        Callable[_P, _R]
        | Callable[_P, Coroutine[Any, Any, _R]]
        | Callable[_P, Generation[_R]]
        | Callable[_P, Coroutine[Any, Any, Generation[_R]]]
    ):
        if _RECORDING_ENABLED:
            register_decorated_function("lilypad.generation", fn)

        is_mirascope_call = hasattr(fn, "__mirascope_call__") or managed
        prompt_template_value = (
            fn._prompt_template if hasattr(fn, "_prompt_template") else ""  # pyright: ignore[reportFunctionMemberAccess]
        )
        config = load_config()
        lilypad_client = LilypadClient(
            token=config.get("token", None),
        )
        if fn_is_async(fn):

            def _create_inner_async(
                get_generation: Callable[
                    [ArgTypes],
                    tuple[GenerationPublic, _GenerationIsManaged],
                ],
                sandbox_runner: SandboxRunner | None = None,
            ) -> (
                Callable[_P, Coroutine[Any, Any, _R]]
                | Callable[_P, Coroutine[Any, Any, Generation[_R]]]
            ):
                @call_safely(fn)  # pyright: ignore [reportArgumentType]
                async def _inner_async(
                    *args: _P.args, **kwargs: _P.kwargs
                ) -> _R | Generation[_R]:
                    arg_types, arg_values = inspect_arguments(fn, *args, **kwargs)
                    generation_, managed_prompt_template = get_generation(arg_types)
                    with _generation_context(generation_):
                        if not is_mirascope_call:
                            decorator_inner = _trace(
                                "generation",
                                _construct_trace_attributes(
                                    generation=generation_, arg_values=arg_values
                                ),
                            )
                            if managed_prompt_template:
                                result = await _build_generation_call(
                                    generation_, True, sandbox_runner
                                )(*args, **kwargs)
                            else:
                                result = await decorator_inner(fn)(*args, **kwargs)
                            output, trace_id, span_id = (
                                result
                                if isinstance(result, tuple)
                                else (result, None, None)
                            )
                        else:
                            span_context_holder = SpanContextHolder()
                            decorator_inner = create_mirascope_middleware(
                                generation_,
                                arg_values,
                                True,
                                generation_.prompt_template
                                if managed_prompt_template
                                else prompt_template_value,
                                span_context_holder=span_context_holder,
                            )
                            output = await decorator_inner(  # pyright: ignore [reportReturnType]
                                _build_mirascope_call(generation_, fn)
                                if managed_prompt_template
                                else fn
                            )(*args, **kwargs)
                            if span_context := span_context_holder.span_context:
                                span_id = span_context.span_id
                                trace_id = span_context.trace_id
                            else:
                                trace_id = span_id = None
                        # Wrap output if in wrap mode
                        if mode == GenerationMode.WRAP:
                            return Generation(output, generation_, trace_id, span_id)  # pyright: ignore [reportReturnType]
                        return output  # pyright: ignore [reportReturnType]

                return _inner_async

            def _get_active_version(
                arg_types: ArgTypes,
            ) -> tuple[GenerationPublic, _GenerationIsManaged]:
                if not managed:
                    return (
                        lilypad_client.get_or_create_generation_version(
                            fn,
                            arg_types,
                            custom_id=custom_id,
                        ),
                        False,
                    )
                try:
                    return (
                        lilypad_client.get_deployed_generation_by_names(fn),
                        True,
                    )
                except LilypadNotFoundError:
                    ui_link = f"{get_settings().remote_client_url}/projects/{lilypad_client.project_uuid}"
                    raise ValueError(
                        f"No generation found for function '{Closure.from_fn(fn).name}'. "
                        f"Please create a new generation at: {ui_link}"
                    )

            inner_async = _create_inner_async(_get_active_version)

            inner_async.version = specific_generation_version_async_factory(  # pyright: ignore [reportAttributeAccessIssue, reportFunctionMemberAccess]
                fn, _create_inner_async, lilypad_client
            )

            return inner_async

        else:

            def _create_inner_sync(
                get_generation: Callable[
                    [ArgTypes], tuple[GenerationPublic, _GenerationIsManaged]
                ],
                sandbox_runner: SandboxRunner | None = None,
            ) -> Callable[_P, _R] | Callable[_P, Generation[_R]]:
                @call_safely(fn)  # pyright: ignore [reportArgumentType]
                def _inner(*args: _P.args, **kwargs: _P.kwargs) -> _R | Generation[_R]:
                    arg_types, arg_values = inspect_arguments(fn, *args, **kwargs)
                    generation_, managed_prompt_template = get_generation(arg_types)
                    with _generation_context(generation_):
                        if not is_mirascope_call:
                            decorator_inner = _trace(
                                "generation",
                                _construct_trace_attributes(
                                    generation=generation_, arg_values=arg_values
                                ),
                            )
                            if managed_prompt_template:
                                result = _build_generation_call(
                                    generation_, False, sandbox_runner
                                )(*args, **kwargs)
                            else:
                                result = decorator_inner(fn)(*args, **kwargs)
                            output, trace_id, span_id = (
                                result
                                if isinstance(result, tuple)
                                else (result, None, None)
                            )
                        else:
                            span_context_holder = SpanContextHolder()
                            decorator_inner = create_mirascope_middleware(
                                generation_,
                                arg_values,
                                False,
                                generation_.prompt_template
                                if managed_prompt_template
                                else prompt_template_value,
                                span_context_holder=span_context_holder,
                            )
                            output = decorator_inner(
                                _build_mirascope_call(generation_, fn)
                                if managed_prompt_template
                                else fn
                            )(*args, **kwargs)
                            if span_context := span_context_holder.span_context:
                                span_id = span_context.span_id
                                trace_id = span_context.trace_id
                            else:
                                trace_id = span_id = None
                        if mode == GenerationMode.WRAP:
                            return Generation(output, generation_, trace_id, span_id)  # pyright: ignore [reportReturnType]
                        return output  # pyright: ignore [reportReturnType]

                return _inner  # pyright: ignore [reportReturnType]

            def _get_active_version(
                arg_types: ArgTypes,
            ) -> tuple[GenerationPublic, _GenerationIsManaged]:
                if not managed:
                    return (
                        lilypad_client.get_or_create_generation_version(
                            fn, arg_types, custom_id=custom_id
                        ),
                        False,
                    )
                try:
                    return (
                        lilypad_client.get_deployed_generation_by_names(fn),
                        True,
                    )
                except LilypadNotFoundError:
                    ui_link = f"{get_settings().remote_client_url}/projects/{lilypad_client.project_uuid}"
                    raise ValueError(
                        f"No generation found for function '{Closure.from_fn(fn).name}'. "
                        f"Please create a new generation at: {ui_link}"
                    )

            inner = _create_inner_sync(_get_active_version)

            inner.version = specific_generation_version_sync_factory(
                fn, _create_inner_sync, lilypad_client
            )  # pyright: ignore [reportAttributeAccessIssue, reportFunctionMemberAccess]

            return inner

    return decorator  # pyright: ignore [reportReturnType]
