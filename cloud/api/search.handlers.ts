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

import { Effect } from "effect";
import { Authentication } from "@/auth";
import {
  ClickHouseSearch,
  type SpanSearchInput,
  type TraceDetailInput,
  type AnalyticsSummaryInput,
  type AttributeFilter,
} from "@/db/clickhouse/search";
import type {
  SearchRequest,
  AnalyticsSummaryRequest,
} from "@/api/search.schemas";

export * from "@/api/search.schemas";

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

    return yield* searchService.search(input);
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

    const input: TraceDetailInput = {
      environmentId: apiKeyInfo.environmentId,
      traceId,
    };

    return yield* searchService.getTraceDetail(input);
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
    };

    return yield* searchService.getAnalyticsSummary(input);
  });
