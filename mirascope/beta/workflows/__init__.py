from __future__ import annotations

import collections
import copy
import hashlib
import inspect
import logging
import threading
import types
import typing
from collections import defaultdict
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from enum import Enum
from functools import cached_property
from typing import (
    Any,
    Generic,
    ParamSpec,
    TypeVar,
    get_args,
    get_origin,
    get_type_hints, TypeAlias,
)

from pydantic import BaseModel, ConfigDict, Field, SkipValidation
from typing_extensions import TypedDict

# Configure logger
logger = logging.getLogger(__name__)

_StartParam = ParamSpec("_StartParam")
_StopResponse = TypeVar("_StopResponse")
_R = TypeVar("_R")
_P = ParamSpec("_P")
_T = TypeVar("_T")
_Context = TypeVar("_Context")

_FuncHash: TypeAlias = str
_GroupId: TypeAlias = str

def get_full_qualname(func: Callable) -> str:
    return f"{func.__module__}.{func.__qualname__}"


def get_function_hash(func: Callable) -> str:
    """Generate a consistent hash for a function based on its fully qualified name."""
    name = get_full_qualname(func)
    # Use SHA-256 to generate a consistent hash value
    return hashlib.sha256(name.encode("utf-8")).hexdigest()


class NextStep(Generic[_T]):
    """Represents the next step in the workflow"""

    def __init__(
        self,
        func: Callable[_StartParam, Any],
        *func_args: _StartParam.args,
        **func_kwargs: _StartParam.kwargs,
    ) -> None:
        self.func = func
        self.func_args = func_args
        self.func_kwargs = func_kwargs

    @cached_property
    def func_hash(self) -> str:
        return get_function_hash(self.func)


class JoinStep(NextStep[_T]):
    """Represents a transition to a join point in the workflow

    Type parameter _T can be a single step or Union of multiple steps
    that need to be synchronized.
    """

    def __init__(
        self,
        func: Callable[_StartParam, Any],
        result: Any,
        group_id: str,  # group_id is consistently str
        expected_count: int,  # expected_count parameter
        *func_args: _StartParam.args,
        **func_kwargs: _StartParam.kwargs,
    ) -> None:
        super().__init__(func, *func_args, **func_kwargs)
        self.result = result
        self.group_id = group_id  # Store the group_id
        self.expected_count = (
            expected_count  # Store the expected number of dependencies
        )

    @classmethod
    def get_source_types(cls, type_param: type) -> set[type]:
        """Extract source types from type parameter"""
        sources = set()
        if origin := get_origin(type_param):
            if origin == typing.Union or (
                inspect.isclass(origin) and issubclass(origin, types.UnionType)
            ):
                for arg in get_args(type_param):
                    sources.add(arg)
            else:
                sources.add(type_param)
        else:
            sources.add(type_param)
        return sources


class StepResult(BaseModel, Generic[_T]):
    """Result of a workflow step execution"""

    value: _T
    step_full_qualname: str = Field(..., examples=["module.submodule.function"])

    model_config = ConfigDict(arbitrary_types_allowed=True)


class Join(BaseModel, Generic[_T]):
    """Represents a join point in the workflow"""

    results: list[StepResult[_T]]
    group_id: _GroupId


class StepStatus(str, Enum):
    """Status of a workflow step"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowNode(BaseModel):
    """Node in the workflow graph maintaining execution state"""

    func_hash: str
    status: StepStatus = StepStatus.PENDING
    results: list[StepResult] = Field(default_factory=list)
    futures: list[Future] = Field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def update_status(self, new_status: StepStatus) -> None:
        """Update node status with logging"""
        old_status = self.status
        self.status = new_status
        logger.debug(
            "Node %d status changed: %s -> %s", self.func_hash, old_status, new_status
        )

    def add_result(self, from_hash: str, result: Any) -> StepResult:
        """Add a result to this node

        Args:
            from_hash: The hash of the step that produced the result
            result: The result value to store

        Returns:
            Created StepResult instance
        """
        step_result = (
            StepResult(value=result, step_full_qualname=get_full_qualname(_steps[from_hash])) if not isinstance(result, StepResult) else result
        )
        self.results.append(step_result)
        self.update_status(StepStatus.COMPLETED)
        return step_result

    def get_last_result(self) -> StepResult | None:
        """Get the most recent result for this node

        Returns:
            Most recent StepResult or None if no results
        """
        return self.results[-1] if self.results else None


class WorkflowGraph(BaseModel):
    """Graph structure for managing workflow execution and dependencies."""

    nodes: dict[_FuncHash, WorkflowNode] = Field(
        default_factory=dict,
        description="Map of function hashes to their corresponding workflow nodes.",
    )
    edges: dict[_FuncHash, set[_FuncHash]] = Field(
        default_factory=lambda: defaultdict(set),
        description="Adjacency list representing edges in the graph.",
    )
    reverse_edges: dict[_FuncHash, set[_FuncHash]] = Field(
        default_factory=lambda: defaultdict(set),
        description="Reverse adjacency list for the graph.",
    )
    join_points: dict[tuple[_FuncHash, _GroupId], int] = Field(
        default_factory=dict,
        description="Map of join points to their expected counts, keyed by (func_hash, group_id).",
    )
    pending_results: dict[tuple[_FuncHash, _GroupId], list[StepResult]] = Field(
        default_factory=lambda: defaultdict(list),
        description="Collected results for join points.",
    )
    locks: dict[tuple[_FuncHash, str], threading.Lock] = Field(
        default_factory=lambda: defaultdict(threading.Lock),
        description="Locks for concurrency control per join point.",
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def add_node(self, func_hash: _FuncHash) -> None:
        """Add a new node to the graph if it doesn't already exist."""
        if func_hash not in self.nodes:
            self.nodes[func_hash] = WorkflowNode(func_hash=func_hash)
            logger.debug("Added node: %d", func_hash)

    def add_edge(self, from_hash: _FuncHash, to_hash: _FuncHash) -> None:
        """Add a directed edge to the graph without cycle detection."""
        self.add_node(from_hash)
        self.add_node(to_hash)

        self.edges[from_hash].add(to_hash)
        self.reverse_edges[to_hash].add(from_hash)
        logger.debug("Added edge: %d -> %d", from_hash, to_hash)

    def add_join_point(
            self, target_hash: _FuncHash, group_id: str, expected_count: int
    ) -> None:
        """Register a join point with its expected result count."""
        logger.debug(
            "Adding join point %d with expected_count %d and group_id %s",
            target_hash,
            expected_count,
            group_id,
        )
        key = (target_hash, group_id)
        if key not in self.join_points:
            self.join_points[key] = expected_count
            self.pending_results[key] = []
        else:
            logger.debug(
                "Join point %d with group_id %s already exists",
                target_hash,
                group_id,
            )

        self.add_node(target_hash)
        target_node = self.nodes[target_hash]
        target_node.status = StepStatus.PENDING

    def _extract_value_by_type(self, func_kwargs: dict[str, Any]) -> Any:
        """Extract the result value from function keyword arguments."""
        for _, value in func_kwargs.items():
            if value is None:
                continue
            if isinstance(value, (Join)):
                continue
            return value
        return None

    def add_result(
            self,
            from_hash: _FuncHash,
            result: Any,
            group_id: str,
    ) -> None:
        """Add a result from a completed step and update node status."""
        key = (from_hash, group_id)
        lock = self.locks[key]
        with lock:
            logger.debug(
                "Processing result from step %d with group_id %s", from_hash, group_id
            )

            self.add_node(from_hash)
            node = self.nodes[from_hash]
            node.status = StepStatus.RUNNING

            # Extract the actual result value
            if isinstance(result, JoinStep):
                result_value = result.result
                if result_value is None:
                    result_value = self._extract_value_by_type(result.func_kwargs)
                group_id = result.group_id
            elif isinstance(result, NextStep):
                result_value = self._extract_value_by_type(result.func_kwargs)
            else:
                result_value = result

            # Store the result with step information
            if result_value is not None:
                if not isinstance(result_value, StepResult):
                    step_result = StepResult(
                        value=result_value,
                        step_full_qualname=get_full_qualname(_steps[from_hash])
                    )
                else:
                    step_result = result_value

                node.add_result(from_hash, step_result)
                node.status = StepStatus.COMPLETED
                logger.debug("Stored result for step %d: %s", from_hash, step_result)
            else:
                logger.debug("No valid result value to store for step %d", from_hash)

            self._process_join_dependencies(from_hash, result_value, group_id)

    def _process_join_dependencies(
            self,
            from_hash: _FuncHash,
            result_value: Any,
            group_id: str
    ) -> None:
        """Process join points that depend on this step."""
        if result_value is None or group_id is None:
            return

        # Ensure result is wrapped in StepResult
        if not isinstance(result_value, StepResult):
            result_value = StepResult(
                value=result_value,
                step_full_qualname=get_full_qualname(_steps[from_hash])
            )

        for key in self.join_points:
            join_hash, join_group_id = key
            if join_group_id == group_id:
                join_lock = self.locks[key]
                with join_lock:
                    self.pending_results[key].append(result_value)
                    logger.debug(
                        "Added result to join point %d with group_id %s",
                        join_hash,
                        group_id,
                    )
                    if self.is_join_ready(join_hash, group_id):
                        join_node = self.nodes[join_hash]
                        join_node.status = StepStatus.COMPLETED

    def is_join_ready(self, join_hash: _FuncHash, group_id: str) -> bool:
        """Check if all dependencies for a join point have provided results."""
        key = (join_hash, group_id)
        if key not in self.join_points:
            return False

        expected_count = self.join_points[key]
        received_count = len(self.pending_results[key])

        ready = received_count >= expected_count
        logger.debug(
            "Join point %d status: Expected count: %d, Received count: %d, Ready: %s, Group ID: %s",
            join_hash,
            expected_count,
            received_count,
            ready,
            group_id,
        )

        return ready

    def get_join_results(self, join_hash: _FuncHash, group_id: str) -> list[StepResult]:
        """Get all results for a join point."""
        if not self.is_join_ready(join_hash, group_id):
            raise ValueError(
                f"Join point {join_hash} with group_id {group_id} is not ready"
            )

        key = (join_hash, group_id)
        results = self.pending_results[key]
        logger.debug(
            "Collecting results for join %d with group_id %s", join_hash, group_id
        )
        logger.debug("Total collected results: %d", len(results))
        return results

    def cleanup_completed_joins(self) -> None:
        """Clean up completed join points to free memory."""
        completed_joins = []
        for key in self.join_points:
            join_hash, group_id = key
            if self.is_join_ready(join_hash, group_id):
                completed_joins.append(key)

        for key in completed_joins:
            del self.pending_results[key]
            del self.join_points[key]
            del self.locks[key]
            logger.debug(
                "Cleaned up completed join point %d with group_id %s", key[0], key[1]
            )

class StepFuncInfo(BaseModel):
    """Metadata about a workflow step function"""

    arguments: dict[str, SkipValidation[type | None]] = Field(default_factory=dict)
    next_steps: set[_FuncHash] = Field(default_factory=set)
    stop_types: list[SkipValidation[type | None]] = Field(default_factory=list)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class BaseContext(TypedDict, total=False):
    """Base context for workflow execution"""

    results: list[StepResult]  # Results from previous steps


_steps: dict[_FuncHash, Callable] = {}


def _extract_join_dependencies(hint: type) -> set[_FuncHash] | None:
    """Extract dependencies from Join type annotation"""
    if (origin := get_origin(hint)) and origin == Join:
        join_deps = set()
        for arg_type in get_args(hint):
            if inspect.isfunction(arg_type):
                func_hash = get_function_hash(arg_type)
                if func_hash in _steps:
                    join_deps.add(func_hash)
                else:
                    raise ValueError(f"Function {arg_type} is not a registered step")
            else:
                # Skip non-function types (e.g., built-in types like str)
                pass
        return join_deps if join_deps else None
    return None


def _extract_next_step(next_type: type[NextStep]) -> set[_FuncHash]:
    """Extract possible next step hashes from type annotation"""
    hashes = set()
    for arg_type in get_args(next_type):
        try:
            arg_type_hash = get_function_hash(arg_type)
        except TypeError:
            raise TypeError(f"Cannot hash function {arg_type}")

        if arg_type_hash not in _steps:
            raise ValueError(f"Function {arg_type} is not a step")
        hashes.add(arg_type_hash)
    return hashes


def _extract_type_arguments(func: Callable) -> tuple[str, StepFuncInfo]:
    """Extract type information and metadata from a workflow step function"""
    try:
        func_hash = get_function_hash(func)
    except TypeError:
        raise TypeError(f"Cannot hash function {func}")

    hints = get_type_hints(func, include_extras=True)
    next_steps: set[str] = set()
    arguments: dict[str, type | None] = {}
    stop_types: list[type] = []

    def process_type(type_hint: type) -> None:
        """Process a single type hint to extract next steps"""
        if origin := get_origin(type_hint):
            if inspect.isclass(origin) and issubclass(origin, JoinStep):
                join_args = get_args(type_hint)[0]
                # Only add function dependencies
                for src in JoinStep.get_source_types(join_args):
                    if inspect.isfunction(src):
                        func_hash = get_function_hash(src)
                        if func_hash in _steps:
                            next_steps.add(func_hash)
                        else:
                            raise ValueError(f"Function {src} is not a registered step")
            elif inspect.isclass(origin) and issubclass(origin, NextStep):
                next_steps.update(_extract_next_step(type_hint))
            elif origin in (typing.Union, types.UnionType):
                # Process each type in the Union
                for arg in get_args(type_hint):
                    process_type(arg)
                return  # Continue processing
            else:
                # Handle other generic types if needed
                pass
        else:
            # For non-generic types, ensure they are functions before processing
            if inspect.isfunction(type_hint):
                func_hash = get_function_hash(type_hint)
                if func_hash in _steps:
                    next_steps.add(func_hash)
                else:
                    raise ValueError(f"Function {type_hint} is not a registered step")
            else:
                # Non-function types are considered stop types
                stop_types.append(type_hint)

    for name, hint in hints.items():
        if name == "return":
            if origin := get_origin(hint):
                # Process generator types
                if origin in (typing.Generator, collections.abc.Generator):
                    generator_args = get_args(hint)
                    if generator_args:
                        yield_type = generator_args[0]
                        process_type(yield_type)
                        stop_types.append(hint)
                    continue
                # Process Union types
                elif origin in (typing.Union, types.UnionType):
                    for arg in get_args(hint):
                        process_type(arg)
                    continue
                # NextStep or JoinStep types
                elif inspect.isclass(origin) and issubclass(
                    origin, NextStep | JoinStep
                ):
                    process_type(hint)
                    stop_types.append(hint)
                    continue
            else:
                # Non-generic return types
                process_type(hint)
        else:
            arguments[name] = hint
            # Do not extract dependencies from function parameters to avoid cycles

    logger.debug("Extracted next steps for %s: %s", func.__name__, next_steps)
    return func_hash, StepFuncInfo(
        arguments=arguments,
        next_steps=next_steps,
        stop_types=stop_types,
    )


def step() -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    """Decorator to register a function as a workflow step"""

    def decorator(func: Callable[_P, _R]) -> Callable[_P, _R]:
        func_hash = get_function_hash(func)
        _steps[func_hash] = func
        return func

    return decorator


class WorkflowOutput(Generic[_Context, _T]):
    """Output of a workflow execution"""

    def __init__(self, output: _T, context: _Context) -> None:
        self.output: _T = output
        self.context: _Context = context


class Workflow(Generic[_Context, _StartParam, _StopResponse]):
    """Main workflow class"""

    def __init__(
        self,
        start: Callable[_StartParam, Any],
        stop: Callable[[Any], _StopResponse]
        | Callable[[Any], _StopResponse | NextStep],
    ) -> None:
        start_hash = get_function_hash(start)
        stop_hash = get_function_hash(stop)
        if start_hash not in _steps:
            raise ValueError(f"Function {start} is not a step")
        if stop_hash not in _steps:
            raise ValueError(f"Function {stop} is not a step")

        self.start = start
        self.stop = stop
        self._steps: dict[_FuncHash, tuple[StepFuncInfo, Callable]] = {}
        self._thread_pool_executor = ThreadPoolExecutor()
        self._graph = WorkflowGraph()  # Use the updated WorkflowGraph
        self._build_graph()
        self._wrap_step(start)

    def _build_graph(self) -> None:
        """Build the initial graph structure from type information

        Analyzes step function signatures to identify join points and their dependencies.
        """
        # Since group_id and expected_count are dynamic, we cannot build joins here
        pass

    def _process_step_result(
            self,
            result: Any,
            context: _Context,
            step_info: StepFuncInfo,
            func: Callable,
            group_id: str,
    ) -> tuple[_R, _Context]:
        """Process the result of a workflow step

        Handles both NextStep and JoinStep transitions, managing the result collection
        and synchronization for join points.
        """
        func_hash = get_function_hash(func)

        if isinstance(result, NextStep | JoinStep):
            # Validate the next step
            if not step_info.next_steps:
                raise ValueError(f"Function {func} does not have any next steps")
            if result.func_hash not in _steps:
                raise ValueError(f"Function {result.func} is not a registered step")
            if result.func_hash not in step_info.next_steps:
                raise ValueError(f"Function {result.func} is not a valid next step")

            # Add edge to the graph to represent the flow between steps
            self._graph.add_edge(func_hash, result.func_hash)

            if isinstance(result, JoinStep):
                # Handle JoinStep
                group_id = result.group_id
                expected_count = result.expected_count

                if expected_count is None:
                    raise ValueError("expected_count must be specified in JoinStep")

                # Register the join point with expected count and group_id
                self._graph.add_join_point(result.func_hash, group_id, expected_count)

                # Store the current step's result
                self._graph.add_result(func_hash, result, group_id=group_id)

                # Check if the join point is ready
                if not self._graph.is_join_ready(result.func_hash, group_id):
                    # Join point is not ready yet
                    return None, context

                # All results are ready, create a Join result
                join_results = self._graph.get_join_results(result.func_hash, group_id)
                # Use keyword arguments for Join initialization
                join_kwargs = {
                    "multiple_input": Join(
                        results=join_results,
                        group_id=group_id
                    )
                }

                # Merge kwargs and pass group_id
                merged_kwargs = {**result.func_kwargs}
                merged_kwargs.pop("result", None)  # Remove 'result' if present
                merged_kwargs.update(join_kwargs)

                # Clean up completed join to free memory
                self._graph.cleanup_completed_joins()

                # Create the next step for execution
                next_step = NextStep(result.func, *result.func_args, **merged_kwargs)
            else:
                # For NextStep, proceed directly
                next_step = result
                # Store the current step's result
                self._graph.add_result(func_hash, result, group_id=group_id)

            # Execute the next step
            next_step_info, next_wrapped_func = self._steps[next_step.func_hash]
            return next_wrapped_func(
                *next_step.func_args,
                _Workflow__context=context,
                **next_step.func_kwargs,
            )
        else:
            # For non-NextStep results, store the actual value
            self._graph.add_result(func_hash, result, group_id=group_id)
            return result, context

    def _wrap_step(self, func: Callable[_P, _R]) -> None:
        """Wrap a workflow step with execution logic"""
        func_hash, step_info = _extract_type_arguments(func)

        def wrapper(
            *args: _P.args, __context: _Context, **kwargs: _P.kwargs
        ) -> tuple[_R, _Context] | tuple[list[_R], list[_Context]]:
            group_id = kwargs.get("group_id", None)
            if inspect.isgeneratorfunction(func):
                # If the function is a generator, handle each yielded value
                with ThreadPoolExecutor() as executor:
                    result = func(*args, **kwargs)
                    futures = []
                    results = []
                    contexts = []

                    # Submit all tasks for parallel execution
                    for res in result:
                        # Extract group_id from the result if present
                        res_group_id = getattr(res, "group_id", group_id)
                        future = executor.submit(
                            self._process_step_result,
                            res,
                            copy.deepcopy(__context),
                            step_info,
                            func,
                            group_id=res_group_id,
                        )
                        futures.append(future)

                    # Process results as they complete
                    for future in as_completed(futures):
                        try:
                            res_result, res_context = future.result()
                            if res_result is not None:  # Not waiting at a join point
                                results.append(res_result)
                                contexts.append(res_context)
                        except Exception as e:
                            logger.exception("Error processing step result")
                            raise e

                    # Return any completed results
                    return results, contexts
            else:
                # For regular functions
                if "context" in step_info.arguments:
                    # If the function expects 'context' as an argument
                    result = func(*args, **kwargs, context=__context)
                else:
                    result = func(*args, **kwargs)
                return self._process_step_result(
                    result, __context, step_info, func, group_id=group_id,
                )

        # Register the wrapped function
        self._steps[func_hash] = (step_info, wrapper)
        # Recursively wrap next steps if not already wrapped
        for next_step_hash in step_info.next_steps:
            if next_step_hash not in self._steps:
                next_func = _steps[next_step_hash]
                self._wrap_step(next_func)
                # Add edge to the graph
                self._graph.add_edge(func_hash, next_step_hash)

    def run(
        self, *args: _StartParam.args, **kwargs: _StartParam.kwargs
    ) -> WorkflowOutput[_Context, _StopResponse]:
        """Run the workflow"""
        context: _Context = {}
        start_hash = get_function_hash(self.start)
        result, context = self._steps[start_hash][1](
            *args, _Workflow__context=context, **kwargs
        )
        return WorkflowOutput(result, context)
