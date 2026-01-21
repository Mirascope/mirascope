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
  AnalyticsSummaryResponse,
  SpanDetail,
  SearchResponse,
  SpanSearchResult,
  TraceDetailResponse,
} from "@/db/clickhouse/search";

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
  inputTokens: 25,
  outputTokens: 25,
  totalTokens: 50,
  functionId: null,
  functionName: null,
  hasChildren: false,
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

/**
 * Creates a search span result for ClickHouse search tests.
 */
export const createSearchSpanResult = (
  overrides: Partial<SpanSearchResult> = {},
): SpanSearchResult => ({
  traceId: "trace-1",
  spanId: "span-1",
  name: "span",
  startTime: new Date().toISOString(),
  durationMs: 100,
  model: null,
  provider: null,
  inputTokens: null,
  outputTokens: null,
  totalTokens: null,
  functionId: null,
  functionName: null,
  hasChildren: false,
  ...overrides,
});

/**
 * Creates a trace detail span for ClickHouse trace detail tests.
 */
export const createTraceDetailSpan = (
  overrides: Partial<SpanDetail> = {},
): SpanDetail => ({
  traceId: "trace-1",
  spanId: "span-1",
  parentSpanId: null,
  environmentId: "environment-1",
  projectId: "project-1",
  organizationId: "organization-1",
  startTime: new Date().toISOString(),
  endTime: new Date().toISOString(),
  durationMs: 100,
  name: "span",
  kind: 1,
  statusCode: null,
  statusMessage: null,
  model: null,
  provider: null,
  inputTokens: null,
  outputTokens: null,
  totalTokens: null,
  costUsd: null,
  functionId: null,
  functionName: null,
  functionVersion: null,
  errorType: null,
  errorMessage: null,
  attributes: "{}",
  events: null,
  links: null,
  serviceName: null,
  serviceVersion: null,
  resourceAttributes: null,
  ...overrides,
});

/**
 * Creates a trace detail response for ClickHouse trace detail tests.
 */
export const createTraceDetailResponse = (
  overrides: Partial<TraceDetailResponse> = {},
): TraceDetailResponse => ({
  traceId: "trace-1",
  spans: [],
  rootSpanId: null,
  totalDurationMs: null,
  ...overrides,
});

/**
 * Creates an analytics summary response for ClickHouse search tests.
 */
export const createAnalyticsSummaryResponse = (
  overrides: Partial<AnalyticsSummaryResponse> = {},
): AnalyticsSummaryResponse => ({
  totalSpans: 0,
  avgDurationMs: null,
  p50DurationMs: null,
  p95DurationMs: null,
  p99DurationMs: null,
  errorRate: 0,
  totalTokens: 0,
  totalCostUsd: 0,
  topModels: [],
  topFunctions: [],
  ...overrides,
});

/**
 * ClickHouse search analytics row used in search tests.
 */
export type SearchAnalyticsRow = {
  trace_id: string;
  span_id: string;
  parent_span_id: string | null;
  environment_id: string;
  project_id: string;
  organization_id: string;
  start_time: string;
  end_time: string;
  duration_ms: number | null;
  name: string;
  kind: number;
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
  _version: number;
};

/**
 * Creates a ClickHouse search analytics row for insert tests.
 */
export const createSearchAnalyticsRow = (
  overrides: Partial<SearchAnalyticsRow> = {},
): SearchAnalyticsRow => ({
  trace_id: "trace-1",
  span_id: "span-1",
  parent_span_id: null,
  environment_id: "environment-1",
  project_id: "project-1",
  organization_id: "organization-1",
  start_time: "2024-01-15 10:00:00.000000000",
  end_time: "2024-01-15 10:00:01.000000000",
  duration_ms: 1000,
  name: "span",
  kind: 1,
  status_code: 0,
  status_message: null,
  model: null,
  provider: null,
  input_tokens: null,
  output_tokens: null,
  total_tokens: null,
  cost_usd: null,
  function_id: null,
  function_name: null,
  function_version: null,
  error_type: null,
  error_message: null,
  attributes: "{}",
  events: null,
  links: null,
  service_name: null,
  service_version: null,
  resource_attributes: null,
  created_at: "2024-01-15 10:00:00.000",
  _version: Date.now(),
  ...overrides,
});
