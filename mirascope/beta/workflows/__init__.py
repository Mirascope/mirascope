from __future__ import annotations

import collections
import copy
import inspect
import logging
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
    get_type_hints,
)

from pydantic import BaseModel, Field, SkipValidation
from typing_extensions import TypedDict

# Configure logger
logger = logging.getLogger(__name__)

_StartParam = ParamSpec("_StartParam")
_StopResponse = TypeVar("_StopResponse")
_R = TypeVar("_R")
_P = ParamSpec("_P")
_T = TypeVar("_T")
_Context = TypeVar("_Context")


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
    def func_hash(self) -> int:
        return hash(self.func)


class JoinStep(NextStep[_T]):
    """Represents a transition to a join point in the workflow

    Type parameter _T can be a single step or Union of multiple steps
    that need to be synchronized.
    """

    def __init__(
        self,
        func: Callable[_StartParam, Any],
        result: Any = None,
        *func_args: _StartParam.args,
        **func_kwargs: _StartParam.kwargs,
    ) -> None:
        super().__init__(func, *func_args, **func_kwargs)
        self.result = result

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


class Join(Generic[_T]):
    """Represents a join point in the workflow"""

    def __init__(self, results: list[_T]):
        self.results = results


class StepStatus(str, Enum):
    """Status of a workflow step"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class StepResult(BaseModel):
    """Result of a workflow step execution"""

    value: Any
    next_steps: list[NextStep] = Field(default_factory=list)
    should_retry: bool = False
    retry_delay: float = 0.0

    class Config:
        arbitrary_types_allowed = True


class WorkflowNode(BaseModel):
    """Node in the workflow graph maintaining execution state"""

    func_hash: int
    status: StepStatus = StepStatus.PENDING
    results: list[StepResult] = Field(default_factory=list)
    futures: list[Future] = Field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3

    class Config:
        arbitrary_types_allowed = True

    def update_status(self, new_status: StepStatus) -> None:
        """Update node status with logging"""
        old_status = self.status
        self.status = new_status
        logger.debug(
            "Node %d status changed: %s -> %s", self.func_hash, old_status, new_status
        )

    def add_result(self, result: Any) -> StepResult:
        """Add a result to this node

        Args:
            result: The result value to store

        Returns:
            Created StepResult instance
        """
        step_result = (
            StepResult(value=result) if not isinstance(result, StepResult) else result
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


class WorkflowDAG(BaseModel):
    """Directed Acyclic Graph structure for managing workflow execution and dependencies"""

    nodes: dict[int, WorkflowNode] = Field(
        default_factory=dict,
        description="Map of function hashes to their workflow nodes",
    )
    edges: dict[int, set[int]] = Field(
        default_factory=lambda: defaultdict(set),
        description="Adjacency list representing DAG edges",
    )
    join_points: dict[int, set[int]] = Field(
        default_factory=lambda: defaultdict(set),
        description="Map of join points to their dependency hashes",
    )
    pending_results: dict[int, dict[int, list[Any]]] = Field(
        default_factory=lambda: defaultdict(lambda: defaultdict(list)),
        description="Collected results for join points",
    )
    active_tasks: dict[int, int] = Field(
        default_factory=dict, description="Count of pending tasks for each join point"
    )

    class Config:
        arbitrary_types_allowed = True

    def add_node(self, func_hash: int) -> None:
        """Add a new node to the DAG"""
        if func_hash not in self.nodes:
            self.nodes[func_hash] = WorkflowNode(func_hash=func_hash)
            logger.debug("Added node: %d", func_hash)

    def add_edge(self, from_hash: int, to_hash: int) -> None:
        """Add a directed edge to the DAG"""
        self.add_node(from_hash)
        self.add_node(to_hash)
        self.edges[from_hash].add(to_hash)
        logger.debug("Added edge: %d -> %d", from_hash, to_hash)

    def get_dependency_path(self, target_hash: int) -> list[int]:
        """Get the path of dependencies leading to a target node"""
        path = []
        visited = set()

        def dfs(node: int) -> bool:
            if node == target_hash:
                path.append(node)
                return True
            visited.add(node)
            for next_node in self.edges[node]:
                if next_node not in visited and dfs(next_node):
                    path.append(node)
                    return True
            return False

        for start_node in self.nodes:
            if start_node not in visited and dfs(start_node):
                break

        return list(reversed(path))

    def add_join_point(self, target_hash: int, dependency_hashes: set[int]) -> None:
        """Register a join point with its dependencies"""
        logger.debug(
            "Adding join point %d with dependencies %s", target_hash, dependency_hashes
        )
        self.join_points[target_hash].update(dependency_hashes)

        # Add edges and initialize nodes
        for dep_hash in dependency_hashes:
            self.add_node(dep_hash)
            self.add_edge(dep_hash, target_hash)

        # Initialize or update task counter
        current_tasks = self.active_tasks.get(target_hash, 0)
        self.active_tasks[target_hash] = current_tasks + len(dependency_hashes)

        # Get or create target node and update its status
        if target_hash not in self.nodes:
            self.add_node(target_hash)
        target_node = self.nodes[target_hash]
        target_node.status = StepStatus.PENDING

        logger.debug(
            "Join point %d status: Dependencies: %s, Active tasks: %d",
            target_hash,
            self.join_points[target_hash],
            self.active_tasks[target_hash],
        )

    def _extract_value_by_type(self, func_kwargs: dict[str, Any]) -> Any:
        """Extract result value from kwargs based on parameter types

        Args:
            func_kwargs: Function keyword arguments

        Returns:
            First valid result value found, or None if no valid value found
        """
        for _, value in func_kwargs.items():
            if value is None:
                continue

            # Skip parameters that are internal types
            if isinstance(value, (Join)):
                continue

            return value
        return None

    def add_result(self, from_hash: int, result: Any) -> None:  # noqa: ANN401
        """Add a result from a completed step and update node status

        Args:
            from_hash: Hash of the step that produced the result
            result: Result value, can be a JoinStep, NextStep, or any value
        """
        logger.debug("Processing result from step %d", from_hash)

        # Get or create node and update its status
        if from_hash not in self.nodes:
            self.nodes[from_hash] = WorkflowNode(func_hash=from_hash)
        node = self.nodes[from_hash]
        node.status = StepStatus.RUNNING

        # Extract the actual result value
        if isinstance(result, JoinStep):
            # For JoinStep, prioritize the result property
            result_value = result.result
            if result_value is None:
                result_value = self._extract_value_by_type(result.func_kwargs)
        elif isinstance(result, NextStep):
            # For NextStep, extract from kwargs by parameter type
            result_value = self._extract_value_by_type(result.func_kwargs)
        else:
            result_value = result

        # Store the result if valid
        if result_value is not None:
            step_result = node.add_result(result_value)
            node.status = StepStatus.COMPLETED
            logger.debug("Stored result for step %d: %s", from_hash, result_value)
        else:
            logger.debug("No valid result value to store for step %d", from_hash)

        # Update join points if this step is a dependency
        self._process_join_dependencies(from_hash, result_value)

    def _process_join_dependencies(self, from_hash: int, result_value: Any) -> None:
        """Process join points that depend on this step

        Args:
            from_hash: Hash of the step that produced the result
            result_value: The result value to store
        """
        if result_value is None:
            return

        for join_hash, dependencies in self.join_points.items():
            if from_hash in dependencies:
                logger.debug(
                    "Updating join point %d with result from %d", join_hash, from_hash
                )
                # Store the result
                self.pending_results[join_hash][from_hash].append(result_value)
                # Update active tasks counter
                self.active_tasks[join_hash] = max(0, self.active_tasks[join_hash] - 1)

                # Update join point node status
                if join_hash in self.nodes:
                    join_node = self.nodes[join_hash]
                    if self.is_join_ready(join_hash):
                        join_node.status = StepStatus.COMPLETED
                    else:
                        join_node.status = StepStatus.RUNNING

    def is_join_ready(self, join_hash: int) -> bool:
        """Check if all dependencies for a join point have provided results

        Args:
            join_hash: Hash of the join point to check

        Returns:
            True if the join point is ready for processing
        """
        if join_hash not in self.join_points:
            return False

        required_deps = self.join_points[join_hash]
        if not required_deps:
            return False

        # Check if we have results from all dependencies
        has_all_results = all(
            len(self.pending_results[join_hash][dep_hash]) > 0
            for dep_hash in required_deps
        )

        # Check if all tasks are completed
        tasks_complete = self.active_tasks.get(join_hash, 0) <= 0

        ready = has_all_results and tasks_complete
        logger.debug(
            "Join point %d status: Required deps: %s, Has results: %s, Tasks complete: %s, Ready: %s",
            join_hash,
            required_deps,
            has_all_results,
            tasks_complete,
            ready,
        )

        return ready

    def get_join_results(self, join_hash: int) -> list[Any]:
        """Get all results for a join point in dependency order"""
        if not self.is_join_ready(join_hash):
            raise ValueError(f"Join point {join_hash} is not ready")

        # Get results in order of dependencies
        all_results = []
        dependency_path = self.get_dependency_path(join_hash)

        logger.debug("Collecting results for join %d", join_hash)
        logger.debug("Dependency path: %s", dependency_path)

        for dep_hash in dependency_path:
            if dep_hash in self.join_points[join_hash]:
                results = self.pending_results[join_hash][dep_hash]
                logger.debug("Results from %d: %s", dep_hash, results)
                all_results.extend(results)

        logger.debug("Total collected results: %d", len(all_results))
        return all_results


class StepFuncInfo(BaseModel):
    """Metadata about a workflow step function"""

    arguments: dict[str, SkipValidation[type | None]] = Field(default_factory=dict)
    next_steps: set[int] = Field(default_factory=set)
    stop_types: list[SkipValidation[type | None]] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True


class BaseContext(TypedDict, total=False):
    """Base context for workflow execution"""

    pass


_steps: dict[int, Callable] = {}


def _extract_join_dependencies(hint: type) -> set[int] | None:
    """Extract dependencies from Join type annotation"""
    if (origin := get_origin(hint)) and origin == Join:
        join_deps = set()
        for arg_type in get_args(hint):
            try:
                join_deps.add(hash(arg_type))
            except TypeError:
                raise TypeError(f"Cannot hash function {arg_type}")
        return join_deps
    return None


def _extract_next_step(next_type: type[NextStep]) -> set[int]:
    """Extract possible next step hashes from type annotation"""
    hashes = set()
    for arg_type in get_args(next_type):
        try:
            arg_type_hash = hash(arg_type)
        except TypeError:
            raise TypeError(f"Cannot hash function {arg_type}")

        if arg_type_hash not in _steps:
            raise ValueError(f"Function {arg_type} is not a step")
        hashes.add(arg_type_hash)
    return hashes


def _extract_type_arguments(func: Callable) -> tuple[int, StepFuncInfo]:
    """Extract type information and metadata from a workflow step function"""
    try:
        func_hash = hash(func)
    except TypeError:
        raise TypeError(f"Cannot hash function {func}")

    hints = get_type_hints(func, include_extras=True)
    next_steps: set[int] = set()
    arguments: dict[str, type | None] = {}
    stop_types: list[type] = []

    def process_type(type_hint: type) -> None:
        """Process a single type hint to extract next steps"""
        if origin := get_origin(type_hint):
            if issubclass(origin, JoinStep):
                join_args = get_args(type_hint)[0]
                next_steps.update(
                    hash(src) for src in JoinStep.get_source_types(join_args)
                )
            elif issubclass(origin, NextStep):
                next_steps.update(_extract_next_step(type_hint))
            elif origin in (typing.Union, types.UnionType):
                # Process each type in the Union
                for arg in get_args(type_hint):
                    if arg_origin := get_origin(arg):
                        process_type(arg)
                    else:
                        stop_types.append(arg)

    for name, hint in hints.items():
        if name == "return":
            if origin := get_origin(hint):
                # Process generator types
                if origin in (typing.Generator, collections.abc.Generator):
                    generator_args = get_args(hint)
                    if generator_args:
                        yield_type = generator_args[0]
                        if yield_origin := get_origin(yield_type):
                            logger.debug("Processing generator type: %s", yield_type)
                            logger.debug("  Origin: %s", yield_origin)

                            # Handle Union in generator yield type
                            if yield_origin in (typing.Union, types.UnionType):
                                for union_arg in get_args(yield_type):
                                    process_type(union_arg)
                            else:
                                process_type(yield_type)
                            stop_types.append(hint)
                            continue
                # Process Union types
                elif (
                    inspect.isclass(origin) and issubclass(origin, types.UnionType)
                ) or origin == typing.Union:
                    for arg in get_args(hint):
                        process_type(arg)
                    continue
                # NextStep or JoinStep types
                elif issubclass(origin, NextStep | JoinStep):
                    process_type(hint)
                    stop_types.append(hint)
                    continue
            stop_types.append(hint)
        else:
            arguments[name] = hint
            if join_deps := _extract_join_dependencies(hint):
                next_steps.update(join_deps)

    logger.debug("Extracted next steps for %s: %s", func.__name__, next_steps)
    return func_hash, StepFuncInfo(
        arguments=arguments,
        next_steps=next_steps,
        stop_types=stop_types,
    )


def step() -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    """Decorator to register a function as a workflow step"""

    def decorator(func: Callable[_P, _R]) -> Callable[_P, _R]:
        _steps[hash(func)] = func
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
        if hash(start) not in _steps:
            raise ValueError(f"Function {start} is not a step")
        if hash(stop) not in _steps:
            raise ValueError(f"Function {stop} is not a step")

        self.start = start
        self.stop = stop
        self._steps: dict[int, tuple[StepFuncInfo, Callable]] = {}
        self._thread_pool_executor = ThreadPoolExecutor()
        self._graph = WorkflowDAG()
        self._build_graph()
        self._wrap_step(start)

    def _build_graph(self) -> None:
        """Build the initial graph structure from type information

        Analyzes step function signatures to identify join points and their dependencies.
        """
        # First pass: collect all join points
        for func_hash, func in _steps.items():
            hints = get_type_hints(func)
            for name, hint in hints.items():
                if join_deps := _extract_join_dependencies(hint):
                    self._graph.add_join_point(func_hash, join_deps)

    def _process_step_result(
        self, result: Any, context: _Context, step_info: StepFuncInfo, func: Callable
    ) -> tuple[_R, _Context]:
        """Process the result of a workflow step

        Handles both NextStep and JoinStep transitions, managing the result collection
        and synchronization for join points.
        """
        if isinstance(result, NextStep | JoinStep):
            # Validate next step
            if not step_info.next_steps:
                raise ValueError(f"Function {func} does not have any next steps")
            if result.func_hash not in _steps:
                raise ValueError(f"Function {result.func} is not a step")
            if result.func_hash not in step_info.next_steps:
                raise ValueError(f"Function {result.func} is not a valid next step")

            # Store the current step's result
            self._graph.add_result(hash(func), result)

            # Handle join points
            if result.func_hash in self._graph.join_points:
                # Check if join point is ready
                if not self._graph.is_join_ready(result.func_hash):
                    return None, context

                # All results are ready, create Join result
                join_results = self._graph.get_join_results(result.func_hash)
                join_kwargs = {"multiple_input": Join(join_results)}

                # Create next step with merged kwargs
                merged_kwargs = {**result.func_kwargs}
                merged_kwargs.pop("result", None)  # Remove result if present
                merged_kwargs.update(join_kwargs)

                # Create next step for execution
                next_step = NextStep(result.func, *result.func_args, **merged_kwargs)
            else:
                next_step = result

            # Execute next step
            next_step_info, next_wrapped_func = self._steps[next_step.func_hash]
            return next_wrapped_func(
                *next_step.func_args,
                **next_step.func_kwargs,
                _Workflow__context=context,
            )
        else:
            # For non-NextStep results, store the actual value
            self._graph.add_result(hash(func), result)
            return result, context

    def _wrap_step(self, func: Callable[_P, _R]) -> None:
        """Wrap a workflow step with execution logic"""
        func_hash, step_info = _extract_type_arguments(func)

        def wrapper(
            *args: _P.args, __context: _Context, **kwargs: _P.kwargs
        ) -> tuple[_R, _Context] | tuple[list[_R], list[_Context]]:
            if inspect.isgeneratorfunction(func):
                with self._thread_pool_executor as executor:
                    result = func(*args, **kwargs)
                    futures = []
                    results = []
                    contexts = []

                    # Submit all tasks for parallel execution
                    for res in result:
                        future = executor.submit(
                            self._process_step_result,
                            res,
                            copy.deepcopy(__context),
                            step_info,
                            func,
                        )
                        futures.append(future)

                    # Process results as they complete
                    for future in as_completed(futures):
                        try:
                            result, context = future.result()
                            if result is not None:  # Not waiting at a join point
                                results.append(result)
                                contexts.append(context)
                        except Exception as e:
                            logger.exception("Error processing step result")
                            raise e

                    # Return any completed results
                    return results, contexts
            else:
                if "context" in step_info.arguments:
                    result = func(*args, **kwargs, context=__context)
                else:
                    result = func(*args, **kwargs)
                return self._process_step_result(result, __context, step_info, func)

        self._steps[func_hash] = step_info, wrapper
        for next_step in step_info.next_steps:
            if next_step not in self._steps:
                self._wrap_step(_steps[next_step])

    def run(
        self, *args: _StartParam.args, **kwargs: _StartParam.kwargs
    ) -> WorkflowOutput[_Context, _StopResponse]:
        """Run the workflow"""
        context: _Context = {}
        result, context = self._steps[hash(self.start)][1](
            *args, _Workflow__context=context, **kwargs
        )
        return WorkflowOutput(result, context)
