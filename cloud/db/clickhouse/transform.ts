/**
 * @fileoverview Utilities for transforming spans into ClickHouse analytics rows.
 *
 * This module is shared between ingestion and realtime paths to ensure a
 * consistent mapping from OTLP spans into the `spans_analytics` schema.
 */

import type { SpanInput } from "@/db/clickhouse/types";

// =============================================================================
// Types
// =============================================================================

export type SpansAnalyticsRow = {
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
  span: SpanInput;
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
export const formatDateTime64 = (date: Date, precision: number): string => {
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

/**
 * Converts a value to a finite number or returns null.
 */
const toNumberOrNull = (value: unknown): number | null => {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim().length > 0) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
};

/**
 * Computes total tokens from attributes.
 *
 * Priority:
 * 1. mirascope.response.usage.total_tokens
 * 2. gen_ai.usage.total_tokens
 * 3. Sum of input and output tokens
 */
const getTotalTokens = (
  attributes: Record<string, unknown> | null,
): number | null => {
  // Try Mirascope total first
  const mirascopeTotal = getMirascopeUsageField(attributes, "total_tokens");
  if (mirascopeTotal !== null) return mirascopeTotal;

  // Try gen_ai total
  const genAiTotal = toNumberOrNull(
    getAttributeValue(attributes, "gen_ai.usage.total_tokens"),
  );
  if (genAiTotal !== null) return genAiTotal;

  // Fall back to summing input and output (using the new helper functions)
  const input = getInputTokens(attributes);
  const output = getOutputTokens(attributes);

  if (input === null && output === null) return null;
  return (input ?? 0) + (output ?? 0);
};

/**
 * Parse mirascope.response.usage JSON and extract a field.
 */
const getMirascopeUsageField = (
  attributes: Record<string, unknown> | null,
  field: string,
): number | null => {
  if (!attributes) return null;
  const usageRaw = getAttributeValue(attributes, "mirascope.response.usage");
  if (usageRaw == null) return null;

  try {
    const parsed: unknown =
      typeof usageRaw === "string" ? JSON.parse(usageRaw) : usageRaw;
    if (parsed && typeof parsed === "object" && field in parsed) {
      return toNumberOrNull((parsed as Record<string, unknown>)[field]);
    }
  } catch {
    // Invalid JSON
  }
  return null;
};

/**
 * Extract input tokens from attributes.
 *
 * Priority:
 * 1. mirascope.response.usage.input_tokens
 * 2. gen_ai.usage.input_tokens
 */
const getInputTokens = (
  attributes: Record<string, unknown> | null,
): number | null => {
  const mirascopeTokens = getMirascopeUsageField(attributes, "input_tokens");
  if (mirascopeTokens !== null) return mirascopeTokens;
  return toNumberOrNull(
    getAttributeValue(attributes, "gen_ai.usage.input_tokens"),
  );
};

/**
 * Extract output tokens from attributes.
 *
 * Priority:
 * 1. mirascope.response.usage.output_tokens
 * 2. gen_ai.usage.output_tokens
 */
const getOutputTokens = (
  attributes: Record<string, unknown> | null,
): number | null => {
  const mirascopeTokens = getMirascopeUsageField(attributes, "output_tokens");
  if (mirascopeTokens !== null) return mirascopeTokens;
  return toNumberOrNull(
    getAttributeValue(attributes, "gen_ai.usage.output_tokens"),
  );
};

/**
 * Extract model from attributes.
 *
 * Priority:
 * 1. mirascope.response.model_id
 * 2. gen_ai.request.model
 */
const getModel = (
  attributes: Record<string, unknown> | null,
): string | null => {
  if (!attributes) return null;
  const mirascopeModel = getAttributeValue(
    attributes,
    "mirascope.response.model_id",
  );
  if (mirascopeModel != null && typeof mirascopeModel === "string") {
    return mirascopeModel;
  }
  const genAiModel = getAttributeValue(attributes, "gen_ai.request.model");
  return typeof genAiModel === "string" ? genAiModel : null;
};

/**
 * Extract provider from attributes.
 *
 * Priority:
 * 1. mirascope.response.provider_id
 * 2. gen_ai.system
 */
const getProvider = (
  attributes: Record<string, unknown> | null,
): string | null => {
  if (!attributes) return null;
  const mirascopeProvider = getAttributeValue(
    attributes,
    "mirascope.response.provider_id",
  );
  if (mirascopeProvider != null && typeof mirascopeProvider === "string") {
    return mirascopeProvider;
  }
  const genAiProvider = getAttributeValue(attributes, "gen_ai.system");
  return typeof genAiProvider === "string" ? genAiProvider : null;
};

/**
 * Extract cost in USD from attributes.
 *
 * Priority:
 * 1. mirascope.response.cost (JSON with total_cost in centicents)
 * 2. gen_ai.usage.cost (direct USD value)
 */
const getCostUsd = (
  attributes: Record<string, unknown> | null,
): number | null => {
  if (!attributes) return null;

  // Try mirascope.response.cost first (JSON string with centicents)
  const mirascpeCostRaw = getAttributeValue(
    attributes,
    "mirascope.response.cost",
  );
  if (mirascpeCostRaw != null) {
    try {
      const parsed: unknown =
        typeof mirascpeCostRaw === "string"
          ? JSON.parse(mirascpeCostRaw)
          : mirascpeCostRaw;
      if (parsed && typeof parsed === "object" && "total_cost" in parsed) {
        const totalCenticents = toNumberOrNull(
          (parsed as Record<string, unknown>).total_cost,
        );
        if (totalCenticents !== null) {
          // Convert centicents to USD (1 centicent = $0.0001)
          return totalCenticents / 10000;
        }
      }
    } catch {
      // Invalid JSON, fall through to gen_ai.usage.cost
    }
  }

  // Fallback to gen_ai.usage.cost (already in USD)
  return toNumberOrNull(getAttributeValue(attributes, "gen_ai.usage.cost"));
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
}: SpanTransformInput): SpansAnalyticsRow => {
  const attributes = span.attributes ?? null;
  const status = span.status ?? null;

  // Calculate duration in milliseconds
  // Fallback to null if end_time < start_time (negative duration)
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
    // LLM-specific attributes (prefer Mirascope, fallback to gen_ai)
    model: getModel(attributes),
    provider: getProvider(attributes),
    input_tokens: getInputTokens(attributes),
    output_tokens: getOutputTokens(attributes),
    total_tokens: getTotalTokens(attributes),
    cost_usd: getCostUsd(attributes),
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
