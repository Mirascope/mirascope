/**
 * @fileoverview Search API schema definitions for ClickHouse-powered search.
 *
 * Provides endpoints for searching spans in ClickHouse analytics database,
 * retrieving trace details, and getting analytics summaries.
 *
 * ## Endpoints (Traces API)
 *
 * - `POST /traces/search` - Search spans with filters and pagination
 * - `GET /traces/:traceId` - Get full trace detail with all spans
 * - `GET /traces/:traceId/spans/:spanId` - Get single span detail by trace/span ID
 * - `GET /traces/analytics` - Get analytics summary for a time range
 * - `GET /traces/analytics/timeseries` - Get time series metrics for a time range
 * - `GET /traces/analytics/functions` - Get per-function aggregates for a time range
 *
 * ## Query Constraints
 *
 * - `limit`: max 1000 (default 50)
 * - `offset`: max 10000
 * - `time_range`: max 30 days (search), max 90 days (analytics)
 * - `rootOnly`: optional root span filter for analytics endpoints
 * - `query`: max 500 characters (token-based matching, not substring)
 * - Required: startTime + endTime
 */

import { Schema } from "effect";

// =============================================================================
// Attribute Filter Schema
// =============================================================================

const AttributeFilterOperatorSchema = Schema.Literal(
  "eq",
  "neq",
  "contains",
  "exists",
);

const AttributeFilterSchema = Schema.Struct({
  key: Schema.String,
  operator: AttributeFilterOperatorSchema,
  value: Schema.optional(Schema.String),
});

// =============================================================================
// Search Request/Response Schemas
// =============================================================================

export const SearchRequestSchema = Schema.Struct({
  startTime: Schema.String,
  endTime: Schema.String,
  query: Schema.optional(Schema.String),
  inputMessagesQuery: Schema.optional(Schema.String),
  outputMessagesQuery: Schema.optional(Schema.String),
  fuzzySearch: Schema.optional(Schema.Boolean),
  traceId: Schema.optional(Schema.String),
  spanId: Schema.optional(Schema.String),
  rootOnly: Schema.optional(Schema.Boolean),
  model: Schema.optional(Schema.Array(Schema.String)),
  provider: Schema.optional(Schema.Array(Schema.String)),
  functionId: Schema.optional(Schema.String),
  functionName: Schema.optional(Schema.String),
  hasError: Schema.optional(Schema.Boolean),
  minTokens: Schema.optional(Schema.Number),
  maxTokens: Schema.optional(Schema.Number),
  minDuration: Schema.optional(Schema.Number),
  maxDuration: Schema.optional(Schema.Number),
  attributeFilters: Schema.optional(Schema.Array(AttributeFilterSchema)),
  limit: Schema.optional(Schema.Number),
  offset: Schema.optional(Schema.Number),
  sortBy: Schema.optional(
    Schema.Literal("start_time", "duration_ms", "total_tokens"),
  ),
  sortOrder: Schema.optional(Schema.Literal("asc", "desc")),
});

export type SearchRequest = typeof SearchRequestSchema.Type;

const SpanSearchResultSchema = Schema.Struct({
  traceId: Schema.String,
  spanId: Schema.String,
  name: Schema.String,
  startTime: Schema.String,
  durationMs: Schema.NullOr(Schema.Number),
  model: Schema.NullOr(Schema.String),
  provider: Schema.NullOr(Schema.String),
  totalTokens: Schema.NullOr(Schema.Number),
  functionId: Schema.NullOr(Schema.String),
  functionName: Schema.NullOr(Schema.String),
});

export type SpanSearchResult = typeof SpanSearchResultSchema.Type;

export const SearchResponseSchema = Schema.Struct({
  spans: Schema.Array(SpanSearchResultSchema),
  total: Schema.Number,
  hasMore: Schema.Boolean,
});

export type SearchResponse = typeof SearchResponseSchema.Type;

// =============================================================================
// Trace Detail Schemas
// =============================================================================

export const SpanDetailSchema = Schema.Struct({
  traceId: Schema.String,
  spanId: Schema.String,
  parentSpanId: Schema.NullOr(Schema.String),
  environmentId: Schema.String,
  projectId: Schema.String,
  organizationId: Schema.String,
  startTime: Schema.String,
  endTime: Schema.String,
  durationMs: Schema.NullOr(Schema.Number),
  name: Schema.String,
  kind: Schema.Number,
  statusCode: Schema.NullOr(Schema.Number),
  statusMessage: Schema.NullOr(Schema.String),
  model: Schema.NullOr(Schema.String),
  provider: Schema.NullOr(Schema.String),
  inputTokens: Schema.NullOr(Schema.Number),
  outputTokens: Schema.NullOr(Schema.Number),
  totalTokens: Schema.NullOr(Schema.Number),
  costUsd: Schema.NullOr(Schema.Number),
  functionId: Schema.NullOr(Schema.String),
  functionName: Schema.NullOr(Schema.String),
  functionVersion: Schema.NullOr(Schema.String),
  errorType: Schema.NullOr(Schema.String),
  errorMessage: Schema.NullOr(Schema.String),
  attributes: Schema.String,
  events: Schema.NullOr(Schema.String),
  links: Schema.NullOr(Schema.String),
  serviceName: Schema.NullOr(Schema.String),
  serviceVersion: Schema.NullOr(Schema.String),
  resourceAttributes: Schema.NullOr(Schema.String),
});

export type SpanDetail = typeof SpanDetailSchema.Type;

export const TraceDetailResponseSchema = Schema.Struct({
  traceId: Schema.String,
  spans: Schema.Array(SpanDetailSchema),
  rootSpanId: Schema.NullOr(Schema.String),
  totalDurationMs: Schema.NullOr(Schema.Number),
});

export type TraceDetailResponse = typeof TraceDetailResponseSchema.Type;

export const SpanDetailRequestSchema = Schema.Struct({
  traceId: Schema.String,
  spanId: Schema.String,
});

export type SpanDetailRequest = typeof SpanDetailRequestSchema.Type;

// =============================================================================
// Analytics Summary Schemas
// =============================================================================

export const AnalyticsSummaryRequestSchema = Schema.Struct({
  startTime: Schema.String,
  endTime: Schema.String,
  functionId: Schema.optional(Schema.String),
  rootOnly: Schema.optional(Schema.BooleanFromString),
});

export type AnalyticsSummaryRequest = typeof AnalyticsSummaryRequestSchema.Type;

const TopModelSchema = Schema.Struct({
  model: Schema.String,
  count: Schema.Number,
});

const TopFunctionSchema = Schema.Struct({
  functionName: Schema.String,
  count: Schema.Number,
});

export const AnalyticsSummaryResponseSchema = Schema.Struct({
  totalSpans: Schema.Number,
  avgDurationMs: Schema.NullOr(Schema.Number),
  p50DurationMs: Schema.NullOr(Schema.Number),
  p95DurationMs: Schema.NullOr(Schema.Number),
  p99DurationMs: Schema.NullOr(Schema.Number),
  errorRate: Schema.Number,
  totalTokens: Schema.Number,
  totalCostUsd: Schema.Number,
  topModels: Schema.Array(TopModelSchema),
  topFunctions: Schema.Array(TopFunctionSchema),
});

export type AnalyticsSummaryResponse =
  typeof AnalyticsSummaryResponseSchema.Type;

// =============================================================================
// Analytics Time Series Schemas
// =============================================================================

export const TimeFrameSchema = Schema.Literal(
  "day",
  "week",
  "month",
  "lifetime",
);

export type TimeFrame = typeof TimeFrameSchema.Type;

export const TimeSeriesRequestSchema = Schema.Struct({
  startTime: Schema.String,
  endTime: Schema.String,
  timeFrame: TimeFrameSchema,
  functionId: Schema.optional(Schema.String),
  rootOnly: Schema.optional(Schema.BooleanFromString),
});

export type TimeSeriesRequest = typeof TimeSeriesRequestSchema.Type;

const TimeSeriesPointSchema = Schema.Struct({
  startTime: Schema.String,
  endTime: Schema.String,
  totalCostUsd: Schema.Number,
  totalInputTokens: Schema.Number,
  totalOutputTokens: Schema.Number,
  totalTokens: Schema.Number,
  averageDurationMs: Schema.NullOr(Schema.Number),
  spanCount: Schema.Number,
});

export const TimeSeriesResponseSchema = Schema.Struct({
  points: Schema.Array(TimeSeriesPointSchema),
  timeFrame: TimeFrameSchema,
});

export type TimeSeriesResponse = typeof TimeSeriesResponseSchema.Type;

// =============================================================================
// Function Aggregates Schemas
// =============================================================================

export const FunctionAggregatesRequestSchema = Schema.Struct({
  startTime: Schema.String,
  endTime: Schema.String,
  rootOnly: Schema.optional(Schema.BooleanFromString),
});

export type FunctionAggregatesRequest =
  typeof FunctionAggregatesRequestSchema.Type;

const FunctionAggregateSchema = Schema.Struct({
  functionId: Schema.String,
  functionName: Schema.String,
  totalCostUsd: Schema.Number,
  totalInputTokens: Schema.Number,
  totalOutputTokens: Schema.Number,
  totalTokens: Schema.Number,
  averageDurationMs: Schema.NullOr(Schema.Number),
  spanCount: Schema.Number,
});

export const FunctionAggregatesResponseSchema = Schema.Struct({
  functions: Schema.Array(FunctionAggregateSchema),
  total: Schema.Number,
});

export type FunctionAggregatesResponse =
  typeof FunctionAggregatesResponseSchema.Type;
