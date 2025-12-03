"""Exporter implementation for OpenTelemetry exporters.

This module provides the export layer for sending OpenTelemetry span
events to the Mirascope ingestion endpoint. It wraps the Fern-generated
Mirascope client to provide the interface needed by OpenTelemetry exporters.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Sequence

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.util.types import AttributeValue

from ....api._generated.traces.types import (
    TracesCreateRequestResourceSpansItem,
    TracesCreateRequestResourceSpansItemResource,
    TracesCreateRequestResourceSpansItemResourceAttributesItem,
    TracesCreateRequestResourceSpansItemResourceAttributesItemValue,
    TracesCreateRequestResourceSpansItemScopeSpansItem,
    TracesCreateRequestResourceSpansItemScopeSpansItemScope,
    TracesCreateRequestResourceSpansItemScopeSpansItemSpansItem,
    TracesCreateRequestResourceSpansItemScopeSpansItemSpansItemAttributesItem,
    TracesCreateRequestResourceSpansItemScopeSpansItemSpansItemAttributesItemValue,
    TracesCreateRequestResourceSpansItemScopeSpansItemSpansItemStatus,
)
from ....api.client import Mirascope

logger = logging.getLogger(__name__)


class MirascopeOTLPExporter(SpanExporter):
    """OTLP/HTTP exporter for completed spans.

    This exporter implements the OpenTelemetry SpanExporter interface
    for exporting completed spans in OTLP format over HTTP. It's
    designed to work with BatchSpanProcessor for efficient batching.

    This uses the Fern auto-generated client for sending converted spans.

    Attributes:
        exporter: Export client for sending events.
        timeout: Request timeout in seconds.
    """

    def __init__(
        self,
        client: Mirascope,
        timeout: float = 30.0,
        max_retry_attempts: int = 3,
    ) -> None:
        """Initialize the telemetry exporter.

        Args:
            client: The Fern-generated Mirascope client instance.
                In the future, this will accept the enhanced client from
                mirascope.api.client that provides error handling and caching
                capabilities.
            timeout: Request timeout in seconds for telemetry operations.
            max_retry_attempts: Maximum number of retry attempts for failed exports.
        """
        self.client = client
        self.timeout = timeout
        self.max_retry_attempts = max_retry_attempts
        self._shutdown = False

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Export a batch of spans to the telemetry endpoint.

        This is the standard OpenTelemetry export interface.

        Args:
            spans: Sequence of ReadableSpan objects to export.

        Returns:
            SpanExportResult indicating success or failure.
        """
        if self._shutdown:
            return SpanExportResult.FAILURE

        if not spans:
            return SpanExportResult.SUCCESS

        exceptions: list[Exception] = []
        delay = 0.1

        for i in range(self.max_retry_attempts):
            if i > 0:
                time.sleep(delay)
                delay = min(delay * 2, 5.0)

            try:
                otlp_data = self._convert_spans_to_otlp(spans)
                response = self.client.traces.create(resource_spans=otlp_data)

                if (
                    response
                    and hasattr(response, "partial_success")
                    and response.partial_success
                ):
                    partial_success = response.partial_success
                    if hasattr(partial_success, "rejected_spans"):
                        rejected = partial_success.rejected_spans
                        if rejected is not None and rejected > 0:
                            return SpanExportResult.FAILURE

                return SpanExportResult.SUCCESS

            except Exception as e:
                exceptions.append(e)
                logger.warning(
                    f"Export attempt {i + 1} failed, retrying in {delay}s: {e}"
                )

        logger.error(
            f"Failed to export spans after {self.max_retry_attempts} attempts: {exceptions}"
        )

        return SpanExportResult.FAILURE

    def _convert_spans_to_otlp(
        self, spans: Sequence[ReadableSpan]
    ) -> list[TracesCreateRequestResourceSpansItem]:
        """Convert OpenTelemetry spans to OTLP format.

        Args:
            spans: Sequence of ReadableSpan objects.

        Returns:
            List of ResourceSpans in OTLP format.
        """
        resource_spans_map = {}

        for span in spans:
            try:
                otlp_span = self._convert_span(span)
            except ValueError as e:
                logger.warning(f"Skipping span due to error: {e}")
                continue

            resource_key = id(span.resource) if span.resource else "default"

            if resource_key not in resource_spans_map:
                resource = None
                if span.resource:
                    resource_attrs = []
                    for key, value in span.resource.attributes.items():
                        attr_value = self._convert_resource_attribute_value(value)
                        resource_attrs.append(
                            TracesCreateRequestResourceSpansItemResourceAttributesItem(
                                key=key,
                                value=attr_value,
                            )
                        )
                    resource = TracesCreateRequestResourceSpansItemResource(
                        attributes=resource_attrs
                    )

                resource_spans_map[resource_key] = {
                    "resource": resource,
                    "scope_spans": {},
                }

            scope_key = (
                span.instrumentation_scope.name
                if span.instrumentation_scope
                else "unknown"
            )

            if scope_key not in resource_spans_map[resource_key]["scope_spans"]:
                scope = None
                if span.instrumentation_scope:
                    scope = TracesCreateRequestResourceSpansItemScopeSpansItemScope(
                        name=span.instrumentation_scope.name,
                        version=span.instrumentation_scope.version,
                    )

                resource_spans_map[resource_key]["scope_spans"][scope_key] = {
                    "scope": scope,
                    "spans": [],
                }

            resource_spans_map[resource_key]["scope_spans"][scope_key]["spans"].append(
                otlp_span
            )

        result = []
        for resource_data in resource_spans_map.values():
            scope_spans = []
            for scope_data in resource_data["scope_spans"].values():
                scope_spans.append(
                    TracesCreateRequestResourceSpansItemScopeSpansItem(
                        scope=scope_data["scope"],
                        spans=scope_data["spans"],
                    )
                )

            result.append(
                TracesCreateRequestResourceSpansItem(
                    resource=resource_data["resource"],
                    scope_spans=scope_spans,
                )
            )

        return result

    def _convert_span(
        self, span: ReadableSpan
    ) -> TracesCreateRequestResourceSpansItemScopeSpansItemSpansItem:
        """Convert a single ReadableSpan to OTLP format."""
        context = span.get_span_context()
        if not context or not context.is_valid:
            raise ValueError(f"Cannot export span without valid context: {span.name}")

        attributes = []
        if span.attributes:
            for key, value in span.attributes.items():
                attr_value = self._convert_attribute_value(value)
                attributes.append(
                    TracesCreateRequestResourceSpansItemScopeSpansItemSpansItemAttributesItem(
                        key=key,
                        value=attr_value,
                    )
                )

        status = None
        if span.status:
            status = TracesCreateRequestResourceSpansItemScopeSpansItemSpansItemStatus(
                code=span.status.status_code.value,
                message=span.status.description or "",
            )

        trace_id = format(context.trace_id, "032x")
        span_id = format(context.span_id, "016x")

        return TracesCreateRequestResourceSpansItemScopeSpansItemSpansItem(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=(
                format(span.parent.span_id, "016x")
                if span.parent and span.parent.span_id
                else None
            ),
            name=span.name,
            kind=span.kind.value if span.kind else 0,
            start_time_unix_nano=str(span.start_time) if span.start_time else "0",
            end_time_unix_nano=str(span.end_time) if span.end_time else "0",
            attributes=attributes or None,
            status=status,
        )

    def _convert_attribute_value(
        self, value: AttributeValue
    ) -> TracesCreateRequestResourceSpansItemScopeSpansItemSpansItemAttributesItemValue:
        """Convert OpenTelemetry AttributeValue to Mirascope API's KeyValueValue.

        This conversion is necessary because the Fern-generated API client
        expects KeyValueValue objects, not OpenTelemetry's AttributeValue types.

        Args:
            value: An OpenTelemetry AttributeValue (bool, int, float, str, or Sequence)

        Returns:
            A KeyValueValue object for the Mirascope API
        """
        match value:
            case str():
                return TracesCreateRequestResourceSpansItemScopeSpansItemSpansItemAttributesItemValue(
                    string_value=value
                )
            case bool():
                return TracesCreateRequestResourceSpansItemScopeSpansItemSpansItemAttributesItemValue(
                    bool_value=value
                )
            case int():
                return TracesCreateRequestResourceSpansItemScopeSpansItemSpansItemAttributesItemValue(
                    int_value=str(value)
                )
            case float():
                return TracesCreateRequestResourceSpansItemScopeSpansItemSpansItemAttributesItemValue(
                    double_value=value
                )
            case _:
                return TracesCreateRequestResourceSpansItemScopeSpansItemSpansItemAttributesItemValue(
                    string_value=str(list(value))
                )

    def _convert_resource_attribute_value(
        self, value: AttributeValue
    ) -> TracesCreateRequestResourceSpansItemResourceAttributesItemValue:
        """Convert OpenTelemetry AttributeValue to Mirascope API's resource KeyValueValue.

        This conversion is necessary because the Fern-generated API client
        expects KeyValueValue objects, not OpenTelemetry's AttributeValue types.

        Args:
            value: An OpenTelemetry AttributeValue (bool, int, float, str, or Sequence)

        Returns:
            A KeyValueValue object for the Mirascope API resource attributes
        """
        match value:
            case str():
                return TracesCreateRequestResourceSpansItemResourceAttributesItemValue(
                    string_value=value
                )
            case bool():
                return TracesCreateRequestResourceSpansItemResourceAttributesItemValue(
                    bool_value=value
                )
            case int():
                return TracesCreateRequestResourceSpansItemResourceAttributesItemValue(
                    int_value=str(value)
                )
            case float():
                return TracesCreateRequestResourceSpansItemResourceAttributesItemValue(
                    double_value=value
                )
            case _:
                return TracesCreateRequestResourceSpansItemResourceAttributesItemValue(
                    string_value=str(list(value))
                )

    def shutdown(self) -> None:
        """Shutdown the exporter. Subsequent exports will return FAILURE."""
        self._shutdown = True

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush any pending data.

        No-op since this exporter does not buffer data internally.

        Args:
            timeout_millis: Maximum time to wait in milliseconds (unused).

        Returns:
            Always True since there is no internal buffer to flush.
        """
        return True
