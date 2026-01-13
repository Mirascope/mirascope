/**
 * @fileoverview Utilities for transforming spans into ClickHouse analytics rows.
 *
 * This module is shared between ingestion and realtime paths to ensure a
 * consistent mapping from OTLP spans into the `spans_analytics` schema.
 */

import type { RealtimeSpanInput } from "@/realtimeSpans";

// =============================================================================
// Types
// =============================================================================

export type SpanAnalyticsRow = {
  trace_id: string;
  span_id: string;
  parent_span_id: string | null;
  environment_id: string;
  project_id: string;
  organization_id: string;
  start_time: string;
  end_time: string | null;
  duration_ms: number | null;
  name: string;
  name_lower: string;
  kind: number | null;
  status_code: number | null;
  status_message: string | null;
  model: string | null;
  provider: string | null;
  input_tokens: number | null;
  output_tokens: number | null;
  total_tokens: number | null;
  cost_usd: number | null;
  function_id: string | null;
  function_name: string | null;
  function_version: string | null;
  error_type: string | null;
  error_message: string | null;
  attributes: string;
  events: string | null;
  links: string | null;
  service_name: string | null;
  service_version: string | null;
  resource_attributes: string | null;
  created_at: string;
  synced_at: string;
  _version: number;
};

export type SpanTransformInput = {
  span: RealtimeSpanInput;
  environmentId: string;
  projectId: string;
  organizationId: string;
  receivedAt: number;
  serviceName: string | null;
  serviceVersion: string | null;
  resourceAttributes: Record<string, unknown> | null;
};

// =============================================================================
// Helpers
// =============================================================================

/**
 * Format Date as ClickHouse DateTime64 string.
 *
 * Example (precision=9): "2024-01-01 12:34:56.123000000"
 */
const formatDateTime64 = (date: Date, precision: number): string => {
  const iso = date.toISOString(); // YYYY-MM-DDTHH:MM:SS.mmmZ
  const [datePart, timePart] = iso.split("T");
  const timeWithoutZone = timePart?.replace("Z", "") ?? "00:00:00.000";
  const [time, milliseconds = ""] = timeWithoutZone.split(".");
  const paddedFraction = milliseconds
    .padEnd(precision, "0")
    .slice(0, precision);
  return `${datePart} ${time}.${paddedFraction}`;
};

/**
 * Extract attribute value from JSONB attributes.
 */
const getAttributeValue = (
  attributes: Record<string, unknown> | null,
  key: string,
): unknown => {
  if (!attributes) return null;
  return attributes[key] ?? null;
};

// =============================================================================
// Transform
// =============================================================================

/**
 * Transform a span + trace into ClickHouse analytics format.
 */
export const transformSpanForClickHouse = ({
  span,
  environmentId,
  projectId,
  organizationId,
  receivedAt,
  serviceName,
  serviceVersion,
  resourceAttributes,
}: SpanTransformInput): SpanAnalyticsRow => {
  const attributes = span.attributes ?? null;
  const status = span.status ?? null;

  // Calculate duration in milliseconds
  // Per plan: fallback to null if end_time < start_time (negative duration)
  let durationMs: number | null = null;
  if (span.startTimeUnixNano && span.endTimeUnixNano) {
    const startNs = BigInt(span.startTimeUnixNano);
    const endNs = BigInt(span.endTimeUnixNano);
    const calculatedMs = Number((endNs - startNs) / BigInt(1000000));
    // Only set if non-negative (negative indicates data inconsistency)
    durationMs = calculatedMs >= 0 ? calculatedMs : null;
  }

  // Convert Unix nano to ISO string
  const startTime = span.startTimeUnixNano
    ? new Date(Number(BigInt(span.startTimeUnixNano) / BigInt(1000000)))
    : new Date(receivedAt);
  const endTime = span.endTimeUnixNano
    ? new Date(Number(BigInt(span.endTimeUnixNano) / BigInt(1000000)))
    : null;

  return {
    trace_id: span.traceId,
    span_id: span.spanId,
    parent_span_id: span.parentSpanId ?? null,
    environment_id: environmentId,
    project_id: projectId,
    organization_id: organizationId,
    start_time: formatDateTime64(startTime, 9),
    end_time: endTime ? formatDateTime64(endTime, 9) : null,
    duration_ms: durationMs,
    name: span.name,
    name_lower: span.name.toLowerCase(),
    kind: span.kind ?? null,
    status_code: status?.code ?? null,
    status_message: status?.message ?? null,
    // LLM-specific attributes
    model: getAttributeValue(attributes, "gen_ai.request.model") as
      | string
      | null,
    provider: getAttributeValue(attributes, "gen_ai.system") as string | null,
    input_tokens: getAttributeValue(attributes, "gen_ai.usage.input_tokens") as
      | number
      | null,
    output_tokens: getAttributeValue(
      attributes,
      "gen_ai.usage.output_tokens",
    ) as number | null,
    total_tokens: null, // Calculated if needed
    cost_usd: getAttributeValue(attributes, "gen_ai.usage.cost") as
      | number
      | null,
    function_id: getAttributeValue(attributes, "mirascope.function_id") as
      | string
      | null,
    function_name: getAttributeValue(attributes, "mirascope.function_name") as
      | string
      | null,
    function_version: getAttributeValue(
      attributes,
      "mirascope.function_version",
    ) as string | null,
    error_type: getAttributeValue(attributes, "exception.type") as
      | string
      | null,
    error_message: getAttributeValue(attributes, "exception.message") as
      | string
      | null,
    // Full JSON attributes
    attributes: JSON.stringify(attributes ?? {}),
    events: span.events ? JSON.stringify(span.events) : null,
    links: span.links ? JSON.stringify(span.links) : null,
    // Trace-level info
    service_name: serviceName,
    service_version: serviceVersion,
    resource_attributes: resourceAttributes
      ? JSON.stringify(resourceAttributes)
      : null,
    // Timestamps
    created_at: formatDateTime64(new Date(receivedAt), 3),
    synced_at: formatDateTime64(new Date(), 3),
    _version: Date.now(),
  };
};
