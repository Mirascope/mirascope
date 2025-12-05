"""Tests for versioning module with tracing attributes."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import patch

import pytest
from inline_snapshot import snapshot
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from mirascope.ops import ClosureComputationError, VersionInfo, session, version
from mirascope.ops._internal.closure import Closure

from .utils import extract_span_data


@pytest.fixture(autouse=True)
def clear_closure_cache() -> Generator[None, None, None]:
    """Ensure Closure.from_fn cache is cleared between tests."""
    Closure.from_fn.cache_clear()
    yield
    Closure.from_fn.cache_clear()


def test_closure_computation_failure() -> None:
    """Ensures `VersionedFunction`s operate like `TracedFunction`s when closure computation fails."""
    with patch(
        "mirascope.ops._internal.closure.Closure.from_fn",
        side_effect=ClosureComputationError(qualified_name="fn"),
    ):

        @version
        def fn() -> str:
            return "ok"

        result = fn()
        assert result == "ok"

        @version
        async def async_fn() -> str:
            return "ok"

        assert async_fn.closure is None


def test_version_with_all_decorator_arguments(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test @version decorator with all arguments (name, tags, description, metadata)."""

    @version(
        name="book_recommender",
        tags=["production", "ml"],
        metadata={"owner": "team-ml", "ticket": "ENG-1234"},
    )
    def recommend_book(genre: str) -> str:
        """Recommends books based on genre"""
        return f"Recommend a {genre} book"

    assert recommend_book.name == "book_recommender"
    assert recommend_book.tags == ("ml", "production")
    assert recommend_book.closure is not None
    assert recommend_book.closure.docstring == "Recommends books based on genre"
    assert recommend_book.metadata == {"owner": "team-ml", "ticket": "ENG-1234"}

    result = recommend_book("fantasy")
    assert result == "Recommend a fantasy book"

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend_book",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend_book",
                "mirascope.fn.is_async": False,
                "mirascope.fn.module": "ops.test_versioning",
                "mirascope.fn.hash": span_data["attributes"]["mirascope.fn.hash"],
                "mirascope.fn.signature_hash": span_data["attributes"][
                    "mirascope.fn.signature_hash"
                ],
                "mirascope.trace.tags": ("ml", "production"),
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.metadata": '{"owner":"team-ml","ticket":"ENG-1234"}',
                "mirascope.trace.arg_values": '{"genre":"fantasy"}',
                "mirascope.version.name": "book_recommender",
                "mirascope.version.description": "Recommends books based on genre",
                "mirascope.trace.output": "Recommend a fantasy book",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.asyncio
async def test_async_version_with_all_decorator_arguments(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test async @version decorator with all arguments (name, tags, description, metadata)."""

    @version(
        name="async_recommender",
        tags=["staging"],
        metadata={"env": "staging"},
    )
    async def recommend_async(genre: str) -> str:
        """Async book recommender"""
        return f"Async recommend a {genre} book"

    assert recommend_async.name == "async_recommender"
    assert recommend_async.tags == ("staging",)
    assert recommend_async.closure is not None
    assert recommend_async.closure.docstring == "Async book recommender"
    assert recommend_async.metadata == {"env": "staging"}

    result = await recommend_async("mystery")
    assert result == "Async recommend a mystery book"

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend_async",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend_async",
                "mirascope.fn.is_async": True,
                "mirascope.fn.module": "ops.test_versioning",
                "mirascope.fn.hash": span_data["attributes"]["mirascope.fn.hash"],
                "mirascope.fn.signature_hash": span_data["attributes"][
                    "mirascope.fn.signature_hash"
                ],
                "mirascope.trace.tags": ("staging",),
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.metadata": '{"env":"staging"}',
                "mirascope.trace.arg_values": '{"genre":"mystery"}',
                "mirascope.version.name": "async_recommender",
                "mirascope.version.description": "Async book recommender",
                "mirascope.trace.output": "Async recommend a mystery book",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


def test_version_with_default_arguments(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test @version decorator with default argument values."""

    @version
    def compute(x: int) -> int:
        return x * 2

    assert compute.name is None
    assert compute.tags == ()
    assert compute.closure is not None
    assert compute.closure.docstring is None
    assert compute.metadata == {}

    result = compute(5)
    assert result == 10

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "compute",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "compute",
                "mirascope.fn.is_async": False,
                "mirascope.fn.module": "ops.test_versioning",
                "mirascope.fn.hash": span_data["attributes"]["mirascope.fn.hash"],
                "mirascope.fn.signature_hash": span_data["attributes"][
                    "mirascope.fn.signature_hash"
                ],
                "mirascope.trace.arg_types": '{"x":"int"}',
                "mirascope.trace.arg_values": '{"x":5}',
                "mirascope.trace.output": 10,
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


def test_version_with_empty_parens(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test @version() decorator with empty parentheses."""

    @version()
    def compute(x: int) -> int:
        return x * 3

    assert compute.name is None
    assert compute.tags == ()
    assert compute.closure is not None
    assert compute.closure.docstring is None
    assert compute.metadata == {}

    result = compute(4)
    assert result == 12

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "compute",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "compute",
                "mirascope.fn.is_async": False,
                "mirascope.fn.module": "ops.test_versioning",
                "mirascope.fn.hash": span_data["attributes"]["mirascope.fn.hash"],
                "mirascope.fn.signature_hash": span_data["attributes"][
                    "mirascope.fn.signature_hash"
                ],
                "mirascope.trace.arg_types": '{"x":"int"}',
                "mirascope.trace.arg_values": '{"x":4}',
                "mirascope.trace.output": 12,
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


def test_version_sync(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test @version decorator captures args and result for sync functions."""

    @version
    def multiply(x: int, y: int) -> int:
        return x * y

    result = multiply(5, 7)
    wrapped_result = multiply.wrapped(5, 7)

    assert result == 35
    assert wrapped_result.result == 35

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 2

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "multiply",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "multiply",
                "mirascope.fn.is_async": False,
                "mirascope.fn.module": "ops.test_versioning",
                "mirascope.fn.hash": extract_span_data(spans[0])["attributes"][
                    "mirascope.fn.hash"
                ],
                "mirascope.fn.signature_hash": extract_span_data(spans[0])[
                    "attributes"
                ]["mirascope.fn.signature_hash"],
                "mirascope.trace.arg_types": '{"x":"int","y":"int"}',
                "mirascope.trace.arg_values": '{"x":5,"y":7}',
                "mirascope.trace.output": 35,
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )

    wrapped_span_data = extract_span_data(spans[1])
    assert wrapped_span_data == span_data


@pytest.mark.asyncio
async def test_version_async(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test async versioning functionality."""
    import asyncio

    @version
    async def process_data(data: dict[str, int]) -> dict[str, float]:
        await asyncio.sleep(0.001)
        return {k: float(v * 2) for k, v in data.items()}

    data, expected_processed_data = {"a": 1, "b": 2}, {"a": 2.0, "b": 4.0}
    result = await process_data(data)
    wrapped_result = await process_data.wrapped(data)

    assert result == expected_processed_data
    assert wrapped_result.result == expected_processed_data

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 2

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "process_data",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "process_data",
                "mirascope.fn.is_async": True,
                "mirascope.fn.module": "ops.test_versioning",
                "mirascope.fn.hash": extract_span_data(spans[0])["attributes"][
                    "mirascope.fn.hash"
                ],
                "mirascope.fn.signature_hash": extract_span_data(spans[0])[
                    "attributes"
                ]["mirascope.fn.signature_hash"],
                "mirascope.trace.arg_types": '{"data":"dict[str, int]"}',
                "mirascope.trace.arg_values": '{"data":{"a":1,"b":2}}',
                "mirascope.trace.output": '{"a":2.0,"b":4.0}',
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )

    wrapped_span_data = extract_span_data(spans[1])
    assert wrapped_span_data == span_data


def test_version_with_session(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that @version decorator records session ID from active session."""

    @version
    def compute(x: int) -> int:
        return x * 10

    with session(id="version-session-789"):
        result = compute(3)

    assert result == 30

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "compute",
            "attributes": {
                "mirascope.ops.session.id": "version-session-789",
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "compute",
                "mirascope.fn.is_async": False,
                "mirascope.fn.module": "ops.test_versioning",
                "mirascope.fn.hash": span_data["attributes"]["mirascope.fn.hash"],
                "mirascope.fn.signature_hash": span_data["attributes"][
                    "mirascope.fn.signature_hash"
                ],
                "mirascope.trace.arg_types": '{"x":"int"}',
                "mirascope.trace.arg_values": '{"x":3}',
                "mirascope.trace.output": 30,
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.asyncio
async def test_async_version_with_session(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that async @version decorator records session ID from active session."""

    @version
    async def compute(x: int) -> int:
        return x * 20

    with session(id="async-version-session-999"):
        result = await compute(4)

    assert result == 80

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "compute",
            "attributes": {
                "mirascope.ops.session.id": "async-version-session-999",
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "compute",
                "mirascope.fn.is_async": True,
                "mirascope.fn.module": "ops.test_versioning",
                "mirascope.fn.hash": span_data["attributes"]["mirascope.fn.hash"],
                "mirascope.fn.signature_hash": span_data["attributes"][
                    "mirascope.fn.signature_hash"
                ],
                "mirascope.trace.arg_types": '{"x":"int"}',
                "mirascope.trace.arg_values": '{"x":4}',
                "mirascope.trace.output": 80,
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


def test_version_wrapped_method(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test @version decorator with .wrapped() method."""

    @version
    def multiply(x: int, y: int) -> int:
        return x * y

    wrapped_result = multiply.wrapped(5, 7)

    assert wrapped_result.result == 35

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data["name"] == "multiply"
    assert span_data["attributes"]["mirascope.trace.output"] == 35


@pytest.mark.asyncio
async def test_async_version_wrapped_method(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test async @version decorator with .wrapped() method."""

    @version
    async def multiply(x: int, y: int) -> int:
        return x * y

    wrapped_result = await multiply.wrapped(5, 7)

    assert wrapped_result.result == 35

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data["name"] == "multiply"
    assert span_data["attributes"]["mirascope.trace.output"] == 35


def test_version_with_function_uuid(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that function_uuid is set on span when _ensure_registration returns a UUID."""

    @version
    def compute(x: int) -> int:
        return x * 2

    with patch.object(compute, "_ensure_registration", return_value="test-uuid-123"):
        result = compute(5)

    assert result == 10

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data["attributes"]["function_uuid"] == "test-uuid-123"


@pytest.mark.asyncio
async def test_async_version_with_function_uuid(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that function_uuid is set on span when async _ensure_registration returns a UUID."""

    @version
    async def compute(x: int) -> int:
        return x * 2

    async def mock_ensure_registration() -> str:
        return "async-test-uuid-456"

    with patch.object(compute, "_ensure_registration", mock_ensure_registration):
        result = await compute(5)

    assert result == 10

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data["attributes"]["function_uuid"] == "async-test-uuid-456"


def test_version_info_property() -> None:
    """Test version_info property returns correct VersionInfo with all fields."""

    @version(
        name="book_recommender",
        tags=["production", "ml"],
        metadata={"owner": "team-ml", "ticket": "ENG-1234"},
    )
    def recommend_book(genre: str) -> str:
        """Recommends books based on genre"""
        return f"Recommend a {genre} book"

    info = recommend_book.version_info

    assert info is not None
    assert isinstance(info, VersionInfo)

    assert info == snapshot(
        VersionInfo(
            uuid=None,
            hash="5237bac10a23a22dc44349a360ea92e1fb8afc019f8003be6fa387e0a60395d7",
            signature_hash="6c72d21b0b804df8f8d9c29c4a48ef20aa33659c088afd6c3396fdb48ee7f261",
            name="book_recommender",
            description="Recommends books based on genre",
            version="1.0",
            tags=("ml", "production"),
            metadata={"owner": "team-ml", "ticket": "ENG-1234"},
        )
    )


def test_version_info_uses_function_name_when_no_custom_name() -> None:
    """Test version_info uses closure name when no custom name is provided."""

    @version
    def compute(x: int) -> int:
        return x * 2

    info = compute.version_info

    assert isinstance(info, VersionInfo)

    assert info == snapshot(
        VersionInfo(
            uuid=None,
            hash="c170404d149195e46de41dbfead33d1b2da0a6981a83d7af77db042dff5a021b",
            signature_hash="557b953f8c5541781e42f0b46f5c901b0411b0c172cc83a075e5a18c8866593b",
            name="compute",
            description=None,
            version="1.0",
            tags=(),
            metadata={},
        )
    )


@pytest.mark.asyncio
async def test_async_version_info_property() -> None:
    """Test version_info property works correctly on async versioned functions."""

    @version(
        name="async_recommender",
        tags=["staging"],
        metadata={"env": "staging"},
    )
    async def recommend_async(genre: str) -> str:
        """Async book recommender"""
        return f"Async recommend a {genre} book"

    info = recommend_async.version_info

    assert info is not None
    assert isinstance(info, VersionInfo)

    assert info == snapshot(
        VersionInfo(
            uuid=None,
            hash="31a4179fa785e06d3eeb722d526a89097cd3765fd520f008cb829873082f098c",
            signature_hash="dd9d176b5fcd78819422d7c50745741f737f50874d3a4c2bee6866da2dcc339f",
            name="async_recommender",
            description="Async book recommender",
            version="1.0",
            tags=("staging",),
            metadata={"env": "staging"},
        )
    )


def test_version_info_returns_none_when_closure_fails() -> None:
    """Test version_info returns None when closure computation fails."""
    with patch(
        "mirascope.ops._internal.closure.Closure.from_fn",
        side_effect=ClosureComputationError(qualified_name="fn"),
    ):

        @version
        def fn() -> str:
            return "ok"

        assert fn.closure is None
        assert fn.version_info is None


def test_version_info_is_cached() -> None:
    """Test version_info property is cached and returns same instance."""

    @version
    def compute(x: int) -> int:
        return x * 2

    info1 = compute.version_info
    info2 = compute.version_info

    assert info1 is info2


def test_version_info_instantiation() -> None:
    """Test VersionInfo dataclass can be instantiated and fields accessed."""
    info = VersionInfo(
        uuid="test-uuid-123",
        hash="abc123def456",
        signature_hash="",
        name="my_function",
        description="A test function",
        version="1.0",
        tags=("production", "v1"),
        metadata={"owner": "team-ml", "ticket": "ENG-1234"},
    )

    assert info == snapshot(
        VersionInfo(
            uuid="test-uuid-123",
            hash="abc123def456",
            signature_hash="",
            name="my_function",
            description="A test function",
            version="1.0",
            tags=("production", "v1"),
            metadata={"owner": "team-ml", "ticket": "ENG-1234"},
        )
    )


def test_version_info_with_none_values() -> None:
    """Test VersionInfo with None uuid and description (before server registration)."""
    info = VersionInfo(
        uuid=None,
        hash="abc123",
        signature_hash="",
        name="unregistered_fn",
        description=None,
        version="0.1",
        tags=(),
        metadata={},
    )

    assert info == snapshot(
        VersionInfo(
            uuid=None,
            hash="abc123",
            signature_hash="",
            name="unregistered_fn",
            description=None,
            version="0.1",
            tags=(),
            metadata={},
        )
    )
