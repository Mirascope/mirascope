/**
 * @fileoverview Search API handlers for ClickHouse-powered search.
 *
 * Provides handlers for searching spans, retrieving trace details,
 * and getting analytics summaries from ClickHouse.
 *
 * ## Authentication
 *
 * All endpoints require API key authentication. The environment ID
 * is extracted from the API key scope.
 *
 * @example
 * ```ts
 * // Handler usage (internal)
 * const result = yield* searchHandler({ startTime: "...", endTime: "..." });
 * ```
 */

import { Effect, Option } from "effect";
import { Authentication } from "@/auth";
import {
  ClickHouseSearch,
  type SpanSearchInput,
  type TraceDetailInput,
  type AnalyticsSummaryInput,
  type TimeSeriesInput,
  type FunctionAggregatesInput,
  type AttributeFilter,
  type SearchResponse,
  type TraceDetailResponse,
} from "@/db/clickhouse/search";
import { RealtimeSpans } from "@/workers/realtimeSpans";
import type {
  SearchRequest,
  AnalyticsSummaryRequest,
  TimeSeriesRequest,
  FunctionAggregatesRequest,
} from "@/api/traces-search.schemas";

export * from "@/api/traces-search.schemas";

// =============================================================================
// Handlers
// =============================================================================

/**
 * Search spans with filters and pagination.
 *
 * Requires API key authentication. Uses the environment ID from the API key scope.
 */
export const searchHandler = (payload: SearchRequest) =>
  Effect.gen(function* () {
    const { apiKeyInfo } = yield* Authentication.ApiKey;
    const searchService = yield* ClickHouseSearch;
    const realtimeOption = yield* Effect.serviceOption(RealtimeSpans);

    // Convert readonly arrays to mutable arrays
    const model =
      payload.model && payload.model.length > 0
        ? [...payload.model]
        : undefined;
    const provider =
      payload.provider && payload.provider.length > 0
        ? [...payload.provider]
        : undefined;
    const attributeFilters: AttributeFilter[] | undefined =
      payload.attributeFilters
        ? payload.attributeFilters.map((f) => ({
            key: f.key,
            operator: f.operator,
            value: f.value,
          }))
        : undefined;

    const input: SpanSearchInput = {
      environmentId: apiKeyInfo.environmentId,
      startTime: new Date(payload.startTime),
      endTime: new Date(payload.endTime),
      query: payload.query,
      inputMessagesQuery: payload.inputMessagesQuery,
      outputMessagesQuery: payload.outputMessagesQuery,
      fuzzySearch: payload.fuzzySearch,
      traceId: payload.traceId,
      spanId: payload.spanId,
      rootOnly: payload.rootOnly,
      model,
      provider,
      functionId: payload.functionId,
      functionName: payload.functionName,
      hasError: payload.hasError,
      minTokens: payload.minTokens,
      maxTokens: payload.maxTokens,
      minDuration: payload.minDuration,
      maxDuration: payload.maxDuration,
      attributeFilters,
      limit: payload.limit,
      offset: payload.offset,
      sortBy: payload.sortBy,
      sortOrder: payload.sortOrder,
    };

    // Skip realtime merge for paginated requests (offset > 0) to ensure
    // consistent pagination across pages
    const skipRealtime = (input.offset ?? 0) > 0;

    const realtimeResult = yield* Option.match(realtimeOption, {
      onNone: () => Effect.succeed<SearchResponse | null>(null),
      onSome: (realtime) => {
        if (skipRealtime) {
          return Effect.succeed<SearchResponse | null>(null);
        }
        if (!shouldQueryRealtime(input.startTime, input.endTime)) {
          return Effect.succeed<SearchResponse | null>(null);
        }
        const realtimeInput: SpanSearchInput = {
          ...input,
          limit: undefined,
          offset: undefined,
        };
        return realtime
          .search(realtimeInput)
          .pipe(Effect.catchAll(() => Effect.succeed(null)));
      },
    });

    const clickhouseResult = yield* searchService.search(input);

    if (!realtimeResult) {
      return clickhouseResult;
    }

    return mergeSearchResults(clickhouseResult, realtimeResult, input);
  });

/**
 * Get full trace detail with all spans.
 *
 * Requires API key authentication. Uses the environment ID from the API key scope.
 */
export const getTraceDetailHandler = (traceId: string) =>
  Effect.gen(function* () {
    const { apiKeyInfo } = yield* Authentication.ApiKey;
    const searchService = yield* ClickHouseSearch;
    const realtimeOption = yield* Effect.serviceOption(RealtimeSpans);

    const input: TraceDetailInput = {
      environmentId: apiKeyInfo.environmentId,
      traceId,
    };

    const realtimeResult = yield* Option.match(realtimeOption, {
      onNone: () => Effect.succeed<TraceDetailResponse | null>(null),
      onSome: (realtime) =>
        realtime
          .getTraceDetail(input)
          .pipe(Effect.catchAll(() => Effect.succeed(null))),
    });

    const clickhouseResult = yield* searchService.getTraceDetail(input);

    if (!realtimeResult) {
      return clickhouseResult;
    }

    return mergeTraceDetails(clickhouseResult, realtimeResult, input.traceId);
  });

/**
 * Get analytics summary for a time range.
 *
 * Requires API key authentication. Uses the environment ID from the API key scope.
 */
export const getAnalyticsSummaryHandler = (params: AnalyticsSummaryRequest) =>
  Effect.gen(function* () {
    const { apiKeyInfo } = yield* Authentication.ApiKey;
    const searchService = yield* ClickHouseSearch;

    const input: AnalyticsSummaryInput = {
      environmentId: apiKeyInfo.environmentId,
      startTime: new Date(params.startTime),
      endTime: new Date(params.endTime),
      functionId: params.functionId,
      rootOnly: params.rootOnly,
    };

    return yield* searchService.getAnalyticsSummary(input);
  });

/**
 * Get time series metrics for a time range.
 *
 * Requires API key authentication. Uses the environment ID from the API key scope.
 */
export const getTimeSeriesMetricsHandler = (params: TimeSeriesRequest) =>
  Effect.gen(function* () {
    const { apiKeyInfo } = yield* Authentication.ApiKey;
    const searchService = yield* ClickHouseSearch;

    const input: TimeSeriesInput = {
      environmentId: apiKeyInfo.environmentId,
      startTime: new Date(params.startTime),
      endTime: new Date(params.endTime),
      timeFrame: params.timeFrame,
      functionId: params.functionId,
      rootOnly: params.rootOnly,
    };

    return yield* searchService.getTimeSeriesMetrics(input);
  });

/**
 * Get per-function aggregates for a time range.
 *
 * Requires API key authentication. Uses the environment ID from the API key scope.
 */
export const getFunctionAggregatesHandler = (
  params: FunctionAggregatesRequest,
) =>
  Effect.gen(function* () {
    const { apiKeyInfo } = yield* Authentication.ApiKey;
    const searchService = yield* ClickHouseSearch;

    const input: FunctionAggregatesInput = {
      environmentId: apiKeyInfo.environmentId,
      startTime: new Date(params.startTime),
      endTime: new Date(params.endTime),
      rootOnly: params.rootOnly,
    };

    return yield* searchService.getFunctionAggregates(input);
  });

// =============================================================================
// Realtime merge helpers
// =============================================================================

/**
 * Time-to-live window for realtime span cache (10 minutes in milliseconds).
 * Spans older than this are assumed to have been flushed to ClickHouse.
 */
const REALTIME_TTL_MS = 10 * 60 * 1000;

/** Default pagination limit when not specified by the caller. */
const DEFAULT_LIMIT = 50;

/**
 * Determines whether the query time range overlaps with the realtime cache window.
 *
 * Returns true if any part of the [startTime, endTime] range overlaps with
 * [now - TTL, now], meaning there may be recent spans not yet in ClickHouse.
 */
const shouldQueryRealtime = (startTime: Date, endTime: Date): boolean => {
  const now = Date.now();
  const windowStart = now - REALTIME_TTL_MS;
  const windowEnd = now;
  return startTime.getTime() <= windowEnd && endTime.getTime() >= windowStart;
};

/** Creates a unique key for deduplication from trace and span identifiers. */
const makeSpanKey = (traceId: string, spanId: string): string =>
  `${traceId}:${spanId}`;

/**
 * Sorts merged search results by the specified field with null handling.
 *
 * Null values are placed at the end for ascending order and at the beginning
 * for descending order to keep meaningful values prominent.
 */
const sortSearchResults = (
  spans: SearchResponse["spans"],
  sortBy: "start_time" | "duration_ms" | "total_tokens",
  sortOrder: "asc" | "desc",
): SearchResponse["spans"] => {
  const multiplier = sortOrder === "asc" ? 1 : -1;
  const toSortableValue = (span: SearchResponse["spans"][number]): number => {
    switch (sortBy) {
      case "duration_ms":
        return (
          span.durationMs ??
          (sortOrder === "asc"
            ? Number.POSITIVE_INFINITY
            : Number.NEGATIVE_INFINITY)
        );
      case "total_tokens":
        return (
          span.totalTokens ??
          (sortOrder === "asc"
            ? Number.POSITIVE_INFINITY
            : Number.NEGATIVE_INFINITY)
        );
      case "start_time":
      default: {
        const value = Date.parse(span.startTime);
        return Number.isFinite(value)
          ? value
          : sortOrder === "asc"
            ? Number.POSITIVE_INFINITY
            : Number.NEGATIVE_INFINITY;
      }
    }
  };

  return [...spans].sort((a, b) => {
    const aValue = toSortableValue(a);
    const bValue = toSortableValue(b);
    if (aValue === bValue) return 0;
    return aValue > bValue ? multiplier : -multiplier;
  });
};

/**
 * Merges search results from ClickHouse and realtime sources with deduplication.
 *
 * ClickHouse results take precedence for duplicate spans (same traceId+spanId).
 * Results are sorted and paginated according to the input parameters.
 * Total count is adjusted to include new realtime spans not in ClickHouse.
 */
const mergeSearchResults = (
  clickhouse: SearchResponse,
  realtime: SearchResponse,
  input: SpanSearchInput,
): SearchResponse => {
  const spanMap = new Map<string, SearchResponse["spans"][number]>();
  let realtimeNew = 0;

  for (const span of clickhouse.spans) {
    const key = makeSpanKey(span.traceId, span.spanId);
    spanMap.set(key, span);
  }
  for (const span of realtime.spans) {
    const key = makeSpanKey(span.traceId, span.spanId);
    if (!spanMap.has(key)) {
      realtimeNew += 1;
      spanMap.set(key, span);
    }
  }

  const merged = Array.from(spanMap.values());
  const sorted = sortSearchResults(
    merged,
    input.sortBy ?? "start_time",
    input.sortOrder ?? "desc",
  );

  const limit = input.limit ?? DEFAULT_LIMIT;
  const offset = input.offset ?? 0;
  const spans = sorted.slice(offset, offset + limit);
  const totalBase = clickhouse.hasMore
    ? clickhouse.total
    : clickhouse.total + realtimeNew;
  const total = Math.max(sorted.length, totalBase);

  return {
    spans,
    total,
    hasMore: offset + spans.length < total || clickhouse.hasMore,
  };
};

/**
 * Computes trace-level statistics from a list of spans.
 *
 * Identifies the root span (parentSpanId === null) and calculates total
 * duration from the earliest start time to the latest end time.
 * Returns null values if spans are empty or have invalid timestamps.
 */
const computeTraceStats = (
  spans: TraceDetailResponse["spans"],
): { rootSpanId: string | null; totalDurationMs: number | null } => {
  if (spans.length === 0) {
    return { rootSpanId: null, totalDurationMs: null };
  }

  const rootSpan = spans.find((span) => span.parentSpanId === null);
  const rootSpanId = rootSpan?.spanId ?? null;

  let minStart: number | null = null;
  let maxEnd: number | null = null;

  for (const span of spans) {
    const start = Date.parse(span.startTime);
    const end = Date.parse(span.endTime);
    if (!Number.isFinite(start) || !Number.isFinite(end)) continue;
    if (minStart === null || start < minStart) minStart = start;
    if (maxEnd === null || end > maxEnd) maxEnd = end;
  }

  const totalDurationMs =
    minStart !== null && maxEnd !== null ? maxEnd - minStart : null;

  return { rootSpanId, totalDurationMs };
};

/**
 * Merges trace detail responses from ClickHouse and realtime sources.
 *
 * ClickHouse spans take precedence for duplicates (same traceId+spanId).
 * Merged spans are sorted by start time and trace stats are recomputed.
 */
const mergeTraceDetails = (
  clickhouse: TraceDetailResponse,
  realtime: TraceDetailResponse,
  traceId: string,
): TraceDetailResponse => {
  const spanMap = new Map<string, TraceDetailResponse["spans"][number]>();

  for (const span of clickhouse.spans) {
    spanMap.set(makeSpanKey(span.traceId, span.spanId), span);
  }
  for (const span of realtime.spans) {
    const key = makeSpanKey(span.traceId, span.spanId);
    if (!spanMap.has(key)) {
      spanMap.set(key, span);
    }
  }

  const spans = Array.from(spanMap.values()).sort((a, b) => {
    const aTime = Date.parse(a.startTime);
    const bTime = Date.parse(b.startTime);
    /* v8 ignore start -- defensive fallback for invalid date strings */
    if (!Number.isFinite(aTime)) return 1;
    if (!Number.isFinite(bTime)) return -1;
    /* v8 ignore stop */
    return aTime - bTime;
  });
  const { rootSpanId, totalDurationMs } = computeTraceStats(spans);

  return {
    traceId,
    spans,
    rootSpanId,
    totalDurationMs,
  };
};
