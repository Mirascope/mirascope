/**
 * @fileoverview Shared test fixtures for span-related tests.
 *
 * Provides reusable fixtures and builder functions to reduce duplication
 * across test files. Import these fixtures instead of defining inline data.
 */

import { Effect } from "effect";
import type { SpanTransformInput } from "@/db/clickhouse/transform";
import type {
  CompletedSpanInput,
  CompletedSpansBatchRequest,
} from "@/db/clickhouse/types";
import type {
  SearchResponse,
  TraceDetailResponse,
} from "@/api/traces-search.schemas";

// =============================================================================
// Span Fixtures
// =============================================================================

/**
 * Default OTLP span fixture for testing.
 * Contains all commonly used span attributes for LLM call scenarios.
 */
export const TestSpanFixture: CompletedSpanInput = {
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
export const TestErrorSpanFixture: CompletedSpanInput = {
  ...TestSpanFixture,
  spanId: "error-span-0001",
  status: { code: 2, message: "ERROR" },
  attributes: {
    ...TestSpanFixture.attributes,
    "exception.type": "Error",
    "exception.message": "Test error message",
  },
};

/**
 * Span fixture for ClickHouse transform testing.
 * Contains error attributes needed by transform.test.ts.
 */
const TestTransformSpanFixtureData: CompletedSpanInput = {
  traceId: "otel-trace-1",
  spanId: "otel-span-1",
  parentSpanId: null,
  name: "LLM.Call",
  kind: 1,
  startTimeUnixNano: "1700000000000000000",
  endTimeUnixNano: "1700000001000000000",
  attributes: {
    "gen_ai.request.model": "gpt-4",
    "gen_ai.system": "openai",
    "gen_ai.usage.input_tokens": 12,
    "gen_ai.usage.output_tokens": 34,
    "gen_ai.usage.cost": 0.01,
    "mirascope.function_id": "function-1",
    "mirascope.function_name": "summarize",
    "mirascope.function_version": "v1",
    "exception.type": "Error",
    "exception.message": "boom",
  },
  status: { code: 2, message: "ERROR" },
  events: [{ name: "event" }],
  links: [{ traceId: "link-trace" }],
};

// =============================================================================
// Message Fixtures
// =============================================================================

/**
 * Default spans ingest message fixture for testing queue consumers.
 */
export const TestSpansIngestMessageFixture: CompletedSpansBatchRequest = {
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

/** Default transform input fixture data (internal). */
const TestTransformInputFixtureData: SpanTransformInput = {
  span: TestTransformSpanFixtureData,
  environmentId: "00000000-0000-0000-0000-000000000020",
  projectId: "00000000-0000-0000-0000-000000000030",
  organizationId: "00000000-0000-0000-0000-000000000040",
  receivedAt: new Date("2024-01-01T00:00:00.123Z").getTime(),
  serviceName: "svc",
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
  overrides: Partial<CompletedSpanInput> = {},
): CompletedSpanInput => ({
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
export const buildIndexedSpan = (index: number): CompletedSpanInput => ({
  ...TestSpanFixture,
  spanId: `span-${index.toString().padStart(4, "0")}`,
  name: `span-${index}`,
});

/**
 * Builds a spans ingest message with optional overrides.
 */
export const buildSpansIngestMessage = (
  overrides: Partial<CompletedSpansBatchRequest> & {
    span?: Partial<CompletedSpanInput>;
  } = {},
): CompletedSpansBatchRequest => {
  const { span: spanOverrides, ...messageOverrides } = overrides;
  return {
    ...TestSpansIngestMessageFixture,
    ...messageOverrides,
    spans: spanOverrides
      ? [buildSpan(spanOverrides)]
      : TestSpansIngestMessageFixture.spans,
  };
};

// =============================================================================
// Effect-native Fixtures
// =============================================================================

type SpanOverrides = Partial<SpanTransformInput["span"]>;
type InputOverrides = Omit<Partial<SpanTransformInput>, "span"> & {
  span?: SpanOverrides;
};

/**
 * Effect-native test fixture for transform span.
 *
 * Use `yield* TestTransformSpanFixture()` or `yield* TestTransformSpanFixture({ ...overrides })`.
 */
export const TestTransformSpanFixture = (
  overrides: SpanOverrides = {},
): Effect.Effect<SpanTransformInput["span"]> =>
  Effect.succeed({ ...TestTransformSpanFixtureData, ...overrides });

/**
 * Effect-native test fixture for transform input.
 *
 * Use `yield* TestTransformInputFixture()` or `yield* TestTransformInputFixture({ ...overrides })`.
 */
export const TestTransformInputFixture = (
  overrides: InputOverrides = {},
): Effect.Effect<SpanTransformInput> => {
  const { span: spanOverrides, ...inputOverrides } = overrides;
  return Effect.succeed({
    ...TestTransformInputFixtureData,
    ...inputOverrides,
    span: { ...TestTransformSpanFixtureData, ...spanOverrides },
  });
};

// =============================================================================
// Search Test Fixtures
// =============================================================================

/**
 * Builds a search span result with optional overrides.
 */
export const buildSearchSpan = (
  overrides: Partial<SearchResponse["spans"][number]> = {},
): SearchResponse["spans"][number] => ({
  traceId: "trace-1",
  spanId: "span-1",
  name: "test-span",
  startTime: new Date().toISOString(),
  durationMs: 100,
  model: "gpt-4",
  provider: "openai",
  totalTokens: 50,
  functionId: null,
  functionName: null,
  ...overrides,
});

/**
 * Builds a trace detail span with optional overrides.
 */
export const buildTraceDetailSpan = (
  overrides: Partial<TraceDetailResponse["spans"][number]> = {},
): TraceDetailResponse["spans"][number] => ({
  traceId: "trace-1",
  spanId: "span-1",
  parentSpanId: null,
  environmentId: "env-1",
  projectId: "proj-1",
  organizationId: "org-1",
  startTime: new Date().toISOString(),
  endTime: new Date(Date.now() + 100).toISOString(),
  durationMs: 100,
  name: "test-span",
  kind: 1,
  statusCode: 0,
  statusMessage: null,
  model: "gpt-4",
  provider: "openai",
  inputTokens: 25,
  outputTokens: 25,
  totalTokens: 50,
  costUsd: 0.01,
  functionId: null,
  functionName: null,
  functionVersion: null,
  errorType: null,
  errorMessage: null,
  attributes: "{}",
  events: null,
  links: null,
  serviceName: "test-service",
  serviceVersion: "1.0.0",
  resourceAttributes: null,
  ...overrides,
});

/**
 * Creates a time window for search tests (past 24 hours to now).
 */
export const createSearchTimeWindow = () => ({
  startTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
  endTime: new Date().toISOString(),
});
