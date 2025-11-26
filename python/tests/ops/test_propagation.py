"""Tests for context propagation utilities."""

from __future__ import annotations

import logging
import os
import threading
from collections.abc import Iterator, Mapping, MutableMapping
from unittest.mock import patch

import pytest
from inline_snapshot import snapshot
from opentelemetry import propagate, trace
from opentelemetry.context import Context
from opentelemetry.sdk.trace import TracerProvider

from mirascope.ops import (
    SESSION_HEADER_NAME,
    ContextPropagator,
    PropagatorFormat,
    extract_context,
    extract_session_id,
    get_propagator,
    inject_context,
    propagated_context,
    reset_propagator,
    session,
)
from mirascope.ops._internal.propagation import (
    ENV_PROPAGATOR_FORMAT,
    ENV_PROPAGATOR_SET_GLOBAL,
)
from mirascope.ops.exceptions import ConfigurationError

from .conftest import (
    PROPAGATOR_FORMATS,
    TRACEPARENT_PATTERN,
    VALID_SPAN_ID,
    VALID_TRACE_ID,
    VALID_TRACEPARENT,
)

PROPAGATOR_FORMAT_CONFIGS = [
    (None, {"traceparent"}),
    ("tracecontext", {"traceparent"}),
    ("b3", {"b3"}),
    ("b3multi", {"x-b3-traceid", "x-b3-spanid", "x-b3-sampled"}),
    ("jaeger", {"uber-trace-id"}),
    (
        "composite",
        {
            "traceparent",
            "b3",
            "x-b3-traceid",
            "x-b3-spanid",
            "x-b3-sampled",
            "uber-trace-id",
        },
    ),
]


class InvalidCarrier(Mapping[str, str]):
    """Mock carrier that raises errors during extraction."""

    def __getitem__(self, key: str) -> str:
        raise RuntimeError("extraction error")

    def __iter__(self) -> Iterator[str]:
        raise RuntimeError("extraction error")

    def __len__(self) -> int:
        raise RuntimeError("extraction error")


class ImmutableCarrier(MutableMapping[str, str]):
    """Mock carrier that raises errors during injection."""

    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def __getitem__(self, key: str) -> str:
        return self._data[key]

    def __setitem__(self, key: str, value: str) -> None:
        raise RuntimeError("injection error")

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)


def _configure_propagator(format_name: str) -> None:
    """Configure propagator format and reset singleton."""
    os.environ[ENV_PROPAGATOR_FORMAT] = format_name
    reset_propagator()


@pytest.mark.parametrize(
    ("propagator_format", "expected_headers"),
    PROPAGATOR_FORMAT_CONFIGS,
    ids=["default"] + PROPAGATOR_FORMATS,
)
def test_propagator_formats(
    propagator_format: PropagatorFormat | None,
    expected_headers: set[str],
    tracer_provider: TracerProvider,
) -> None:
    """Create correct propagator based on MIRASCOPE_PROPAGATOR environment variable."""
    if propagator_format is None:
        os.environ.pop(ENV_PROPAGATOR_FORMAT, None)
    else:
        os.environ[ENV_PROPAGATOR_FORMAT] = propagator_format

    context_propagator = ContextPropagator(set_global=False)

    tracer = tracer_provider.get_tracer(__name__)
    with tracer.start_as_current_span("test-span") as span:
        current_context = trace.set_span_in_context(span)
        carrier: dict[str, str] = {}
        context_propagator.inject_context(carrier, context=current_context)

        actual_headers = set(carrier)
        missing = expected_headers - actual_headers
        unexpected = actual_headers - expected_headers
        assert not missing, f"Missing headers: {missing}"
        assert not unexpected, f"Unexpected headers: {unexpected}"


def test_propagator_invalid_format_raises_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Raise ConfigurationError and log error for invalid propagator format."""
    os.environ[ENV_PROPAGATOR_FORMAT] = "invalid_format"

    with (
        caplog.at_level(logging.ERROR),
        pytest.raises(ConfigurationError) as exception_info,
    ):
        ContextPropagator()

    assert str(exception_info.value) == snapshot(
        "Invalid propagator format: invalid_format. "
        "Valid options: tracecontext, b3, b3multi, jaeger, composite"
    )
    assert caplog.record_tuples == snapshot(
        [
            (
                "mirascope.ops._internal.propagation",
                logging.ERROR,
                "Invalid propagator format: invalid_format. "
                "Valid options: tracecontext, b3, b3multi, jaeger, composite",
            )
        ]
    )


def test_propagator_sets_global_by_default() -> None:
    """Set the propagator as global textmap propagator by default."""
    os.environ[ENV_PROPAGATOR_FORMAT] = "tracecontext"
    propagator = ContextPropagator()
    assert propagate.get_global_textmap() is propagator._propagator  # pyright: ignore[reportPrivateUsage]


def test_propagator_respects_set_global_false() -> None:
    """Do not set global propagator when set_global=False."""
    os.environ[ENV_PROPAGATOR_FORMAT] = "tracecontext"
    previous_global = propagate.get_global_textmap()
    ContextPropagator(set_global=False)
    assert propagate.get_global_textmap() is previous_global


def test_propagator_respects_set_global_guard() -> None:
    """Do not set global propagator when _MIRASCOPE_PROPAGATOR_SET_GLOBAL is false."""
    os.environ[ENV_PROPAGATOR_FORMAT] = "tracecontext"
    os.environ[ENV_PROPAGATOR_SET_GLOBAL] = "false"
    previous_global = propagate.get_global_textmap()
    ContextPropagator()
    assert propagate.get_global_textmap() is previous_global


@pytest.mark.parametrize(
    ("carrier", "expected"),
    [
        pytest.param(
            {"traceparent": VALID_TRACEPARENT},
            {
                "is_valid": True,
                "trace_id": VALID_TRACE_ID,
                "span_id": VALID_SPAN_ID,
            },
            id="valid_headers",
        ),
        pytest.param(
            {"traceparent": "invalid-traceparent-format"},
            {"is_valid": False},
            id="invalid_headers",
        ),
        pytest.param(
            {},
            {"is_valid": False},
            id="missing_headers",
        ),
    ],
)
def test_propagator_extract_context(
    carrier: dict[str, str],
    expected: dict[str, bool | int],
) -> None:
    """Extract context from carrier with valid, invalid, or missing headers."""
    os.environ[ENV_PROPAGATOR_FORMAT] = "tracecontext"

    context_propagator = get_propagator()

    extracted_context = context_propagator.extract_context(carrier)

    assert isinstance(extracted_context, Context)

    extracted_span = trace.get_current_span(extracted_context)
    span_context = extracted_span.get_span_context()

    result: dict[str, bool | int] = {"is_valid": span_context.is_valid}
    if span_context.is_valid:
        result["trace_id"] = span_context.trace_id
        result["span_id"] = span_context.span_id

    assert result == expected


def test_propagator_handles_extraction_errors(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Log debug message when extraction fails on malformed carrier."""
    os.environ[ENV_PROPAGATOR_FORMAT] = "tracecontext"

    context_propagator = get_propagator()

    with caplog.at_level(logging.DEBUG):
        carrier = InvalidCarrier()
        result = context_propagator.extract_context(carrier)

        assert caplog.record_tuples == snapshot(
            [
                (
                    "mirascope.ops._internal.propagation",
                    logging.DEBUG,
                    "Failed to extract context from carrier: "
                    "RuntimeError: extraction error",
                )
            ]
        )
        assert isinstance(result, Context)


def test_propagator_injects_context_into_carrier(
    tracer_provider: TracerProvider,
) -> None:
    """Inject current context into carrier headers."""
    os.environ[ENV_PROPAGATOR_FORMAT] = "tracecontext"

    tracer = tracer_provider.get_tracer(__name__)

    context_propagator = get_propagator()

    with tracer.start_as_current_span("test-span") as span:
        current_context = trace.set_span_in_context(span)
        carrier: dict[str, str] = {}
        context_propagator.inject_context(carrier, context=current_context)

        assert set(carrier.keys()) == snapshot({"traceparent"})
        assert TRACEPARENT_PATTERN.match(carrier["traceparent"])


@pytest.mark.parametrize(
    "use_method",
    [
        pytest.param(True, id="method"),
        pytest.param(False, id="convenience_function"),
    ],
)
def test_inject_specific_context(
    tracer_provider: TracerProvider,
    use_method: bool,
) -> None:
    """Inject a specific context rather than current context."""
    os.environ[ENV_PROPAGATOR_FORMAT] = "tracecontext"

    tracer = tracer_provider.get_tracer(__name__)
    context_propagator = get_propagator()

    with tracer.start_as_current_span("test-span") as span:
        specific_context = Context()
        specific_context = trace.set_span_in_context(span, specific_context)

        carrier: dict[str, str] = {}

        if use_method:
            context_propagator.inject_context(carrier, context=specific_context)
        else:
            inject_context(carrier, context=specific_context)

        assert set(carrier.keys()) == snapshot({"traceparent"})


def test_propagator_handles_injection_errors(
    caplog: pytest.LogCaptureFixture,
    tracer_provider: TracerProvider,
) -> None:
    """Log debug message when injection fails on immutable carrier."""
    os.environ[ENV_PROPAGATOR_FORMAT] = "tracecontext"

    context_propagator = get_propagator()
    tracer = tracer_provider.get_tracer(__name__)

    with tracer.start_as_current_span("test-span") as span:
        current_context = trace.set_span_in_context(span)

        with caplog.at_level(logging.DEBUG):
            carrier = ImmutableCarrier()
            context_propagator.inject_context(carrier, context=current_context)

            assert caplog.record_tuples == snapshot(
                [
                    (
                        "mirascope.ops._internal.propagation",
                        logging.DEBUG,
                        "Failed to inject context into carrier: "
                        "RuntimeError: injection error",
                    )
                ]
            )


def test_get_propagator_singleton() -> None:
    """Return the same ContextPropagator instance on multiple calls."""
    first_call = get_propagator()
    second_call = get_propagator()

    assert first_call is second_call
    assert isinstance(first_call, ContextPropagator)


def test_get_propagator_creates_instance_once() -> None:
    """Create propagator instance only on first call to get_propagator."""
    reset_propagator()

    with patch(
        "mirascope.ops._internal.propagation.ContextPropagator", wraps=ContextPropagator
    ) as mock_constructor:
        get_propagator()
        get_propagator()
        get_propagator()

        assert mock_constructor.call_count == 1


def test_extract_context_convenience_function(
    valid_carrier: dict[str, str],
) -> None:
    """Module-level extract_context delegates to propagator instance."""

    extracted_context = extract_context(valid_carrier)

    assert isinstance(extracted_context, Context)

    extracted_span = trace.get_current_span(extracted_context)
    span_context = extracted_span.get_span_context()

    assert span_context.is_valid
    assert span_context.trace_id == VALID_TRACE_ID
    assert span_context.span_id == VALID_SPAN_ID


def test_inject_context_convenience_function(
    tracer_provider: TracerProvider,
) -> None:
    """Module-level inject_context delegates to propagator instance."""

    tracer = tracer_provider.get_tracer(__name__)

    with tracer.start_as_current_span("test-span") as span:
        current_context = trace.set_span_in_context(span)
        carrier: dict[str, str] = {}
        inject_context(carrier, context=current_context)

        assert set(carrier.keys()) == snapshot({"traceparent"})


def test_inject_extract_session_roundtrip(
    tracer_provider: TracerProvider,
) -> None:
    """Inject and extract session ID through carrier headers."""

    tracer = tracer_provider.get_tracer(__name__)

    with (
        session(id="test-session-123"),
        tracer.start_as_current_span("test-span") as span,
    ):
        current_context = trace.set_span_in_context(span)
        carrier: dict[str, str] = {}
        inject_context(carrier, context=current_context)

        assert set(carrier.keys()) == snapshot({"traceparent", SESSION_HEADER_NAME})
        assert carrier[SESSION_HEADER_NAME] == snapshot("test-session-123")

        extracted_session_id = extract_session_id(carrier)
        assert extracted_session_id == snapshot("test-session-123")


@pytest.mark.parametrize(
    "propagator_format",
    PROPAGATOR_FORMATS,
)
def test_extract_inject_roundtrip(
    tracer: trace.Tracer, propagator_format: PropagatorFormat
) -> None:
    """Verify extract and inject roundtrip for all propagator formats."""
    _configure_propagator(propagator_format)

    with tracer.start_as_current_span("original-span") as original_span:
        carrier: dict[str, str] = {}
        inject_context(carrier)

        extracted_context = extract_context(carrier)
        extracted_span = trace.get_current_span(extracted_context)

        original_span_context = original_span.get_span_context()
        extracted_span_context = extracted_span.get_span_context()

        assert original_span_context.trace_id == extracted_span_context.trace_id
        assert original_span_context.span_id == extracted_span_context.span_id


def test_distributed_trace_client_to_server_continuity(tracer: trace.Tracer) -> None:
    """Verify trace_id propagates from client to server in distributed system."""
    _configure_propagator("tracecontext")

    with tracer.start_as_current_span("client-span") as client_span:
        client_trace_id = client_span.get_span_context().trace_id

        carrier: dict[str, str] = {}
        inject_context(carrier)

        extracted_context = extract_context(carrier)

        with (
            propagated_context(parent=extracted_context),
            tracer.start_as_current_span("server-span") as server_span,
        ):
            server_trace_id = server_span.get_span_context().trace_id

            assert client_trace_id == server_trace_id


def test_multihop_trace_propagation(tracer: trace.Tracer) -> None:
    """Verify trace_id propagates across multiple service hops (A→B→C)."""
    _configure_propagator("tracecontext")

    with tracer.start_as_current_span("service-a-span") as service_a_span:
        service_a_trace_id = service_a_span.get_span_context().trace_id

        carrier_a_to_b: dict[str, str] = {}
        inject_context(carrier_a_to_b)

        context_b = extract_context(carrier_a_to_b)
        with (
            propagated_context(parent=context_b),
            tracer.start_as_current_span("service-b-span") as service_b_span,
        ):
            service_b_trace_id = service_b_span.get_span_context().trace_id

            carrier_b_to_c: dict[str, str] = {}
            inject_context(carrier_b_to_c)

            context_c = extract_context(carrier_b_to_c)
            with (
                propagated_context(parent=context_c),
                tracer.start_as_current_span("service-c-span") as service_c_span,
            ):
                service_c_trace_id = service_c_span.get_span_context().trace_id

                assert service_a_trace_id == service_b_trace_id
                assert service_b_trace_id == service_c_trace_id


def test_cross_format_propagation_b3_to_composite(tracer: trace.Tracer) -> None:
    """Verify trace propagates when client uses b3 and server uses composite."""
    _configure_propagator("b3")

    with tracer.start_as_current_span("client-span") as client_span:
        client_trace_id = client_span.get_span_context().trace_id

        carrier: dict[str, str] = {}
        inject_context(carrier)

        _configure_propagator("composite")

        extracted_context = extract_context(carrier)

        with (
            propagated_context(parent=extracted_context),
            tracer.start_as_current_span("server-span") as server_span,
        ):
            server_trace_id = server_span.get_span_context().trace_id

            assert client_trace_id == server_trace_id


def test_concurrent_requests_context_isolation(tracer: trace.Tracer) -> None:
    """Verify concurrent requests maintain isolated trace contexts."""
    _configure_propagator("tracecontext")

    trace_ids: list[int] = []
    lock = threading.Lock()

    def create_trace_and_propagate(index: int) -> None:
        with tracer.start_as_current_span(f"request-{index}") as span:
            trace_id = span.get_span_context().trace_id

            carrier: dict[str, str] = {}
            inject_context(carrier)

            extracted_context = extract_context(carrier)

            with (
                propagated_context(parent=extracted_context),
                tracer.start_as_current_span(f"handler-{index}") as handler_span,
            ):
                handler_trace_id = handler_span.get_span_context().trace_id

                with lock:
                    trace_ids.append(trace_id)

                assert trace_id == handler_trace_id

    threads = [
        threading.Thread(target=create_trace_and_propagate, args=(i,)) for i in range(5)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert len(trace_ids) == 5
    assert len(set(trace_ids)) == 5


def test_malformed_header_creates_new_trace(tracer: trace.Tracer) -> None:
    """Verify server creates new trace when receiving malformed traceparent."""
    _configure_propagator("tracecontext")

    carrier: dict[str, str] = {"traceparent": "invalid-traceparent-format"}

    extracted_context = extract_context(carrier)

    with (
        propagated_context(parent=extracted_context),
        tracer.start_as_current_span("new-span") as new_span,
    ):
        new_trace_id = new_span.get_span_context().trace_id

        assert new_trace_id > 0
        assert new_span.is_recording()


def test_partial_context_extraction(tracer: trace.Tracer) -> None:
    """Verify graceful handling of partially valid trace context."""
    _configure_propagator("tracecontext")

    carrier: dict[str, str] = {
        "traceparent": "00-0af7651916cd43dd8448eb211c80319c-invalid-01"
    }

    extracted_context = extract_context(carrier)

    with (
        propagated_context(parent=extracted_context),
        tracer.start_as_current_span("span-from-partial") as span,
    ):
        trace_id = span.get_span_context().trace_id

        assert trace_id > 0
        assert span.is_recording()


def test_empty_carrier_extraction(tracer: trace.Tracer) -> None:
    """Verify extraction from empty carrier creates valid context for new trace."""
    _configure_propagator("tracecontext")

    carrier: dict[str, str] = {}

    extracted_context = extract_context(carrier)

    with (
        propagated_context(parent=extracted_context),
        tracer.start_as_current_span("span-from-empty") as span,
    ):
        trace_id = span.get_span_context().trace_id

        assert trace_id > 0
        assert span.is_recording()


def test_reset_propagator_clears_singleton(tracer_provider: TracerProvider) -> None:
    """Verify reset_propagator clears the singleton and allows fresh initialization."""
    os.environ[ENV_PROPAGATOR_FORMAT] = "tracecontext"

    first_propagator = get_propagator()

    reset_propagator()
    os.environ[ENV_PROPAGATOR_FORMAT] = "b3"

    second_propagator = get_propagator()

    tracer = tracer_provider.get_tracer(__name__)

    with tracer.start_as_current_span("test-span") as span:
        current_context = trace.set_span_in_context(span)

        carrier1: dict[str, str] = {}
        carrier2: dict[str, str] = {}

        first_propagator.inject_context(carrier1, context=current_context)
        second_propagator.inject_context(carrier2, context=current_context)

        assert set(carrier1.keys()) == snapshot({"traceparent"})
        assert set(carrier2.keys()) == snapshot({"b3"})
