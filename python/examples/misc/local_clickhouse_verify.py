"""E2E verification of ClickHouse sync via Search API.

Complete end-to-end test:
1. Send spans via OTLP exporter (same as local_versioning_example.py)
2. Wait for ClickHouse sync (polling Search API)
3. Verify data via Search API endpoints

Prerequisites:
1. Start Docker: `cd cloud && docker compose -f docker/compose.yml up -d`
2. Start cloud server: `cd cloud && bun run dev`

Usage:
    MIRASCOPE_API_KEY=mk_xxx uv run python examples/misc/local_clickhouse_verify.py
"""

from __future__ import annotations

import os
import time
from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from typing import Any

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from mirascope import ops
from mirascope.api._generated.traces import TracesSearchResponse
from mirascope.api.client import Mirascope, create_export_client
from mirascope.ops._internal.exporters import MirascopeOTLPExporter

BASE_URL = os.getenv("MIRASCOPE_BASE_URL", "http://localhost:3000/api/v2")
API_KEY = os.getenv("MIRASCOPE_API_KEY")


def send_spans(provider: TracerProvider) -> tuple[str, set[str]]:
    """Send test spans via OTLP exporter. Returns span name for verification."""

    @ops.trace
    def e2e_clickhouse_test(message: str) -> str:
        """E2E test trace for ClickHouse verification."""
        return f"processed: {message}"

    @ops.trace
    def e2e_nested_operation(data: str) -> str:
        """Nested operation to create multi-span trace."""
        return f"nested: {data}"

    # Create a trace with nested spans
    trace = e2e_clickhouse_test.wrapped("ClickHouse E2E test message")
    print(f"    Trace result: {trace.result}")

    nested = e2e_nested_operation.wrapped("nested data")
    print(f"    Nested result: {nested.result}")

    provider.force_flush()
    print("    Spans flushed!")

    return "e2e_clickhouse_test", {"e2e_clickhouse_test", "e2e_nested_operation"}


def wait_for_sync(
    client: Mirascope, span_name: str, timeout_sec: int = 30
) -> TracesSearchResponse | None:
    """Poll Search API until spans appear or timeout."""
    now = datetime.now(timezone.utc)
    start_time = (now - timedelta(minutes=5)).isoformat()
    end_time = (now + timedelta(minutes=5)).isoformat()

    for i in range(timeout_sec):
        result = client.traces.search(
            start_time=start_time,
            end_time=end_time,
            query=span_name,
            limit=10,
            sort_by="start_time",
            sort_order="desc",
        )
        if result.total and result.total > 0:
            return result
        print(f"    Waiting for sync... ({i + 1}/{timeout_sec}s)")
        time.sleep(1)
    return None


def normalize_datetime(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def assert_span_fields(span: Any, require_end_time: bool) -> None:
    assert span.name, "span.name is required"
    assert span.trace_id, "span.trace_id is required"
    assert span.span_id, "span.span_id is required"
    assert span.start_time, "span.start_time is required"
    if require_end_time:
        assert span.end_time, "span.end_time is required"
    assert span.duration_ms is not None, "span.duration_ms is required"
    assert span.duration_ms >= 0, "span.duration_ms must be non-negative"
    start_time = normalize_datetime(span.start_time)
    if require_end_time:
        end_time = normalize_datetime(span.end_time)
        assert end_time >= start_time, "span.end_time must be >= span.start_time"


def assert_recent_span(span: Any, now: datetime, window_minutes: int = 10) -> None:
    start_time = normalize_datetime(span.start_time)
    delta = abs((now - start_time).total_seconds())
    assert delta <= window_minutes * 60, (
        f"span.start_time too old/new: {span.start_time}"
    )


def assert_trace_contains_names(spans: Iterable[Any], expected: set[str]) -> None:
    names = {span.name for span in spans if span.name}
    missing = expected - names
    assert not missing, f"missing expected span names: {sorted(missing)}"


def verify_search_api(
    client: Mirascope,
    search_result: TracesSearchResponse,
    expected_names: set[str],
    span_name: str,
) -> bool:
    """Verify Search API endpoints with the synced data."""
    spans = search_result.spans or []
    total = search_result.total or 0
    print(f"    Found {total} spans (showing {len(spans)})")

    for span in spans[:3]:
        assert_span_fields(span, require_end_time=False)
        dur = span.duration_ms
        dur_str = f"{dur}ms" if dur is not None else "NULL"
        model = span.model or "N/A"
        name = span.name[:30] if span.name else "N/A"
        print(f"      - {name:<30} | {model:<15} | {dur_str}")

    if not spans:
        return False

    trace_id = spans[0].trace_id
    trace_result = client.traces.gettracedetail(trace_id)

    if not trace_result:
        print("    Failed to get trace detail")
        return False

    trace_spans = trace_result.spans or []
    print(f"    Trace {trace_id[:16]}... has {len(trace_spans)} spans")
    assert trace_spans, "trace detail has no spans"
    for span in trace_spans:
        assert_span_fields(span, require_end_time=True)
    assert_trace_contains_names(trace_spans, {span_name})
    now = datetime.now(timezone.utc)
    for span in trace_spans:
        assert_recent_span(span, now)

    start_time = (now - timedelta(minutes=10)).isoformat()
    end_time = (now + timedelta(minutes=5)).isoformat()

    analytics_result = client.traces.getanalyticssummary(
        start_time=start_time,
        end_time=end_time,
    )

    if not analytics_result:
        print("    Failed to get analytics")
        return False

    print(
        f"    Analytics: {analytics_result.total_spans or 0} spans, "
        f"avg {analytics_result.avg_duration_ms}ms"
    )
    assert analytics_result.total_spans is not None, "analytics.total_spans missing"
    assert analytics_result.total_spans >= len(trace_spans), (
        "analytics.total_spans is less than trace spans"
    )
    assert analytics_result.avg_duration_ms is not None, (
        "analytics.avg_duration_ms missing"
    )
    assert analytics_result.avg_duration_ms >= 0, (
        "analytics.avg_duration_ms must be non-negative"
    )

    return True


def main():
    if not API_KEY:
        print("ERROR: MIRASCOPE_API_KEY environment variable is required")
        print("Create an API key in the Mirascope Cloud UI: http://localhost:3000")
        exit(1)

    print("=" * 70)
    print("ClickHouse E2E Verification")
    print("=" * 70)
    print(f"API Base URL: {BASE_URL}")
    print(f"API Key: {API_KEY[:15]}...")

    # Create Mirascope client for Search API
    api_client = Mirascope(base_url=BASE_URL, api_key=API_KEY)

    # 1. Setup OTLP exporter
    print("\n[1/4] Setting up OTLP exporter...")
    export_client = create_export_client(base_url=BASE_URL, api_key=API_KEY)
    provider = TracerProvider()
    exporter = MirascopeOTLPExporter(client=export_client)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    ops.configure(tracer_provider=provider)
    ops.instrument_llm()
    print("    OTLP exporter configured")

    # 2. Send spans
    print("\n[2/4] Sending test spans...")
    span_name, expected_names = send_spans(provider)

    # 3. Wait for ClickHouse sync
    print("\n[3/4] Waiting for ClickHouse sync...")
    search_result = wait_for_sync(api_client, span_name)

    if not search_result:
        print("    TIMEOUT: Spans not found in ClickHouse")
        print("    Make sure clickhouseSyncLocal worker is running:")
        print("      cd cloud && bun run tsx workers/clickhouseSyncLocal.ts")
        provider.shutdown()
        exit(1)

    print("    Sync complete!")

    # 4. Verify Search API
    print("\n[4/4] Verifying Search API...")
    success = verify_search_api(api_client, search_result, expected_names, span_name)

    provider.shutdown()

    print("\n" + "=" * 70)
    if success:
        print("E2E Verification PASSED!")
    else:
        print("E2E Verification FAILED!")
        exit(1)
    print("=" * 70)


if __name__ == "__main__":
    main()
