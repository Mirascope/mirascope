"""Typed arguments are reconstructed when executing JSON tool calls."""

import inspect
import json
from datetime import date

import pytest
from pydantic import BaseModel, ConfigDict, ValidationError

from mirascope import llm


class City(BaseModel):
    name: str


class Trip(BaseModel):
    model_config = ConfigDict(strict=True)

    destination: City
    departure: date | None = None
    route: tuple[City, ...] = ()


DEFAULT_TRIP = Trip(destination=City(name="London"))


@llm.tool
def describe_trip(
    trip: Trip = DEFAULT_TRIP, stops: list[City] | None = None, suffix: str = "!"
) -> str:
    names = [
        trip.destination.name,
        *(city.name for city in trip.route),
        *(city.name for city in stops or []),
    ]
    departure = f" ({trip.departure.isoformat()})" if trip.departure else ""
    return ", ".join(names) + departure + suffix


@llm.tool
async def describe_trip_async(
    trip: Trip = DEFAULT_TRIP, stops: list[City] | None = None, suffix: str = "!"
) -> str:
    return describe_trip(trip, stops, suffix)


@llm.tool
def describe_trip_context(
    ctx: llm.Context[str],
    trip: Trip = DEFAULT_TRIP,
    stops: list[City] | None = None,
    suffix: str = "!",
) -> str:
    return ctx.deps + describe_trip(trip, stops, suffix)


@llm.tool
async def describe_trip_async_context(
    ctx: llm.Context[str],
    trip: Trip = DEFAULT_TRIP,
    stops: list[City] | None = None,
    suffix: str = "!",
) -> str:
    return ctx.deps + describe_trip(trip, stops, suffix)


TOOLS = [
    describe_trip,
    describe_trip_async,
    describe_trip_context,
    describe_trip_async_context,
]


@pytest.mark.parametrize("tool", TOOLS)
@pytest.mark.parametrize(
    ("args", "expected"),
    [
        ('{"trip": {"destination": {"name": "Paris"}}}', "Paris!"),
        (
            '{"trip": {"destination": {"name": "Paris"}, "departure": "2026-10-18", "route": [{"name": "Berlin"}]}}',
            "Paris, Berlin (2026-10-18)!",
        ),
        (
            '{"stops": [{"name": "Paris"}, {"name": "Berlin"}]}',
            "London, Paris, Berlin!",
        ),
        ('{"stops": null, "suffix": "?"}', "London?"),
        ("{}", "London!"),
        ("", "London!"),
        (" \t\n", "London!"),
    ],
)
@pytest.mark.asyncio
async def test_typed_arguments(
    tool: llm.Tool | llm.AsyncTool | llm.ContextTool[str] | llm.AsyncContextTool[str],
    args: str,
    expected: str,
) -> None:
    call = llm.ToolCall(id="typed", name=tool.name, args=args)
    ctx = llm.Context(deps="Trip: ")
    if isinstance(tool, llm.AsyncContextTool):
        output = await tool.execute(ctx, call)
        expected = ctx.deps + expected
    elif isinstance(tool, llm.ContextTool):
        output = tool.execute(ctx, call)
        expected = ctx.deps + expected
    elif isinstance(tool, llm.AsyncTool):
        output = await tool.execute(call)
    else:
        output = tool.execute(call)
    assert output.error is None
    assert output.result == expected
    assert output.id == call.id
    assert output.name == tool.name


@pytest.mark.parametrize("tool", TOOLS)
@pytest.mark.parametrize(
    ("args", "error_type"),
    [
        ('{"trip": {"destination": {}}}', ValidationError),
        ('{"stops": [{"name": []}]}', ValidationError),
        ('{"unexpected": true}', TypeError),
        ("{", json.JSONDecodeError),
        ("null", TypeError),
        ("[]", TypeError),
    ],
)
@pytest.mark.asyncio
async def test_invalid_typed_arguments(
    tool: llm.Tool | llm.AsyncTool | llm.ContextTool[str] | llm.AsyncContextTool[str],
    args: str,
    error_type: type[Exception],
) -> None:
    call = llm.ToolCall(id="invalid", name=tool.name, args=args)
    ctx = llm.Context(deps="Trip: ")
    if isinstance(tool, llm.AsyncContextTool):
        output = await tool.execute(ctx, call)
    elif isinstance(tool, llm.ContextTool):
        output = tool.execute(ctx, call)
    elif isinstance(tool, llm.AsyncTool):
        output = await tool.execute(call)
    else:
        output = tool.execute(call)
    assert isinstance(output.error, llm.ToolExecutionError)
    assert isinstance(output.error.tool_exception, error_type)


@pytest.mark.asyncio
async def test_direct_calls_preserve_model_instances() -> None:
    trip = Trip(destination=City(name="Paris"))
    stops = [City(name="Berlin")]
    ctx = llm.Context(deps="Trip: ")
    assert describe_trip(trip, stops) == "Paris, Berlin!"
    assert await describe_trip_async(trip, stops) == "Paris, Berlin!"
    assert describe_trip_context(ctx, trip, stops) == "Trip: Paris, Berlin!"
    assert await describe_trip_async_context(ctx, trip, stops) == "Trip: Paris, Berlin!"
    assert describe_trip() == "London!"
    assert (
        inspect.signature(describe_trip.fn).parameters["trip"].default is DEFAULT_TRIP
    )
