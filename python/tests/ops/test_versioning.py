"""Tests for versioning module with tracing attributes."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import patch

import pytest
from inline_snapshot import snapshot
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from mirascope import llm, ops
from mirascope.ops import ClosureComputationError, VersionInfo, session, version
from mirascope.ops._internal.closure import Closure
from mirascope.ops._internal.versioned_calls import (
    _compute_closure_from_call,  # pyright: ignore[reportPrivateUsage]
)

from .utils import extract_span_data


@pytest.fixture(autouse=True, scope="function")
def initialize() -> Generator[None, None, None]:
    """Initialize ops configuration and LLM instrumentation for each test."""
    ops.configure()
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
                "mirascope.fn.module": "ops.test_versioning",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.arg_values": '{"genre":"fantasy"}',
                "mirascope.trace.tags": ("ml", "production"),
                "mirascope.trace.metadata": '{"owner":"team-ml","ticket":"ENG-1234"}',
                "mirascope.version.hash": "5237bac10a23a22dc44349a360ea92e1fb8afc019f8003be6fa387e0a60395d7",
                "mirascope.version.signature_hash": "6c72d21b0b804df8f8d9c29c4a48ef20aa33659c088afd6c3396fdb48ee7f261",
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
                "mirascope.fn.module": "ops.test_versioning",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"genre":"str"}',
                "mirascope.trace.arg_values": '{"genre":"mystery"}',
                "mirascope.trace.tags": ("staging",),
                "mirascope.trace.metadata": '{"env":"staging"}',
                "mirascope.version.hash": "31a4179fa785e06d3eeb722d526a89097cd3765fd520f008cb829873082f098c",
                "mirascope.version.signature_hash": "dd9d176b5fcd78819422d7c50745741f737f50874d3a4c2bee6866da2dcc339f",
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
                "mirascope.fn.module": "ops.test_versioning",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"x":"int"}',
                "mirascope.trace.arg_values": '{"x":5}',
                "mirascope.version.hash": "c170404d149195e46de41dbfead33d1b2da0a6981a83d7af77db042dff5a021b",
                "mirascope.version.signature_hash": "557b953f8c5541781e42f0b46f5c901b0411b0c172cc83a075e5a18c8866593b",
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
                "mirascope.fn.module": "ops.test_versioning",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"x":"int"}',
                "mirascope.trace.arg_values": '{"x":4}',
                "mirascope.version.hash": "394a50b0a209c7063a82069a95cda071eada3a97fc3656e2b898d28b49fd95f2",
                "mirascope.version.signature_hash": "d2006ef36ed7ecb416bb6d1487cfbe5e8c9eafbf4ee865b88d875f4fe4bcc158",
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
                "mirascope.fn.module": "ops.test_versioning",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"x":"int","y":"int"}',
                "mirascope.trace.arg_values": '{"x":5,"y":7}',
                "mirascope.version.hash": "04fe91ab23242c63bb8a2013f17df9fbe5378ec20c0cc35467f06c8fa8a14373",
                "mirascope.version.signature_hash": "0c457fa03ae6f618e1c3b063d863881997103c9f17e7b3b59a86ceb0f0d74085",
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
                "mirascope.fn.module": "ops.test_versioning",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"data":"dict[str, int]"}',
                "mirascope.trace.arg_values": '{"data":{"a":1,"b":2}}',
                "mirascope.version.hash": "88e96c471ead265f7c48a24bc48910d595d637bfa323c545e4745ffbdfd81cd7",
                "mirascope.version.signature_hash": "d18d86a9986299ae93164d8d886eba4a32bc9e213134dc92113ae3cac6170408",
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
                "mirascope.fn.module": "ops.test_versioning",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"x":"int"}',
                "mirascope.trace.arg_values": '{"x":3}',
                "mirascope.version.hash": "9149426872615a93b816bf0dc4aab6e745c0c6e8143cb314a266944c9f7cc0f0",
                "mirascope.version.signature_hash": "557b953f8c5541781e42f0b46f5c901b0411b0c172cc83a075e5a18c8866593b",
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
                "mirascope.fn.module": "ops.test_versioning",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"x":"int"}',
                "mirascope.trace.arg_values": '{"x":4}',
                "mirascope.version.hash": "a50e892e8a96846305b48320c2b3d708ba02bb170412aec0e5e17c31437e0ecd",
                "mirascope.version.signature_hash": "4c1cec07ce867f76ef0e07158f45f79a11125129b6b5eb5d42ad8be08a9c0dd0",
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
from mirascope import llm, ops


@ops.version(
    name="book_recommender",
    tags=["production"],
    metadata={"team": "ml"},
)
@llm.call("openai/gpt-4o-mini")
def recommend(genre: str) -> str:
    return f"Recommend a {genre} book."
""")

    info = recommend.version_info
    assert info is not None and isinstance(info, VersionInfo)
    assert info == snapshot(
        VersionInfo(
            uuid=None,
            hash="e1f15d277a7d1660f1114323ca62776c66595e5c71cd4e03b80f5a68ab762887",
            signature_hash="b150356b913e618ee78d5e70c96d5077bbabd67bcfc1dcdd567c89ea5f3c6fa4",
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"args":["fantasy"],"kwargs":{}}',
                "mirascope.version.hash": "76a7b11e288b2363ec592d668f67ad432a10a0b914c311a4848b6be707d4d38d",
                "mirascope.version.signature_hash": "b85dbb2d72f8337e8096866160b19224be513ed1806d27a65dc03663b61b22b8",
                "mirascope.version.version": "1.0",
                "mirascope.trace.output": "I highly recommend **\"The Name of the Wind\" by Patrick Rothfuss**. It's the first book in the Kingkiller Chronicle series and follows the story of Kvothe, a gifted young man who becomes a legendary figure. The narrative weaves together magic, music, and adventure, all told in Kvothe's own voice as he recounts his life's journey. The writing is beautiful, and the world-building is rich and immersive. Enjoy your reading!",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
def test_versioned_call_wrapped_method(span_exporter: InMemorySpanExporter) -> None:
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"args":["mystery"],"kwargs":{}}',
                "mirascope.version.hash": "76a7b11e288b2363ec592d668f67ad432a10a0b914c311a4848b6be707d4d38d",
                "mirascope.version.signature_hash": "b85dbb2d72f8337e8096866160b19224be513ed1806d27a65dc03663b61b22b8",
                "mirascope.version.version": "1.0",
                "mirascope.trace.output": "I recommend **\"The No. 1 Ladies' Detective Agency\"** by Alexander McCall Smith. It's a charming mystery set in Botswana, featuring the clever and resourceful Precious Ramotswe as she solves various cases with a unique blend of humor and insight. The book combines an engaging storyline with rich cultural details, making it both an enjoyable read and a delightful introduction to the series.",
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
def test_versioned_call_call_method(span_exporter: InMemorySpanExporter) -> None:
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"args":["fantasy"],"kwargs":{}}',
                "mirascope.version.hash": "76a7b11e288b2363ec592d668f67ad432a10a0b914c311a4848b6be707d4d38d",
                "mirascope.version.signature_hash": "b85dbb2d72f8337e8096866160b19224be513ed1806d27a65dc03663b61b22b8",
                "mirascope.version.version": "1.0",
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
def test_versioned_call_wrapped_stream(span_exporter: InMemorySpanExporter) -> None:
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
            "name": "stream",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "stream",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"args":["adventure"],"kwargs":{}}',
                "mirascope.version.hash": "76a7b11e288b2363ec592d668f67ad432a10a0b914c311a4848b6be707d4d38d",
                "mirascope.version.signature_hash": "b85dbb2d72f8337e8096866160b19224be513ed1806d27a65dc03663b61b22b8",
                "mirascope.version.version": "1.0",
                "mirascope.trace.output": "**[No Content]**",
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"args":["horror"],"kwargs":{}}',
                "mirascope.version.hash": "5e8d200470c1ca96f0d9898bc7fb3582dd376bd5fc1f931d4694f1ca16d81791",
                "mirascope.version.signature_hash": "5e70c3fd765650ffaf302c8281a5cfae52c45a760aa7724c249dcf8d238c8765",
                "mirascope.version.version": "1.0",
                "mirascope.trace.output": 'I recommend **"The Haunting of Hill House" by Shirley Jackson**. This classic novel explores the eerie and unsettling experiences of a group of people staying in a supposedly haunted mansion. Jackson\'s atmospheric writing and psychological tension create a chilling experience, making it a must-read for horror fans. If you\'re looking for something more contemporary, consider **"Mexican Gothic" by Silvia Moreno-Garcia**, which combines elements of gothic horror with a rich cultural backdrop. Both books offer unique and compelling takes on the genre!',
            },
            "status": {"status_code": "UNSET", "description": None},
            "events": [],
        }
    )


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_versioned_async_call_call_method(
    span_exporter: InMemorySpanExporter,
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"args":["horror"],"kwargs":{}}',
                "mirascope.version.hash": "5e8d200470c1ca96f0d9898bc7fb3582dd376bd5fc1f931d4694f1ca16d81791",
                "mirascope.version.signature_hash": "5e70c3fd765650ffaf302c8281a5cfae52c45a760aa7724c249dcf8d238c8765",
                "mirascope.version.version": "1.0",
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"ctx":"Context","args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"args":["fantasy"],"kwargs":{}}',
                "mirascope.version.hash": "d4e3376a2b4f08c3f0913f581a4902c3208dfc00c66297f4caf718d19aa0612d",
                "mirascope.version.signature_hash": "705465be5837caf8c33b7319e7f0fd0b6a81dcd7a89cb099e4fa6e76fc2880f8",
                "mirascope.version.version": "1.0",
                "mirascope.trace.output": 'I highly recommend **"The Name of the Wind" by Patrick Rothfuss**. This novel is the first book in the *Kingkiller Chronicle* series and follows the story of Kvothe, a gifted young man who grows up to become a legendary figure. The narrative combines rich world-building, a unique magic system, and its protagonist\'s journey through love, loss, and the pursuit of knowledge. The prose is lyrical, making it a joy to read while exploring themes of storytelling and identity. Perfect for fans of intricate plots and character-driven tales!',
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": True,
                "mirascope.trace.arg_types": '{"ctx":"Context","args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"ctx":{"deps":"As a librarian,"},"args":["mystery"],"kwargs":{}}',
                "mirascope.version.hash": "50b2b4f589367939f530073654e53599b461083c656b1e17effaea958c3610f1",
                "mirascope.version.signature_hash": "bc0660ba28abdfb06a4f855865d1bb4e306f8c4c223360a1e5ade287fc443f8f",
                "mirascope.version.version": "1.0",
                "mirascope.trace.output": 'I recommend **"The Guest List" by Lucy Foley**. This gripping mystery unfolds during a lavish wedding celebration on a remote Irish island. As the guests gather, tensions rise, and secrets begin to surface, culminating in a shocking murder. The narrative shifts between multiple perspectives, keeping you guessing until the very end. It\'s a fantastic blend of suspense, rich character development, and atmospheric setting—perfect for fans of psychological thrillers!',
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
def test_versioned_call_with_tags(span_exporter: InMemorySpanExporter) -> None:
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
            "name": "call",
            "attributes": {
                "mirascope.type": "trace",
                "mirascope.fn.qualname": "call",
                "mirascope.fn.module": "mirascope.llm.calls.calls",
                "mirascope.fn.is_async": False,
                "mirascope.trace.arg_types": '{"args":"P.args","kwargs":"P.kwargs"}',
                "mirascope.trace.arg_values": '{"args":["romance"],"kwargs":{}}',
                "mirascope.trace.tags": ("production", "recommendations"),
                "mirascope.version.hash": "550eeecde161f3c6629e208e1bc41fa2eb5ddb75381c8c6cf2592aea25d323e7",
                "mirascope.version.signature_hash": "6d70fb16697482fb44090153b4b6f1f1a32f84d25b8c74269945a99677c5b50e",
                "mirascope.version.version": "1.0",
                "mirascope.version.tags": ("production", "recommendations"),
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
