/**
 * @fileoverview Shared test fixtures for span-related tests.
 *
 * Provides reusable fixtures and builder functions to reduce duplication
 * across test files. Import these fixtures instead of defining inline data.
 */

import type { SpanTransformInput } from "@/clickhouse/transform";
import type {
  RealtimeSpanInput,
  RealtimeSpansUpsertRequest,
} from "@/realtimeSpans";

// =============================================================================
// Span Fixtures
// =============================================================================

/**
 * Default OTLP span fixture for testing.
 * Contains all commonly used span attributes for LLM call scenarios.
 */
export const TestSpanFixture: RealtimeSpanInput = {
  traceId: "0123456789abcdef0123456789abcdef",
  spanId: "0123456789abcdef",
  parentSpanId: null,
  name: "LLM.Call",
  kind: 1,
  startTimeUnixNano: "1704067200000000000", // 2024-01-01T00:00:00Z
  endTimeUnixNano: "1704067201000000000", // 2024-01-01T00:00:01Z
  attributes: {
    "gen_ai.request.model": "gpt-4",
    "gen_ai.system": "openai",
    "gen_ai.usage.input_tokens": 100,
    "gen_ai.usage.output_tokens": 50,
    "gen_ai.usage.cost": 0.01,
    "mirascope.function_id": "00000000-0000-0000-0000-000000000001",
    "mirascope.function_name": "summarize",
    "mirascope.function_version": "v1",
  },
  status: { code: 1, message: "OK" },
  events: [],
  links: [],
};

/**
 * Span fixture with error status for testing error scenarios.
 */
export const TestErrorSpanFixture: RealtimeSpanInput = {
  ...TestSpanFixture,
  spanId: "error-span-0001",
  status: { code: 2, message: "ERROR" },
  attributes: {
    ...TestSpanFixture.attributes,
    "exception.type": "Error",
    "exception.message": "Test error message",
  },
};

// =============================================================================
// Message Fixtures
// =============================================================================

/**
 * Default spans ingest message fixture for testing queue consumers.
 */
export const TestSpansIngestMessageFixture: RealtimeSpansUpsertRequest = {
  environmentId: "00000000-0000-0000-0000-000000000020",
  projectId: "00000000-0000-0000-0000-000000000030",
  organizationId: "00000000-0000-0000-0000-000000000040",
  receivedAt: 1704067200000, // 2024-01-01T00:00:00Z
  serviceName: "test-service",
  serviceVersion: "1.0.0",
  resourceAttributes: { "service.name": "test-service" },
  spans: [TestSpanFixture],
};

// =============================================================================
// Transform Input Fixtures
// =============================================================================

/**
 * Default transform input fixture for ClickHouse transform tests.
 */
export const TestTransformInputFixture: SpanTransformInput = {
  span: TestSpanFixture,
  environmentId: "00000000-0000-0000-0000-000000000020",
  projectId: "00000000-0000-0000-0000-000000000030",
  organizationId: "00000000-0000-0000-0000-000000000040",
  receivedAt: 1704067200123, // 2024-01-01T00:00:00.123Z
  serviceName: "test-service",
  serviceVersion: "1.0.0",
  resourceAttributes: { region: "us-east-1" },
};

// =============================================================================
// Builder Functions
// =============================================================================

/**
 * Builds a span with optional overrides.
 */
export const buildSpan = (
  overrides: Partial<RealtimeSpanInput> = {},
): RealtimeSpanInput => ({
  ...TestSpanFixture,
  ...overrides,
  attributes: {
    ...TestSpanFixture.attributes,
    ...overrides.attributes,
  },
});

/**
 * Builds an indexed span for batch testing.
 */
export const buildIndexedSpan = (index: number): RealtimeSpanInput => ({
  ...TestSpanFixture,
  spanId: `span-${index.toString().padStart(4, "0")}`,
  name: `span-${index}`,
});

/**
 * Builds a spans ingest message with optional overrides.
 */
export const buildSpansIngestMessage = (
  overrides: Partial<RealtimeSpansUpsertRequest> & {
    span?: Partial<RealtimeSpanInput>;
  } = {},
): RealtimeSpansUpsertRequest => {
  const { span: spanOverrides, ...messageOverrides } = overrides;
  return {
    ...TestSpansIngestMessageFixture,
    ...messageOverrides,
    spans: spanOverrides
      ? [buildSpan(spanOverrides)]
      : TestSpansIngestMessageFixture.spans,
  };
};

/**
 * Builds a transform input with optional overrides.
 * Supports nested span overrides via the `span` property.
 */
export const buildTransformInput = (
  overrides: Omit<Partial<SpanTransformInput>, "span"> & {
    span?: Partial<RealtimeSpanInput>;
  } = {},
): SpanTransformInput => {
  const { span: spanOverrides, ...inputOverrides } = overrides;
  return {
    ...TestTransformInputFixture,
    ...inputOverrides,
    span: spanOverrides
      ? buildSpan(spanOverrides)
      : TestTransformInputFixture.span,
  };
};
