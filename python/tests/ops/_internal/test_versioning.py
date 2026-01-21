"""Tests for versioning module with tracing attributes."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from inline_snapshot import snapshot
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from mirascope import llm, ops
from mirascope.ops import ClosureComputationError, VersionInfo, session, version
from mirascope.ops._internal.closure import Closure
from mirascope.ops._internal.versioned_calls import (
    _compute_closure_from_call,  # pyright: ignore[reportPrivateUsage]
)
from tests.ops.utils import extract_span_data


@pytest.fixture(autouse=True, scope="function")
def initialize(tracer_provider: TracerProvider) -> Generator[None, None, None]:
    """Initialize ops configuration and LLM instrumentation for each test."""
    ops.configure(tracer_provider=tracer_provider)
    ops.instrument_llm()
    yield
    ops.uninstrument_llm()


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
                "mirascope.fn.module": "ops._internal.test_versioning",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.arg_values": '{"genre":"fantasy"}',
                "mirascope.trace.tags": ("ml", "production"),
                "mirascope.trace.metadata": '{"owner":"team-ml","ticket":"ENG-1234"}',
                "mirascope.version.hash": "fca936cf3f2fd455ba48dd450212ab85555fa359a1af67b837c1908d81adae58",
                "mirascope.version.signature_hash": "ba60803eef650bab7ae9b30bbb0b3421e416eb9b5b2571c4e5b36bf8fc6c2d2f",
                "mirascope.version.version": "1.0",
                "mirascope.version.name": "book_recommender",
                "mirascope.version.tags": ("ml", "production"),
                "mirascope.version.description": "Recommends books based on genre",
                "mirascope.version.meta.owner": "team-ml",
                "mirascope.version.meta.ticket": "ENG-1234",
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
                "mirascope.fn.module": "ops._internal.test_versioning",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.arg_values": '{"genre":"mystery"}',
                "mirascope.trace.tags": ("staging",),
                "mirascope.trace.metadata": '{"env":"staging"}',
                "mirascope.version.hash": "d6a313c1ec5544d61441c21947e3e64dd25fcc9571b644c9d21dd86a8eb3b398",
                "mirascope.version.signature_hash": "37f223943863bd6a446e5fac93fcdabc7b1c7c5654e7053943cc6e9c8aa8e353",
                "mirascope.version.version": "1.0",
                "mirascope.version.name": "async_recommender",
                "mirascope.version.tags": ("staging",),
                "mirascope.version.description": "Async book recommender",
                "mirascope.version.meta.env": "staging",
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
                "mirascope.fn.module": "ops._internal.test_versioning",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"x":"int"}',
                "mirascope.trace.arg_values": '{"x":5}',
                "mirascope.version.hash": "adfd8e5dfc41d8e936b1847d42c54894c0e8553bc1462e1b14775852b9adfdc9",
                "mirascope.version.signature_hash": "d12d2f1b52019811ac6fc845a48b6e419ee4e9e8b00b20241d5fe4617aeab35c",
                "mirascope.version.version": "1.0",
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
                "mirascope.fn.module": "ops._internal.test_versioning",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"x":"int"}',
                "mirascope.trace.arg_values": '{"x":4}',
                "mirascope.version.hash": "03e3be9d3aa942e13c033148737b2193362ba1b7b2578bf6663e4740f6a221b9",
                "mirascope.version.signature_hash": "d12d2f1b52019811ac6fc845a48b6e419ee4e9e8b00b20241d5fe4617aeab35c",
                "mirascope.version.version": "1.0",
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
                "mirascope.fn.module": "ops._internal.test_versioning",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"x":"int","y":"int"}',
                "mirascope.trace.arg_values": '{"x":5,"y":7}',
                "mirascope.version.hash": "a7b2e7221dfcd582555e021420bb03af69f44777537b6c3f903a00495d12c446",
                "mirascope.version.signature_hash": "9bc5d458c67f7f18711a951f5a7fbfaaf91bab3c9e68d7f4408017d9fd60753b",
                "mirascope.version.version": "1.0",
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
                "mirascope.fn.module": "ops._internal.test_versioning",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"data":"dict[str, int]"}',
                "mirascope.trace.arg_values": '{"data":{"a":1,"b":2}}',
                "mirascope.version.hash": "0c6ad72c20fe6d6608f865af2e43dbf32a15cac0c6fbdef976ac14fbf701280a",
                "mirascope.version.signature_hash": "f16109852d1364aed5e818d5685db423a600942db1dc1864773cb157b8a6f499",
                "mirascope.version.version": "1.0",
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
                "mirascope.fn.module": "ops._internal.test_versioning",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"x":"int"}',
                "mirascope.trace.arg_values": '{"x":3}',
                "mirascope.version.hash": "a5d3154570852e2c440b66fca7db2d04a806f83ac6f166c3e2da8464a1e4c82a",
                "mirascope.version.signature_hash": "d12d2f1b52019811ac6fc845a48b6e419ee4e9e8b00b20241d5fe4617aeab35c",
                "mirascope.version.version": "1.0",
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
                "mirascope.fn.module": "ops._internal.test_versioning",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"x":"int"}',
                "mirascope.trace.arg_values": '{"x":4}',
                "mirascope.version.hash": "5994d00bfc7af3b40e07cb168de11b3f8132b6ce1111f09ad9dbecfe3949c374",
                "mirascope.version.signature_hash": "0ba4723a5c88759f34c34ca38fc3f47709888c1555c96b74556709b11e413ea3",
                "mirascope.version.version": "1.0",
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
    assert span_data["attributes"]["mirascope.version.uuid"] == "test-uuid-123"


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
    assert span_data["attributes"]["mirascope.version.uuid"] == "async-test-uuid-456"


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
            hash="fca936cf3f2fd455ba48dd450212ab85555fa359a1af67b837c1908d81adae58",
            signature_hash="ba60803eef650bab7ae9b30bbb0b3421e416eb9b5b2571c4e5b36bf8fc6c2d2f",
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
            hash="adfd8e5dfc41d8e936b1847d42c54894c0e8553bc1462e1b14775852b9adfdc9",
            signature_hash="d12d2f1b52019811ac6fc845a48b6e419ee4e9e8b00b20241d5fe4617aeab35c",
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
            hash="d6a313c1ec5544d61441c21947e3e64dd25fcc9571b644c9d21dd86a8eb3b398",
            signature_hash="37f223943863bd6a446e5fac93fcdabc7b1c7c5654e7053943cc6e9c8aa8e353",
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


def test_versioned_call_closure_and_version_info() -> None:
    """Test VersionedCall.version_info returns correct VersionInfo."""

    @ops.version(
        name="book_recommender",
        tags=["production"],
        metadata={"team": "ml"},
    )
    @llm.call("openai/gpt-4o-mini")
    def recommend(genre: str) -> str:
        """Recommends books based on genre"""
        return f"Recommend a {genre} book."

    assert recommend.closure is not None
    assert recommend.closure.code == snapshot("""\
from mirascope import llm


@llm.call("openai/gpt-4o-mini")
def recommend(genre: str) -> str:
    return f"Recommend a {genre} book."
""")

    info = recommend.version_info
    assert info is not None and isinstance(info, VersionInfo)
    assert info == snapshot(
        VersionInfo(
            uuid=None,
            hash="2820850484af684cd70ef2b89cc09bd16dffd6003b2e8bb3ed0907232e44144e",
            signature_hash="d3afa65513fc5a9d79bcfdadd5775889dc259dc949c76d2c476ef916b4f234c2",
            name="book_recommender",
            description="Recommends books based on genre",
            version="1.0",
            tags=("production",),
            metadata={"team": "ml"},
        )
    )


@pytest.mark.vcr()
def test_versioned_call_sync(span_exporter: InMemorySpanExporter) -> None:
    """Test @ops.version on @llm.call creates VersionedCall and returns Response directly."""

    @ops.version
    @llm.call("openai/gpt-4o-mini")
    def recommend(genre: str) -> str:
        return f"Recommend a {genre} book."

    assert isinstance(recommend, ops.VersionedCall)

    response = recommend("fantasy")
    assert response.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "ops._internal.test_versioning",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.arg_values": '{"genre":"fantasy"}',
                "mirascope.version.hash": "2820850484af684cd70ef2b89cc09bd16dffd6003b2e8bb3ed0907232e44144e",
                "mirascope.version.signature_hash": "d3afa65513fc5a9d79bcfdadd5775889dc259dc949c76d2c476ef916b4f234c2",
                "mirascope.version.version": "1.0",
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"Recommend a fantasy book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"I recommend **\\"The Name of the Wind\\" by Patrick Rothfuss**. It\'s the first book in the *Kingkiller Chronicle* series and follows the story of Kvothe, a talented young man who becomes a legendary figure. The narrative blends elements of magic, music, and adventure with rich world-building and an engaging, character-driven plot. It\'s a fantastic read for anyone who loves immersive fantasy!"}]',
                "mirascope.response.usage": '{"input_tokens":12,"output_tokens":82,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":94}',
                "mirascope.trace.output": "I recommend **\"The Name of the Wind\" by Patrick Rothfuss**. It's the first book in the *Kingkiller Chronicle* series and follows the story of Kvothe, a talented young man who becomes a legendary figure. The narrative blends elements of magic, music, and adventure with rich world-building and an engaging, character-driven plot. It's a fantastic read for anyone who loves immersive fantasy!",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
def test_versioned_call_wrapped_method(
    span_exporter: InMemorySpanExporter,
    mirascope_api_key: None,
) -> None:
    """Test VersionedCall.wrapped() returns VersionedResult."""

    @ops.version
    @llm.call("openai/gpt-4o-mini")
    def recommend(genre: str) -> str:
        return f"Recommend a {genre} book."

    result = recommend.wrapped("mystery")
    assert result.result.content
    assert result.span_id is not None

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "ops._internal.test_versioning",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.arg_values": '{"genre":"mystery"}',
                "mirascope.version.hash": "2820850484af684cd70ef2b89cc09bd16dffd6003b2e8bb3ed0907232e44144e",
                "mirascope.version.signature_hash": "d3afa65513fc5a9d79bcfdadd5775889dc259dc949c76d2c476ef916b4f234c2",
                "mirascope.version.uuid": "f90e3dcd-5907-4822-aa74-f051a60e37de",
                "mirascope.version.version": "1.0",
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"Recommend a mystery book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"I recommend **\\"The No. 1 Ladies\' Detective Agency\\"** by Alexander McCall Smith. It\'s a charming mystery set in Botswana, featuring the clever and resourceful Precious Ramotswe as she solves various cases with a unique blend of humor and insight. The book combines an engaging storyline with rich cultural details, making it both an enjoyable read and a delightful introduction to the series."}]',
                "mirascope.response.usage": '{"input_tokens":12,"output_tokens":79,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":91}',
                "mirascope.trace.output": "I recommend **\"The No. 1 Ladies' Detective Agency\"** by Alexander McCall Smith. It's a charming mystery set in Botswana, featuring the clever and resourceful Precious Ramotswe as she solves various cases with a unique blend of humor and insight. The book combines an engaging storyline with rich cultural details, making it both an enjoyable read and a delightful introduction to the series.",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
def test_versioned_call_call_method(
    span_exporter: InMemorySpanExporter,
    mirascope_api_key: None,
) -> None:
    """Test VersionedCall.call() returns Response directly and creates span."""

    @ops.version
    @llm.call("openai/gpt-4o-mini")
    def recommend(genre: str) -> str:
        return f"Recommend a {genre} book."

    response = recommend.call("fantasy")
    assert response.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "ops._internal.test_versioning",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.arg_values": '{"genre":"fantasy"}',
                "mirascope.version.hash": "2820850484af684cd70ef2b89cc09bd16dffd6003b2e8bb3ed0907232e44144e",
                "mirascope.version.signature_hash": "d3afa65513fc5a9d79bcfdadd5775889dc259dc949c76d2c476ef916b4f234c2",
                "mirascope.version.uuid": "f90e3dcd-5907-4822-aa74-f051a60e37de",
                "mirascope.version.version": "1.0",
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"Recommend a fantasy book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"I recommend **\\"The Name of the Wind\\" by Patrick Rothfuss**. It’s the first book in the *The Kingkiller Chronicle* series and follows the story of Kvothe, a gifted young man who grows to become a legendary figure. The narrative weaves magic, music, and adventure in a richly detailed world. Its lyrical prose and deep character development make it a captivating read for fantasy lovers. Enjoy!"}]',
                "mirascope.response.usage": '{"input_tokens":12,"output_tokens":86,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":98}',
                "mirascope.trace.output": 'I recommend **"The Name of the Wind" by Patrick Rothfuss**. It’s the first book in the *The Kingkiller Chronicle* series and follows the story of Kvothe, a gifted young man who grows to become a legendary figure. The narrative weaves magic, music, and adventure in a richly detailed world. Its lyrical prose and deep character development make it a captivating read for fantasy lovers. Enjoy!',
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
def test_versioned_call_stream_method(span_exporter: InMemorySpanExporter) -> None:
    """Test VersionedCall.stream() returns StreamResponse directly."""

    @ops.version
    @llm.call("openai/gpt-4o-mini")
    def recommend(genre: str) -> str:
        return f"Recommend a {genre} book."

    stream_response = recommend.stream("adventure")
    stream_response.finish()
    assert stream_response.content


@pytest.mark.vcr()
def test_versioned_call_wrapped_stream(
    span_exporter: InMemorySpanExporter,
    mirascope_api_key: None,
) -> None:
    """Test VersionedCall.wrapped_stream() returns VersionedResult[StreamResponse]."""

    @ops.version
    @llm.call("openai/gpt-4o-mini")
    def recommend(genre: str) -> str:
        return f"Recommend a {genre} book."

    result = recommend.wrapped_stream("adventure")
    assert result.span_id is not None
    result.result.finish()
    assert result.result.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.stream",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.stream",
                "mirascope.fn.module": "ops._internal.test_versioning",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.arg_values": '{"genre":"adventure"}',
                "mirascope.version.hash": "2820850484af684cd70ef2b89cc09bd16dffd6003b2e8bb3ed0907232e44144e",
                "mirascope.version.signature_hash": "d3afa65513fc5a9d79bcfdadd5775889dc259dc949c76d2c476ef916b4f234c2",
                "mirascope.version.uuid": "f90e3dcd-5907-4822-aa74-f051a60e37de",
                "mirascope.version.version": "1.0",
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"Recommend a adventure book."}],"name":null}]',
                "mirascope.response.content": "[]",
                "mirascope.trace.output": "",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_versioned_async_call(span_exporter: InMemorySpanExporter) -> None:
    """Test @ops.version on async @llm.call creates VersionedAsyncCall."""

    @ops.version
    @llm.call("openai/gpt-4o-mini")
    async def recommend(genre: str) -> str:
        return f"Recommend a {genre} book."

    assert isinstance(recommend, ops.VersionedAsyncCall)

    response = await recommend("horror")
    assert response.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "ops._internal.test_versioning",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.arg_values": '{"genre":"horror"}',
                "mirascope.version.hash": "0391c2bfd9cae644a1b467679c5d6b8a03a8df17c733c4309e36838127bc6d85",
                "mirascope.version.signature_hash": "b9cd3d0dbb1c669832bb9bec2c556281f7587625908d698c7152a510b516ec26",
                "mirascope.version.version": "1.0",
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"Recommend a horror book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"I recommend **\\"The Haunting of Hill House\\" by Shirley Jackson**. This classic novel masterfully blends psychological tension with supernatural elements, following a group of people who experience unsettling occurrences in a mysterious mansion. Jackson\'s atmospheric writing and exploration of fear and isolation make it a compelling read for any horror enthusiast. Enjoy the chills!"}]',
                "mirascope.response.usage": '{"input_tokens":12,"output_tokens":67,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":79}',
                "mirascope.trace.output": 'I recommend **"The Haunting of Hill House" by Shirley Jackson**. This classic novel masterfully blends psychological tension with supernatural elements, following a group of people who experience unsettling occurrences in a mysterious mansion. Jackson\'s atmospheric writing and exploration of fear and isolation make it a compelling read for any horror enthusiast. Enjoy the chills!',
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_versioned_async_call_call_method(
    span_exporter: InMemorySpanExporter,
    mirascope_api_key: None,
) -> None:
    """Test VersionedAsyncCall.call() returns AsyncResponse directly."""

    @ops.version
    @llm.call("openai/gpt-4o-mini")
    async def recommend(genre: str) -> str:
        return f"Recommend a {genre} book."

    response = await recommend.call("horror")
    assert response.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "ops._internal.test_versioning",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.arg_values": '{"genre":"horror"}',
                "mirascope.version.hash": "0391c2bfd9cae644a1b467679c5d6b8a03a8df17c733c4309e36838127bc6d85",
                "mirascope.version.signature_hash": "b9cd3d0dbb1c669832bb9bec2c556281f7587625908d698c7152a510b516ec26",
                "mirascope.version.uuid": "1c6495c3-f5b4-4795-b99c-221ff3273156",
                "mirascope.version.version": "1.0",
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"Recommend a horror book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"I recommend \\"The Haunting of Hill House\\" by Shirley Jackson. It\'s a classic in the horror genre, exploring themes of fear, isolation, and psychological disturbance. The story follows a group of people who gather at a supposedly haunted mansion, and the eerie atmosphere and character dynamics make it both chilling and thought-provoking. Enjoy!"}]',
                "mirascope.response.usage": '{"input_tokens":12,"output_tokens":66,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":78}',
                "mirascope.trace.output": 'I recommend "The Haunting of Hill House" by Shirley Jackson. It\'s a classic in the horror genre, exploring themes of fear, isolation, and psychological disturbance. The story follows a group of people who gather at a supposedly haunted mansion, and the eerie atmosphere and character dynamics make it both chilling and thought-provoking. Enjoy!',
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_versioned_async_call_stream_method(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test VersionedAsyncCall.stream() returns AsyncStreamResponse directly."""

    @ops.version
    @llm.call("openai/gpt-4o-mini")
    async def recommend(genre: str) -> str:
        return f"Recommend a {genre} book."

    stream_response = await recommend.stream("adventure")
    await stream_response.finish()
    assert stream_response.content


@pytest.mark.vcr()
def test_versioned_context_call(span_exporter: InMemorySpanExporter) -> None:
    """Test @ops.version on @llm.call with context creates VersionedContextCall."""

    @ops.version
    @llm.call("openai/gpt-4o-mini")
    def recommend(ctx: llm.Context[str], genre: str) -> str:
        return f"{ctx.deps} Recommend a {genre} book."

    assert isinstance(recommend, ops.VersionedContextCall)

    ctx = llm.Context(deps="As a librarian,")
    response = recommend(ctx, "fantasy")
    assert response.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "ops._internal.test_versioning",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"ctx":"llm.Context[str]","genre":"str"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"genre":"fantasy"}',
                "mirascope.version.hash": "040ba4bb8fbe484b0fec96048fc27c7f1b8c8f3ed36a2ed94e92e8cc13407517",
                "mirascope.version.signature_hash": "3d98c672f65730494cad6b8cc3410c69067bbaa986d745e26f416e99b9db9373",
                "mirascope.version.version": "1.0",
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"As a librarian, Recommend a fantasy book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"I recommend **\\"The Night Circus\\" by Erin Morgenstern**. This enchanting novel tells the story of a mysterious circus that appears only at night, featuring exquisite performances and magical wonders. At the heart of the story is a competition between two young illusionists, Celia and Marco, bound to each other by a challenge that intertwines their fates. The lush, imaginative writing and intricate plot make it a captivating read for any fantasy enthusiast. Enjoy the magic!"}]',
                "mirascope.response.usage": '{"input_tokens":16,"output_tokens":94,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":110}',
                "mirascope.trace.output": 'I recommend **"The Night Circus" by Erin Morgenstern**. This enchanting novel tells the story of a mysterious circus that appears only at night, featuring exquisite performances and magical wonders. At the heart of the story is a competition between two young illusionists, Celia and Marco, bound to each other by a challenge that intertwines their fates. The lush, imaginative writing and intricate plot make it a captivating read for any fantasy enthusiast. Enjoy the magic!',
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
def test_versioned_context_call_call_method(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test VersionedContextCall.call() returns ContextResponse directly."""

    @ops.version
    @llm.call("openai/gpt-4o-mini")
    def recommend(ctx: llm.Context[str], genre: str) -> str:
        return f"{ctx.deps} Recommend a {genre} book."

    ctx = llm.Context(deps="As a librarian,")
    response = recommend.call(ctx, "fantasy")
    assert response.content


@pytest.mark.vcr()
def test_versioned_context_call_stream_method(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test VersionedContextCall.stream() returns ContextStreamResponse."""

    @ops.version
    @llm.call("openai/gpt-4o-mini")
    def recommend(ctx: llm.Context[str], genre: str) -> str:
        return f"{ctx.deps} Recommend a {genre} book."

    ctx = llm.Context(deps="As a librarian,")
    stream_response = recommend.stream(ctx, "adventure")
    stream_response.finish()
    assert stream_response.content


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_versioned_async_context_call(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test @ops.version on async @llm.call with context creates VersionedAsyncContextCall."""

    @ops.version
    @llm.call("openai/gpt-4o-mini")
    async def recommend(ctx: llm.Context[str], genre: str) -> str:
        return f"{ctx.deps} Recommend a {genre} book."

    assert isinstance(recommend, ops.VersionedAsyncContextCall)

    ctx = llm.Context(deps="As a librarian,")
    response = await recommend(ctx, "mystery")
    assert response.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "ops._internal.test_versioning",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"ctx":"llm.Context[str]","genre":"str"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"genre":"mystery"}',
                "mirascope.version.hash": "79085c0ac8178f3ae453795c87e509b7738abc1b1dcf58b045137c5cfe7e7923",
                "mirascope.version.signature_hash": "ae19bdc73bdb0f93f143b7df3c8cead8efc708c74688fcf000de53be729c5e96",
                "mirascope.version.version": "1.0",
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"As a librarian, Recommend a mystery book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"I recommend **\\"The Cuckoo\'s Calling\\"** by Robert Galbraith (pen name of J.K. Rowling). It\'s the first book in the Cormoran Strike series, featuring a private detective investigating the suspicious death of a supermodel. The plot is intricately woven with rich character development and sharp insights into the world of fame and fortune. It expertly balances suspense and a deep exploration of human nature, making it a compelling read for any mystery enthusiast. Enjoy!"}]',
                "mirascope.response.usage": '{"input_tokens":16,"output_tokens":97,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":113}',
                "mirascope.trace.output": "I recommend **\"The Cuckoo's Calling\"** by Robert Galbraith (pen name of J.K. Rowling). It's the first book in the Cormoran Strike series, featuring a private detective investigating the suspicious death of a supermodel. The plot is intricately woven with rich character development and sharp insights into the world of fame and fortune. It expertly balances suspense and a deep exploration of human nature, making it a compelling read for any mystery enthusiast. Enjoy!",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_versioned_async_context_call_call_method(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test VersionedAsyncContextCall.call() returns AsyncContextResponse."""

    @ops.version
    @llm.call("openai/gpt-4o-mini")
    async def recommend(ctx: llm.Context[str], genre: str) -> str:
        return f"{ctx.deps} Recommend a {genre} book."

    ctx = llm.Context(deps="As a librarian,")
    response = await recommend.call(ctx, "mystery")
    assert response.content


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_versioned_async_context_call_stream_method(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test VersionedAsyncContextCall.stream() returns AsyncContextStreamResponse."""

    @ops.version
    @llm.call("openai/gpt-4o-mini")
    async def recommend(ctx: llm.Context[str], genre: str) -> str:
        return f"{ctx.deps} Recommend a {genre} book."

    ctx = llm.Context(deps="As a librarian,")
    stream_response = await recommend.stream(ctx, "adventure")
    await stream_response.finish()
    assert stream_response.content


@pytest.mark.vcr()
def test_versioned_call_with_tags(
    span_exporter: InMemorySpanExporter,
    mirascope_api_key: None,
) -> None:
    """Test @ops.version(tags=[...]) passes tags to VersionedCall."""

    @ops.version(tags=["production", "recommendations"])
    @llm.call("openai/gpt-4o-mini")
    def recommend(genre: str) -> str:
        return f"Recommend a {genre} book."

    response = recommend("romance")
    assert response.content

    spans = span_exporter.get_finished_spans()
    trace_spans = [
        span
        for span in spans
        if (span.attributes or {}).get("mirascope.type") == "trace"
    ]
    assert len(trace_spans) == 1

    span_data = extract_span_data(trace_spans[0])
    assert span_data == snapshot(
        {
            "name": "recommend.call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "recommend.call",
                "mirascope.fn.module": "ops._internal.test_versioning",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.arg_values": '{"genre":"romance"}',
                "mirascope.trace.tags": ("production", "recommendations"),
                "mirascope.version.hash": "2820850484af684cd70ef2b89cc09bd16dffd6003b2e8bb3ed0907232e44144e",
                "mirascope.version.signature_hash": "d3afa65513fc5a9d79bcfdadd5775889dc259dc949c76d2c476ef916b4f234c2",
                "mirascope.version.uuid": "f90e3dcd-5907-4822-aa74-f051a60e37de",
                "mirascope.version.version": "1.0",
                "mirascope.version.tags": ("production", "recommendations"),
                "mirascope.response.provider_id": "openai",
                "mirascope.response.model_id": "openai/gpt-4o-mini",
                "mirascope.response.messages": '[{"role":"user","content":[{"type":"text","text":"Recommend a romance book."}],"name":null}]',
                "mirascope.response.content": '[{"type":"text","text":"I recommend **\\"The Kiss Quotient\\" by Helen Hoang**. It’s a refreshing story about Stella Lane, a successful woman with Asperger\'s, who decides to hire an escort to help her gain more experience in relationships. The book beautifully explores themes of love, acceptance, and self-discovery, with a charming romance that unfolds between Stella and the escort, Michael. It\'s both sweet and steamy, making it a wonderful read for romance lovers!"}]',
                "mirascope.response.usage": '{"input_tokens":12,"output_tokens":93,"cache_read_tokens":0,"cache_write_tokens":0,"reasoning_tokens":0,"total_tokens":105}',
                "mirascope.trace.output": "I recommend **\"The Kiss Quotient\" by Helen Hoang**. It’s a refreshing story about Stella Lane, a successful woman with Asperger's, who decides to hire an escort to help her gain more experience in relationships. The book beautifully explores themes of love, acceptance, and self-discovery, with a charming romance that unfolds between Stella and the escort, Michael. It's both sweet and steamy, making it a wonderful read for romance lovers!",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


def test_versioned_call_closure_extraction_failure() -> None:
    """Test VersionedCall handles closure extraction failure gracefully."""
    with patch(
        "mirascope.ops._internal.versioned_calls.Closure.from_fn",
        side_effect=ClosureComputationError(qualified_name="recommend"),
    ):

        @ops.version
        @llm.call("openai/gpt-4o-mini")
        def recommend(genre: str) -> str:
            return f"Recommend a {genre} book."

        assert recommend.closure is None
        assert recommend.version_info is None


def test_versioned_async_call_closure_extraction_failure() -> None:
    """Test VersionedAsyncCall handles closure extraction failure gracefully."""
    with patch(
        "mirascope.ops._internal.versioned_calls.Closure.from_fn",
        side_effect=ClosureComputationError(qualified_name="recommend"),
    ):

        @ops.version
        @llm.call("openai/gpt-4o-mini")
        async def recommend(genre: str) -> str:
            return f"Recommend a {genre} book."

        assert recommend.closure is None
        assert recommend.version_info is None


def test_versioned_context_call_closure_extraction_failure() -> None:
    """Test VersionedContextCall handles closure extraction failure gracefully."""
    with patch(
        "mirascope.ops._internal.versioned_calls.Closure.from_fn",
        side_effect=ClosureComputationError(qualified_name="recommend"),
    ):

        @ops.version
        @llm.call("openai/gpt-4o-mini")
        def recommend(ctx: llm.Context[str], genre: str) -> str:
            return f"{ctx.deps} Recommend a {genre} book."

        assert recommend.closure is None
        assert recommend.version_info is None


def test_versioned_async_context_call_closure_extraction_failure() -> None:
    """Test VersionedAsyncContextCall handles closure extraction failure gracefully."""
    with patch(
        "mirascope.ops._internal.versioned_calls.Closure.from_fn",
        side_effect=ClosureComputationError(qualified_name="recommend"),
    ):

        @ops.version
        @llm.call("openai/gpt-4o-mini")
        async def recommend(ctx: llm.Context[str], genre: str) -> str:
            return f"{ctx.deps} Recommend a {genre} book."

        assert recommend.closure is None
        assert recommend.version_info is None


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_versioned_async_call_wrapped_method(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test VersionedAsyncCall.wrapped() returns AsyncVersionedResult."""

    @ops.version
    @llm.call("openai/gpt-4o-mini")
    async def recommend(genre: str) -> str:
        return f"Recommend a {genre} book."

    result = await recommend.wrapped("fantasy")
    assert result.result.content
    assert result.span_id is not None


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_versioned_async_call_wrapped_stream_method(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test VersionedAsyncCall.wrapped_stream() returns AsyncVersionedResult."""

    @ops.version
    @llm.call("openai/gpt-4o-mini")
    async def recommend(genre: str) -> str:
        return f"Recommend a {genre} book."

    result = await recommend.wrapped_stream("adventure")
    assert result.span_id is not None
    await result.result.finish()
    assert result.result.content


@pytest.mark.vcr()
def test_versioned_context_call_wrapped_method(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test VersionedContextCall.wrapped() returns VersionedResult."""

    @ops.version
    @llm.call("openai/gpt-4o-mini")
    def recommend(ctx: llm.Context[str], genre: str) -> str:
        return f"{ctx.deps} Recommend a {genre} book."

    ctx = llm.Context(deps="As a librarian,")
    result = recommend.wrapped(ctx, "fantasy")
    assert result.result.content
    assert result.span_id is not None


@pytest.mark.vcr()
def test_versioned_context_call_wrapped_stream_method(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test VersionedContextCall.wrapped_stream() returns VersionedResult."""

    @ops.version
    @llm.call("openai/gpt-4o-mini")
    def recommend(ctx: llm.Context[str], genre: str) -> str:
        return f"{ctx.deps} Recommend a {genre} book."

    ctx = llm.Context(deps="As a librarian,")
    result = recommend.wrapped_stream(ctx, "adventure")
    assert result.span_id is not None
    result.result.finish()
    assert result.result.content


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_versioned_async_context_call_wrapped_method(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test VersionedAsyncContextCall.wrapped() returns AsyncVersionedResult."""

    @ops.version
    @llm.call("openai/gpt-4o-mini")
    async def recommend(ctx: llm.Context[str], genre: str) -> str:
        return f"{ctx.deps} Recommend a {genre} book."

    ctx = llm.Context(deps="As a librarian,")
    result = await recommend.wrapped(ctx, "fantasy")
    assert result.result.content
    assert result.span_id is not None


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_versioned_async_context_call_wrapped_stream_method(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test VersionedAsyncContextCall.wrapped_stream() returns AsyncVersionedResult."""

    @ops.version
    @llm.call("openai/gpt-4o-mini")
    async def recommend(ctx: llm.Context[str], genre: str) -> str:
        return f"{ctx.deps} Recommend a {genre} book."

    ctx = llm.Context(deps="As a librarian,")
    result = await recommend.wrapped_stream(ctx, "adventure")
    assert result.span_id is not None
    await result.result.finish()
    assert result.result.content


def test_compute_closure_from_call_fallback() -> None:
    """Test _compute_closure_from_call uses fn directly when no closure exists."""

    class MockPrompt:
        def fn(self) -> str:
            return "test"

    class MockCall:
        prompt = MockPrompt()

    mock_call = MockCall()
    result = _compute_closure_from_call(mock_call)  # pyright: ignore[reportArgumentType]
    assert result is not None
    assert isinstance(result, Closure)


@pytest.mark.vcr()
def test_version_registers_new_function(
    span_exporter: InMemorySpanExporter,
    mirascope_api_key: None,
) -> None:
    """Test that versioned function registers new function via API."""

    @version(name="test_register_new_fn", tags=["test"])
    def compute_new(x: int) -> int:
        return x * 2

    result = compute_new(5)
    assert result == 10

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "compute_new",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "compute_new",
                "mirascope.fn.module": "ops._internal.test_versioning",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"x":"int"}',
                "mirascope.trace.arg_values": '{"x":5}',
                "mirascope.trace.tags": ("test",),
                "mirascope.version.hash": "2b5f697ef9a0d908b6b6674005c6e0e5d19581834dafd9c41771ca6994b263d9",
                "mirascope.version.signature_hash": "3779bb3e22ca9b1dd5379cda31c2cdce8f3b5d27528c328270e7e196b67cc58a",
                "mirascope.version.uuid": "0b49be1b-0d15-4009-819f-16b4a4fcfb83",
                "mirascope.version.version": "1.0",
                "mirascope.version.name": "test_register_new_fn",
                "mirascope.version.tags": ("test",),
                "mirascope.trace.output": 10,
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
def test_version_uses_existing_function(
    span_exporter: InMemorySpanExporter,
    mirascope_api_key: None,
) -> None:
    """Test that versioned function uses existing function from API."""

    @version(name="test_existing_fn")
    def compute_existing(x: int) -> int:
        return x * 3

    result = compute_existing(5)
    assert result == 15

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "compute_existing",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "compute_existing",
                "mirascope.fn.module": "ops._internal.test_versioning",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"x":"int"}',
                "mirascope.trace.arg_values": '{"x":5}',
                "mirascope.version.hash": "b8be4f8989ddbe687f19b8b96f29094884a1e903728de2cea7b17a37c22c285e",
                "mirascope.version.signature_hash": "10c4ac91cbe5db326143343357a94d550db16f3242b05d6533ca504ed9e8dd43",
                "mirascope.version.uuid": "94b35c14-88fd-4930-9884-7c8b8a269135",
                "mirascope.version.version": "1.0",
                "mirascope.version.name": "test_existing_fn",
                "mirascope.trace.output": 15,
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_async_version_registers_new_function(
    span_exporter: InMemorySpanExporter,
    mirascope_api_key: None,
) -> None:
    """Test that async versioned function registers new function via API."""

    @version(name="test_async_register_fn", tags=["async-test"])
    async def async_compute_new(x: int) -> int:
        return x * 2

    result = await async_compute_new(5)
    assert result == 10

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "async_compute_new",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "async_compute_new",
                "mirascope.fn.module": "ops._internal.test_versioning",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"x":"int"}',
                "mirascope.trace.arg_values": '{"x":5}',
                "mirascope.trace.tags": ("async-test",),
                "mirascope.version.hash": "e29e925666db867702c08edf6cda0d34414d5284b34779efb6def7cddf39d450",
                "mirascope.version.signature_hash": "e895135474979165e8f95c8c3616326d740ad66821238ab65f8b0506645fce3e",
                "mirascope.version.uuid": "8373d50e-b7bf-440d-beaf-743681eb5ea1",
                "mirascope.version.version": "1.0",
                "mirascope.version.name": "test_async_register_fn",
                "mirascope.version.tags": ("async-test",),
                "mirascope.trace.output": 10,
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_async_version_uses_existing_function(
    span_exporter: InMemorySpanExporter,
    mirascope_api_key: None,
) -> None:
    """Test that async versioned function uses existing function from API."""

    @version(name="test_async_existing_fn")
    async def async_compute_existing(x: int) -> int:
        return x * 3

    result = await async_compute_existing(5)
    assert result == 15

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span_data = extract_span_data(spans[0])
    assert span_data == snapshot(
        {
            "name": "async_compute_existing",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "async_compute_existing",
                "mirascope.fn.module": "ops._internal.test_versioning",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"x":"int"}',
                "mirascope.trace.arg_values": '{"x":5}',
                "mirascope.version.hash": "7355652ef8883faeddcc7b95410e50e70559db4c7cee553e9e42047dcf7eda6d",
                "mirascope.version.signature_hash": "0abeec0082e47278ee7e07ee22dc13c14bd30d43d41e9da4a092a0f8f89dc9cb",
                "mirascope.version.uuid": "d7264ea1-9e52-4ecf-89bf-85b886a854e9",
                "mirascope.version.version": "1.0",
                "mirascope.version.name": "test_async_existing_fn",
                "mirascope.trace.output": 15,
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


def test_version_continues_when_get_client_fails(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that versioned function continues when get_sync_client fails."""

    @version
    def compute(x: int) -> int:
        return x * 2

    with patch(
        "mirascope.ops._internal.versioned_functions.get_sync_client",
        side_effect=Exception("Connection error"),
    ):
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
                    "mirascope.fn.module": "ops._internal.test_versioning",
                    "mirascope.fn.is_async": False,
                    "mirascope.trace.arg_types": '{"x":"int"}',
                    "mirascope.trace.arg_values": '{"x":5}',
                    "mirascope.version.hash": "adfd8e5dfc41d8e936b1847d42c54894c0e8553bc1462e1b14775852b9adfdc9",
                    "mirascope.version.signature_hash": "d12d2f1b52019811ac6fc845a48b6e419ee4e9e8b00b20241d5fe4617aeab35c",
                    "mirascope.version.version": "1.0",
                    "mirascope.trace.output": 10,
                },
                "status": {"status_code": "UNSET", "description": None},
                "events": [],
            }
        )


def test_version_continues_when_api_fails(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that versioned function continues when API call raises non-NotFoundError."""

    @version
    def compute(x: int) -> int:
        return x * 2

    mock_client = patch(
        "mirascope.ops._internal.versioned_functions.get_sync_client"
    ).start()
    mock_client.return_value.functions.findbyhash.side_effect = Exception(
        "Connection error"
    )

    try:
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
                    "mirascope.fn.module": "ops._internal.test_versioning",
                    "mirascope.fn.is_async": False,
                    "mirascope.trace.arg_types": '{"x":"int"}',
                    "mirascope.trace.arg_values": '{"x":5}',
                    "mirascope.version.hash": "adfd8e5dfc41d8e936b1847d42c54894c0e8553bc1462e1b14775852b9adfdc9",
                    "mirascope.version.signature_hash": "d12d2f1b52019811ac6fc845a48b6e419ee4e9e8b00b20241d5fe4617aeab35c",
                    "mirascope.version.version": "1.0",
                    "mirascope.trace.output": 10,
                },
                "status": {"status_code": "UNSET", "description": None},
                "events": [],
            }
        )
    finally:
        patch.stopall()


@pytest.mark.asyncio
async def test_async_version_continues_when_get_client_fails(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that async versioned function continues when get_async_client fails."""

    @version
    async def compute(x: int) -> int:
        return x * 2

    with patch(
        "mirascope.ops._internal.versioned_functions.get_async_client",
        side_effect=Exception("Connection error"),
    ):
        result = await compute(5)
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
                    "mirascope.fn.module": "ops._internal.test_versioning",
                    "mirascope.fn.is_async": True,
                    "mirascope.trace.arg_types": '{"x":"int"}',
                    "mirascope.trace.arg_values": '{"x":5}',
                    "mirascope.version.hash": "d891aa4c5746080deef063db11ea258137822c4914f85ba96c8426686af26530",
                    "mirascope.version.signature_hash": "0ba4723a5c88759f34c34ca38fc3f47709888c1555c96b74556709b11e413ea3",
                    "mirascope.version.version": "1.0",
                    "mirascope.trace.output": 10,
                },
                "status": {"status_code": "UNSET", "description": None},
                "events": [],
            }
        )


@pytest.mark.asyncio
async def test_async_version_continues_when_api_fails(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that async versioned function continues when API call raises non-NotFoundError."""

    @version
    async def compute(x: int) -> int:
        return x * 2

    mock_client = patch(
        "mirascope.ops._internal.versioned_functions.get_async_client"
    ).start()
    mock_client.return_value.functions.findbyhash = AsyncMock(
        side_effect=Exception("Connection error")
    )

    try:
        result = await compute(5)
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
                    "mirascope.fn.module": "ops._internal.test_versioning",
                    "mirascope.fn.is_async": True,
                    "mirascope.trace.arg_types": '{"x":"int"}',
                    "mirascope.trace.arg_values": '{"x":5}',
                    "mirascope.version.hash": "d891aa4c5746080deef063db11ea258137822c4914f85ba96c8426686af26530",
                    "mirascope.version.signature_hash": "0ba4723a5c88759f34c34ca38fc3f47709888c1555c96b74556709b11e413ea3",
                    "mirascope.version.version": "1.0",
                    "mirascope.trace.output": 10,
                },
                "status": {"status_code": "UNSET", "description": None},
                "events": [],
            }
        )
    finally:
        patch.stopall()


@pytest.mark.asyncio
async def test_async_version_continues_when_closure_is_none(
    span_exporter: InMemorySpanExporter,
) -> None:
    """Test that async versioned function continues when closure is None."""
    with patch(
        "mirascope.ops._internal.closure.Closure.from_fn",
        side_effect=ClosureComputationError(qualified_name="fn"),
    ):

        @version
        async def compute(x: int) -> int:
            return x * 2

        assert compute.closure is None

        result = await compute(5)
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
                    "mirascope.fn.module": "ops._internal.test_versioning",
                    "mirascope.fn.is_async": True,
                    "mirascope.trace.arg_types": '{"x":"int"}',
                    "mirascope.trace.arg_values": '{"x":5}',
                    "mirascope.trace.output": 10,
                },
                "status": {"status_code": "UNSET", "description": None},
                "events": [],
            }
        )
