/**
 * @fileoverview Effect-native ClickHouse search service for spans analytics.
 *
 * Provides read-only search and analytics operations against ClickHouse.
 * Uses ClickHouse for database access with automatic connection pooling.
 *
 * ## Architecture
 *
 * ```
 * ClickHouseSearch (read-only search operations)
 *   └── data access via ClickHouse
 * ```
 *
 * ## Query Strategies
 *
 * - **search()**: Uses `argMax` for deduplication (fast, eventual consistency)
 * - **getTraceDetail()**: Uses `FINAL` for exact deduplication (accurate, lower frequency)
 * - **getAnalyticsSummary()**: Uses `argMax` (aggregates need only latest values)
 *
 * ## Query Constraints
 *
 * - `limit`: max 1000 (default 50)
 * - `offset`: max 10000 (cursor-based pagination recommended for deeper pages)
 * - `time_range`: max 30 days (search), max 90 days (analytics)
 * - `query`: max 500 characters
 * - `attributeFilters`: max 10
 * - `model[]`/`provider[]`: max 20 items
 * - Required: environmentId + startTime + endTime
 *
 * @example
 * ```ts
 * const searchService = yield* ClickHouseSearch;
 *
 * // Search spans with filters
 * const results = yield* searchService.search({
 *   environmentId: "env-123",
 *   startTime: new Date("2024-01-01"),
 *   endTime: new Date("2024-01-02"),
 *   query: "llm.call",
 * });
 *
 * // Get trace details with all spans
 * const trace = yield* searchService.getTraceDetail({
 *   environmentId: "env-123",
 *   traceId: "abc123",
 * });
 * ```
 */

import { Context, Effect, Layer } from "effect";

import { ClickHouse } from "@/db/clickhouse/client";
import { formatDateTime64 } from "@/db/clickhouse/transform";
import { ClickHouseError } from "@/errors";

// =============================================================================
// Query Constraints
// =============================================================================

const QUERY_CONSTRAINTS = {
  /** Maximum limit for search results */
  MAX_LIMIT: 1000,
  /** Default limit for search results */
  DEFAULT_LIMIT: 50,
  /** Maximum offset for pagination (prevents deep pagination) */
  MAX_OFFSET: 10000,
  /** Maximum time range in days for search */
  MAX_TIME_RANGE_DAYS_SEARCH: 30,
  /** Maximum time range in days for analytics */
  MAX_TIME_RANGE_DAYS_ANALYTICS: 90,
  /** Maximum query string length */
  MAX_QUERY_LENGTH: 500,
  /** Maximum attribute filters */
  MAX_ATTRIBUTE_FILTERS: 10,
  /** Maximum items in model/provider arrays */
  MAX_ARRAY_ITEMS: 20,
} as const;

// =============================================================================
// Input Types
// =============================================================================

/** Attribute filter for ad-hoc queries */
export interface AttributeFilter {
  /** Attribute key path (e.g., "gen_ai.request.model") */
  key: string;
  /** Comparison operator */
  operator: "eq" | "neq" | "contains" | "exists";
  /** Value to compare against (optional for "exists") */
  value?: string;
}

/** Input type for span search with required filters. */
export interface SpanSearchInput {
  /** Environment ID to scope the search (required). */
  environmentId: string;
  /** Start of time range (required). */
  startTime: Date;
  /** End of time range (required). */
  endTime: Date;
  /** Optional text search query (token-based matching on span name). */
  query?: string;
  /** Optional search in input messages (gen_ai.input_messages, mirascope.trace.arg_values). */
  inputMessagesQuery?: string;
  /** Optional search in output messages (gen_ai.output_messages, mirascope.trace.output). */
  outputMessagesQuery?: string;
  /** Enable fuzzy search using ngramSearch (default: false, uses LIKE). */
  fuzzySearch?: boolean;
  /** Filter by trace ID. */
  traceId?: string;
  /** Filter by span ID. */
  spanId?: string;
  /** Filter by model names. */
  model?: string[];
  /** Filter by provider names. */
  provider?: string[];
  /** Filter by function ID. */
  functionId?: string;
  /** Filter by function name (stored in function_name column). */
  functionName?: string;
  /**
   * Filter by span name prefix. Matches spans where name equals prefix
   * or starts with prefix followed by a dot (e.g., "myFunc" matches
   * "myFunc", "myFunc.call", "myFunc.stream").
   */
  spanNamePrefix?: string;
  /** Filter by error presence. */
  hasError?: boolean;
  /** Filter by minimum total tokens. */
  minTokens?: number;
  /** Filter by maximum total tokens. */
  maxTokens?: number;
  /** Filter by minimum duration (ms). */
  minDuration?: number;
  /** Filter by maximum duration (ms). */
  maxDuration?: number;
  /** Custom attribute filters. */
  attributeFilters?: AttributeFilter[];
  /** Number of results to return (max 1000). */
  limit?: number;
  /** Offset for pagination (max 10000). */
  offset?: number;
  /** Sort field. */
  sortBy?: "start_time" | "duration_ms" | "total_tokens";
  /** Sort direction. */
  sortOrder?: "asc" | "desc";
  /** Filter for root spans only (no parent). */
  rootSpansOnly?: boolean;
}

/** Input type for trace detail retrieval. */
export interface TraceDetailInput {
  /** Environment ID to scope the query (required). */
  environmentId: string;
  /** Trace ID to retrieve (required). */
  traceId: string;
}

/** Input type for analytics summary. */
export interface AnalyticsSummaryInput {
  /** Environment ID to scope the query (required). */
  environmentId: string;
  /** Start of time range (required). */
  startTime: Date;
  /** End of time range (required). */
  endTime: Date;
  /** Optional function ID filter. */
  functionId?: string;
}

// =============================================================================
// Output Types
// =============================================================================

/**
 * Span search result (summary mode).
 *
 * Note: attributes, events, links, resource_attributes are intentionally
 * excluded for query cost reduction. Use getTraceDetail() for full span data.
 */
export interface SpanSearchResult {
  traceId: string;
  spanId: string;
  name: string;
  startTime: string;
  durationMs: number | null;
  model: string | null;
  provider: string | null;
  inputTokens: number | null;
  outputTokens: number | null;
  totalTokens: number | null;
  costUsd: number | null;
  functionId: string | null;
  functionName: string | null;
  /** Whether this span has child spans */
  hasChildren: boolean;
}

/** Search response with pagination info. */
export interface SearchResponse {
  spans: SpanSearchResult[];
  total: number;
  hasMore: boolean;
}

/** Full span data for trace detail view. */
export interface SpanDetail {
  traceId: string;
  spanId: string;
  parentSpanId: string | null;
  environmentId: string;
  projectId: string;
  organizationId: string;
  startTime: string;
  endTime: string;
  durationMs: number | null;
  name: string;
  kind: number;
  statusCode: number | null;
  statusMessage: string | null;
  model: string | null;
  provider: string | null;
  inputTokens: number | null;
  outputTokens: number | null;
  totalTokens: number | null;
  costUsd: number | null;
  functionId: string | null;
  functionName: string | null;
  functionVersion: string | null;
  errorType: string | null;
  errorMessage: string | null;
  attributes: string;
  events: string | null;
  links: string | null;
  serviceName: string | null;
  serviceVersion: string | null;
  resourceAttributes: string | null;
}

/** Trace detail response with all spans. */
export interface TraceDetailResponse {
  traceId: string;
  spans: SpanDetail[];
  rootSpanId: string | null;
  totalDurationMs: number | null;
}

/** Analytics summary response. */
export interface AnalyticsSummaryResponse {
  totalSpans: number;
  avgDurationMs: number | null;
  p50DurationMs: number | null;
  p95DurationMs: number | null;
  p99DurationMs: number | null;
  errorRate: number;
  totalTokens: number;
  totalInputTokens: number;
  totalOutputTokens: number;
  totalCostUsd: number;
  topModels: Array<{ model: string; count: number }>;
  topFunctions: Array<{ functionName: string; count: number }>;
}

// =============================================================================
// Internal Row Types (ClickHouse query results)
// =============================================================================

interface SpanSummaryRow {
  environment_id: string;
  trace_id: string;
  span_id: string;
  name: string;
  start_time: string;
  duration_ms: number | null;
  model: string | null;
  provider: string | null;
  input_tokens: number | null;
  output_tokens: number | null;
  total_tokens: number | null;
  cost_usd: number | null;
  function_id: string | null;
  function_name: string | null;
  has_children: number; // ClickHouse returns 0/1 for boolean expressions
}

interface SpanDetailRow {
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
}

interface CountRow {
  count: number;
}

interface AnalyticsRow {
  total_spans: number;
  avg_duration_ms: number | null;
  p50_duration_ms: number | null;
  p95_duration_ms: number | null;
  p99_duration_ms: number | null;
  error_count: number;
  total_tokens: number;
  total_input_tokens: number;
  total_output_tokens: number;
  total_cost_usd: number;
}

interface TopModelRow {
  model_value: string;
  count: number;
}

interface TopFunctionRow {
  function_name_value: string;
  count: number;
}

// =============================================================================
// Service Interface
// =============================================================================

export interface ClickHouseSearchClient {
  /** Search spans with filters and pagination. */
  readonly search: (
    input: SpanSearchInput,
  ) => Effect.Effect<SearchResponse, ClickHouseError>;

  /** Get full trace detail with all spans. */
  readonly getTraceDetail: (
    input: TraceDetailInput,
  ) => Effect.Effect<TraceDetailResponse, ClickHouseError>;

  /** Get analytics summary for a time range. */
  readonly getAnalyticsSummary: (
    input: AnalyticsSummaryInput,
  ) => Effect.Effect<AnalyticsSummaryResponse, ClickHouseError>;
}

// =============================================================================
// Service Definition
// =============================================================================

export class ClickHouseSearch extends Context.Tag("ClickHouseSearch")<
  ClickHouseSearch,
  ClickHouseSearchClient
>() {
  static Default = Layer.effect(
    ClickHouseSearch,
    Effect.gen(function* () {
      const client = yield* ClickHouse;

      return {
        search: (input: SpanSearchInput) =>
          Effect.gen(function* () {
            // Validate input constraints
            const validatedInput = validateSearchInput(input);

            // Build WHERE clause and params
            const { clause: whereClause, params } =
              buildSearchWhereClause(validatedInput);

            // Build ORDER BY clause (validated)
            const orderBy = buildOrderByClause(
              validatedInput.sortBy ?? "start_time",
              validatedInput.sortOrder ?? "desc",
            );

            const limit =
              validatedInput.limit ?? QUERY_CONSTRAINTS.DEFAULT_LIMIT;
            const offset = validatedInput.offset ?? 0;

            // Summary query using argMax for deduplication (hot path)
            // Use table alias 's' to avoid column/alias name conflicts
            // Use LEFT JOIN with a subquery to compute has_children (ClickHouse doesn't support correlated subqueries)
            // Children subquery uses FINAL to match trace detail query's deduplication for consistency
            const rows = yield* client.unsafeQuery<SpanSummaryRow>(
              `
              SELECT
                main.*,
                children.parent_span_id IS NOT NULL as has_children
              FROM (
                SELECT
                  s.environment_id,
                  s.trace_id,
                  s.span_id,
                  argMax(s.name, s._version) as name,
                  argMax(s.start_time, s._version) as start_time,
                  argMax(s.duration_ms, s._version) as duration_ms,
                  argMax(s.model, s._version) as model,
                  argMax(s.provider, s._version) as provider,
                  argMax(s.input_tokens, s._version) as input_tokens,
                  argMax(s.output_tokens, s._version) as output_tokens,
                  argMax(s.total_tokens, s._version) as total_tokens,
                  argMax(s.cost_usd, s._version) as cost_usd,
                  argMax(s.function_id, s._version) as function_id,
                  argMax(s.function_name, s._version) as function_name
                FROM spans_analytics AS s
                WHERE ${whereClause}
                GROUP BY s.environment_id, s.trace_id, s.span_id
              ) AS main
              LEFT JOIN (
                SELECT DISTINCT
                  environment_id,
                  trace_id,
                  parent_span_id
                FROM spans_analytics FINAL
                WHERE environment_id = toUUID({environmentId_0:String})
                  AND parent_span_id IS NOT NULL
              ) AS children
              ON main.environment_id = children.environment_id
                AND main.trace_id = children.trace_id
                AND main.span_id = children.parent_span_id
              ORDER BY ${orderBy}
              LIMIT ${limit} OFFSET ${offset}
            `,
              params,
            );

            // Count query for pagination (uses same table alias 's')
            const countRows = yield* client.unsafeQuery<CountRow>(
              `
              SELECT count(DISTINCT (s.environment_id, s.trace_id, s.span_id)) as count
              FROM spans_analytics AS s
              WHERE ${whereClause}
            `,
              params,
            );
            const total = Number(countRows[0]?.count ?? 0);

            // Transform to API response format
            const spans = rows.map(transformToSearchResult);

            return {
              spans,
              total,
              hasMore: offset + spans.length < total,
            };
          }),

        getTraceDetail: (input: TraceDetailInput) =>
          Effect.gen(function* () {
            // Use FINAL for exact deduplication (accuracy priority)
            const rows = yield* client.unsafeQuery<SpanDetailRow>(
              `
              SELECT
                trace_id,
                span_id,
                parent_span_id,
                environment_id,
                project_id,
                organization_id,
                start_time,
                end_time,
                duration_ms,
                name,
                kind,
                status_code,
                status_message,
                model,
                provider,
                input_tokens,
                output_tokens,
                total_tokens,
                cost_usd,
                function_id,
                function_name,
                function_version,
                error_type,
                error_message,
                attributes,
                events,
                links,
                service_name,
                service_version,
                resource_attributes
              FROM spans_analytics FINAL
              WHERE environment_id = toUUID({environmentId:String})
                AND trace_id = {traceId:String}
              ORDER BY start_time ASC
            `,
              {
                environmentId: input.environmentId,
                traceId: input.traceId,
              },
            );

            if (rows.length === 0) {
              return {
                traceId: input.traceId,
                spans: [],
                rootSpanId: null,
                totalDurationMs: null,
              };
            }

            // Transform rows
            const spans = rows.map(transformToSpanDetail);

            // Find root span (no parent) and calculate total duration
            const rootSpan = spans.find((s) => s.parentSpanId === null);
            const rootSpanId = rootSpan?.spanId ?? null;

            // Calculate total duration from earliest start to latest end
            let minStart: number | null = null;
            let maxEnd: number | null = null;

            for (const span of spans) {
              const start = new Date(span.startTime).getTime();
              const end = new Date(span.endTime).getTime();

              if (minStart === null || start < minStart) minStart = start;
              if (maxEnd === null || end > maxEnd) maxEnd = end;
            }

            const totalDurationMs =
              minStart !== null && maxEnd !== null ? maxEnd - minStart : null;

            return {
              traceId: input.traceId,
              spans,
              rootSpanId,
              totalDurationMs,
            };
          }),

        getAnalyticsSummary: (input: AnalyticsSummaryInput) =>
          Effect.gen(function* () {
            // Validate time range (max 90 days for analytics)
            const timeDiff =
              input.endTime.getTime() - input.startTime.getTime();
            const daysDiff = timeDiff / (1000 * 60 * 60 * 24);
            if (daysDiff > QUERY_CONSTRAINTS.MAX_TIME_RANGE_DAYS_ANALYTICS) {
              return yield* Effect.fail(
                new ClickHouseError({
                  message: `Time range exceeds maximum of ${QUERY_CONSTRAINTS.MAX_TIME_RANGE_DAYS_ANALYTICS} days`,
                }),
              );
            }

            // Build base WHERE clause for analytics
            // Use toUUID() for explicit UUID type conversion
            const { clause: baseWhere, params: baseParams } =
              buildAnalyticsBaseWhere(input);

            // Main analytics query using argMax in subquery for deduplication
            // Outer query aggregates the deduplicated values
            // Use table alias 's' to avoid column/alias conflicts
            const analyticsRows = yield* client.unsafeQuery<AnalyticsRow>(
              `
              SELECT
                count() as total_spans,
                avg(duration_ms) as avg_duration_ms,
                quantile(0.5)(duration_ms) as p50_duration_ms,
                quantile(0.95)(duration_ms) as p95_duration_ms,
                quantile(0.99)(duration_ms) as p99_duration_ms,
                countIf(error_type IS NOT NULL) as error_count,
                sum(total_tokens) as total_tokens,
                sum(input_tokens) as total_input_tokens,
                sum(output_tokens) as total_output_tokens,
                sum(cost_usd) as total_cost_usd
              FROM (
                SELECT
                  argMax(s.duration_ms, s._version) as duration_ms,
                  argMax(s.error_type, s._version) as error_type,
                  argMax(s.total_tokens, s._version) as total_tokens,
                  argMax(s.input_tokens, s._version) as input_tokens,
                  argMax(s.output_tokens, s._version) as output_tokens,
                  argMax(s.cost_usd, s._version) as cost_usd
                FROM spans_analytics AS s
                WHERE ${baseWhere}
                GROUP BY s.environment_id, s.trace_id, s.span_id
              )
            `,
              baseParams,
            );
            const analytics = analyticsRows[0];

            // Top models query: deduplicate then group by model
            // Use table alias to avoid column/alias conflicts
            const modelWhere = `${baseWhere} AND s.model IS NOT NULL`;

            const topModelRows = yield* client.unsafeQuery<TopModelRow>(
              `
              SELECT model_value, count() as count
              FROM (
                SELECT argMax(s.model, s._version) as model_value
                FROM spans_analytics AS s
                WHERE ${modelWhere}
                GROUP BY s.environment_id, s.trace_id, s.span_id
              )
              WHERE model_value != ''
              GROUP BY model_value
              ORDER BY count DESC
              LIMIT 10
            `,
              baseParams,
            );

            // Top functions query: deduplicate then group by function_name
            // Use table alias to avoid column/alias conflicts
            const functionWhere = `${baseWhere} AND s.function_name IS NOT NULL`;

            const topFunctionRows = yield* client.unsafeQuery<TopFunctionRow>(
              `
              SELECT function_name_value, count() as count
              FROM (
                SELECT argMax(s.function_name, s._version) as function_name_value
                FROM spans_analytics AS s
                WHERE ${functionWhere}
                GROUP BY s.environment_id, s.trace_id, s.span_id
              )
              WHERE function_name_value != ''
              GROUP BY function_name_value
              ORDER BY count DESC
              LIMIT 10
            `,
              baseParams,
            );

            const totalSpans = Number(analytics?.total_spans ?? 0);
            const errorCount = Number(analytics?.error_count ?? 0);

            return {
              totalSpans,
              avgDurationMs:
                analytics?.avg_duration_ms != null
                  ? Number(analytics.avg_duration_ms)
                  : null,
              p50DurationMs:
                analytics?.p50_duration_ms != null
                  ? Number(analytics.p50_duration_ms)
                  : null,
              p95DurationMs:
                analytics?.p95_duration_ms != null
                  ? Number(analytics.p95_duration_ms)
                  : null,
              p99DurationMs:
                analytics?.p99_duration_ms != null
                  ? Number(analytics.p99_duration_ms)
                  : null,
              errorRate: totalSpans > 0 ? errorCount / totalSpans : 0,
              totalTokens: Number(analytics?.total_tokens ?? 0),
              totalInputTokens: Number(analytics?.total_input_tokens ?? 0),
              totalOutputTokens: Number(analytics?.total_output_tokens ?? 0),
              totalCostUsd: Number(analytics?.total_cost_usd ?? 0),
              topModels: topModelRows.map((r) => ({
                model: r.model_value,
                count: Number(r.count),
              })),
              topFunctions: topFunctionRows.map((r) => ({
                functionName: r.function_name_value,
                count: Number(r.count),
              })),
            };
          }),
      };
    }),
  );
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Validate search input constraints.
 */
function validateSearchInput(input: SpanSearchInput): SpanSearchInput {
  // Validate time range
  const timeDiff = input.endTime.getTime() - input.startTime.getTime();
  const daysDiff = timeDiff / (1000 * 60 * 60 * 24);
  if (daysDiff > QUERY_CONSTRAINTS.MAX_TIME_RANGE_DAYS_SEARCH) {
    throw new ClickHouseError({
      message: `Time range exceeds maximum of ${QUERY_CONSTRAINTS.MAX_TIME_RANGE_DAYS_SEARCH} days`,
    });
  }

  // Validate query length
  if (input.query && input.query.length > QUERY_CONSTRAINTS.MAX_QUERY_LENGTH) {
    throw new ClickHouseError({
      message: `Query exceeds maximum length of ${QUERY_CONSTRAINTS.MAX_QUERY_LENGTH} characters`,
    });
  }

  // Validate limit
  const limit = Math.min(
    input.limit ?? QUERY_CONSTRAINTS.DEFAULT_LIMIT,
    QUERY_CONSTRAINTS.MAX_LIMIT,
  );

  // Validate offset
  if ((input.offset ?? 0) > QUERY_CONSTRAINTS.MAX_OFFSET) {
    throw new ClickHouseError({
      message: `Offset exceeds maximum of ${QUERY_CONSTRAINTS.MAX_OFFSET}. Use cursor-based pagination for deeper results.`,
    });
  }

  // Validate attribute filters
  if (
    input.attributeFilters &&
    input.attributeFilters.length > QUERY_CONSTRAINTS.MAX_ATTRIBUTE_FILTERS
  ) {
    throw new ClickHouseError({
      message: `Too many attribute filters. Maximum is ${QUERY_CONSTRAINTS.MAX_ATTRIBUTE_FILTERS}.`,
    });
  }

  // Validate model/provider array lengths
  if (input.model && input.model.length > QUERY_CONSTRAINTS.MAX_ARRAY_ITEMS) {
    throw new ClickHouseError({
      message: `Too many model values. Maximum is ${QUERY_CONSTRAINTS.MAX_ARRAY_ITEMS}.`,
    });
  }
  if (
    input.provider &&
    input.provider.length > QUERY_CONSTRAINTS.MAX_ARRAY_ITEMS
  ) {
    throw new ClickHouseError({
      message: `Too many provider values. Maximum is ${QUERY_CONSTRAINTS.MAX_ARRAY_ITEMS}.`,
    });
  }

  return { ...input, limit };
}

/**
 * Build WHERE clause for search query.
 */
function buildSearchWhereClause(input: SpanSearchInput): {
  clause: string;
  params: Record<string, unknown>;
} {
  const conditions: string[] = [];
  const params: Record<string, unknown> = {};
  let paramIndex = 0;

  const addParam = (name: string, value: unknown) => {
    const key = `${name}_${paramIndex++}`;
    params[key] = value;
    return key;
  };

  // Required filters (all column references use 's.' prefix)
  // Use toUUID() for explicit type conversion (ClickHouse UUID type)
  const environmentIdKey = addParam("environmentId", input.environmentId);
  conditions.push(`s.environment_id = toUUID({${environmentIdKey}:String})`);

  const startTimeKey = addParam(
    "startTime",
    formatDateTime64(input.startTime, 9),
  );
  conditions.push(`s.start_time >= toDateTime64({${startTimeKey}:String}, 9)`);

  const endTimeKey = addParam("endTime", formatDateTime64(input.endTime, 9));
  conditions.push(`s.start_time <= toDateTime64({${endTimeKey}:String}, 9)`);

  // Optional text search using hasToken for tokenized matching
  if (input.query) {
    const tokens = input.query
      .trim()
      .toLowerCase()
      .split(/[^a-z0-9]+/g)
      .filter((token) => token.length > 0);
    for (const token of tokens) {
      const tokenKey = addParam("token", token);
      conditions.push(`hasToken(s.name_lower, {${tokenKey}:String})`);
    }
  }

  // Optional input messages search (gen_ai.input_messages, mirascope.trace.arg_values)
  if (input.inputMessagesQuery) {
    const inputKey = addParam("inputMessagesQuery", input.inputMessagesQuery);
    if (input.fuzzySearch) {
      // Fuzzy search using ngramSearch (score > 0.3 for typo tolerance)
      conditions.push(
        `(ngramSearchCaseInsensitive(JSONExtractString(s.attributes, 'gen_ai.input_messages'), {${inputKey}:String}) > 0.3 OR ngramSearchCaseInsensitive(JSONExtractString(s.attributes, 'mirascope.trace.arg_values'), {${inputKey}:String}) > 0.3)`,
      );
    } else {
      // Exact substring match using LIKE
      const inputKeyLike = addParam(
        "inputMessagesQueryLike",
        `%${input.inputMessagesQuery}%`,
      );
      conditions.push(
        `(JSONExtractString(s.attributes, 'gen_ai.input_messages') LIKE {${inputKeyLike}:String} OR JSONExtractString(s.attributes, 'mirascope.trace.arg_values') LIKE {${inputKeyLike}:String})`,
      );
    }
  }

  // Optional output messages search (gen_ai.output_messages, mirascope.trace.output)
  if (input.outputMessagesQuery) {
    const outputKey = addParam(
      "outputMessagesQuery",
      input.outputMessagesQuery,
    );
    if (input.fuzzySearch) {
      // Fuzzy search using ngramSearch (score > 0.3 for typo tolerance)
      conditions.push(
        `(ngramSearchCaseInsensitive(JSONExtractString(s.attributes, 'gen_ai.output_messages'), {${outputKey}:String}) > 0.3 OR ngramSearchCaseInsensitive(JSONExtractString(s.attributes, 'mirascope.trace.output'), {${outputKey}:String}) > 0.3)`,
      );
    } else {
      // Exact substring match using LIKE
      const outputKeyLike = addParam(
        "outputMessagesQueryLike",
        `%${input.outputMessagesQuery}%`,
      );
      conditions.push(
        `(JSONExtractString(s.attributes, 'gen_ai.output_messages') LIKE {${outputKeyLike}:String} OR JSONExtractString(s.attributes, 'mirascope.trace.output') LIKE {${outputKeyLike}:String})`,
      );
    }
  }

  // Optional filters
  if (input.traceId) {
    const traceIdKey = addParam("traceId", input.traceId);
    conditions.push(`s.trace_id = {${traceIdKey}:String}`);
  }

  if (input.spanId) {
    const spanIdKey = addParam("spanId", input.spanId);
    conditions.push(`s.span_id = {${spanIdKey}:String}`);
  }

  if (input.model && input.model.length > 0) {
    const modelKey = addParam("model", input.model);
    conditions.push(`s.model IN {${modelKey}:Array(String)}`);
  }

  if (input.provider && input.provider.length > 0) {
    const providerKey = addParam("provider", input.provider);
    conditions.push(`s.provider IN {${providerKey}:Array(String)}`);
  }

  if (input.functionId) {
    const functionIdKey = addParam("functionId", input.functionId);
    conditions.push(`s.function_id = toUUID({${functionIdKey}:String})`);
  }

  if (input.functionName) {
    const functionNameKey = addParam("functionName", input.functionName);
    conditions.push(`s.function_name = {${functionNameKey}:String}`);
  }

  // Match span name exactly or with a method suffix (e.g., "myFunc" matches "myFunc", "myFunc.call", "myFunc.stream")
  if (input.spanNamePrefix) {
    const prefixKey = addParam("spanNamePrefix", input.spanNamePrefix);
    const prefixDotKey = addParam(
      "spanNamePrefixDot",
      `${input.spanNamePrefix}.%`,
    );
    conditions.push(
      `(s.name = {${prefixKey}:String} OR s.name LIKE {${prefixDotKey}:String})`,
    );
  }

  if (input.hasError === true) {
    conditions.push("s.error_type IS NOT NULL");
  } else if (input.hasError === false) {
    conditions.push("s.error_type IS NULL");
  }

  if (input.minTokens !== undefined) {
    const minTokensKey = addParam("minTokens", input.minTokens);
    conditions.push(`s.total_tokens >= {${minTokensKey}:Int64}`);
  }

  if (input.maxTokens !== undefined) {
    const maxTokensKey = addParam("maxTokens", input.maxTokens);
    conditions.push(`s.total_tokens <= {${maxTokensKey}:Int64}`);
  }

  if (input.minDuration !== undefined) {
    const minDurationKey = addParam("minDuration", input.minDuration);
    conditions.push(`s.duration_ms >= {${minDurationKey}:Int64}`);
  }

  if (input.maxDuration !== undefined) {
    const maxDurationKey = addParam("maxDuration", input.maxDuration);
    conditions.push(`s.duration_ms <= {${maxDurationKey}:Int64}`);
  }

  // Root spans only filter (no parent)
  if (input.rootSpansOnly) {
    conditions.push("s.parent_span_id IS NULL");
  }

  // Attribute filters
  if (input.attributeFilters) {
    for (const filter of input.attributeFilters) {
      switch (filter.operator) {
        case "eq":
          {
            const keyParam = addParam("attrKey", filter.key);
            const valueParam = addParam("attrValue", filter.value ?? "");
            conditions.push(
              `JSONExtractString(s.attributes, {${keyParam}:String}) = {${valueParam}:String}`,
            );
          }
          break;
        case "neq":
          {
            const keyParam = addParam("attrKey", filter.key);
            const valueParam = addParam("attrValue", filter.value ?? "");
            conditions.push(
              `JSONExtractString(s.attributes, {${keyParam}:String}) != {${valueParam}:String}`,
            );
          }
          break;
        case "contains":
          {
            const keyParam = addParam("attrKey", filter.key);
            const valueParam = addParam("attrValue", `%${filter.value ?? ""}%`);
            conditions.push(
              `JSONExtractString(s.attributes, {${keyParam}:String}) LIKE {${valueParam}:String}`,
            );
          }
          break;
        case "exists":
          {
            const keyParam = addParam("attrKey", filter.key);
            conditions.push(`JSONHas(s.attributes, {${keyParam}:String})`);
          }
          break;
      }
    }
  }

  return {
    clause: conditions.join(" AND "),
    params,
  };
}

/**
 * Build WHERE clause for analytics queries.
 */
function buildAnalyticsBaseWhere(input: AnalyticsSummaryInput): {
  clause: string;
  params: Record<string, unknown>;
} {
  const params: Record<string, unknown> = {};
  let paramIndex = 0;

  const addParam = (name: string, value: unknown) => {
    const key = `${name}_${paramIndex++}`;
    params[key] = value;
    return key;
  };

  const environmentIdKey = addParam("environmentId", input.environmentId);
  const startTimeKey = addParam(
    "startTime",
    formatDateTime64(input.startTime, 9),
  );
  const endTimeKey = addParam("endTime", formatDateTime64(input.endTime, 9));

  const conditions = [
    `s.environment_id = toUUID({${environmentIdKey}:String})`,
    `s.start_time >= toDateTime64({${startTimeKey}:String}, 9)`,
    `s.start_time <= toDateTime64({${endTimeKey}:String}, 9)`,
  ];

  if (input.functionId) {
    const functionIdKey = addParam("functionId", input.functionId);
    conditions.push(`s.function_id = toUUID({${functionIdKey}:String})`);
  }

  return {
    clause: conditions.join(" AND "),
    params,
  };
}

/**
 * Build ORDER BY clause for search query.
 */
function buildOrderByClause(
  sortBy: "start_time" | "duration_ms" | "total_tokens",
  sortOrder: "asc" | "desc",
): string {
  const direction = sortOrder.toUpperCase();
  // Use column alias - this works because ORDER BY is on the outer query
  // which references the deduplicated subquery results
  return `${sortBy} ${direction}`;
}

/**
 * Convert ClickHouse DateTime64 string to ISO-8601 UTC.
 *
 * Handles:
 * - ClickHouse format: "2024-01-01 12:34:56.123000000" -> "2024-01-01T12:34:56.123Z"
 * - Already ISO with Z: returned as-is
 * - ISO without Z: appends Z (assumes UTC)
 * - Null: returns null
 */
const toIsoUtc = (value: string | null): string | null => {
  if (value === null) return null;
  if (value.endsWith("Z")) return value;
  if (value.includes("T")) return `${value}Z`;
  const [datePart, timePart = "00:00:00"] = value.split(" ");
  const [time, fraction = ""] = timePart.split(".");
  const ms = fraction.padEnd(3, "0").slice(0, 3);
  return `${datePart}T${time}.${ms}Z`;
};

/**
 * Transform ClickHouse row to API search result (snake_case -> camelCase).
 */
function transformToSearchResult(row: SpanSummaryRow): SpanSearchResult {
  return {
    traceId: row.trace_id,
    spanId: row.span_id,
    name: row.name,
    startTime: toIsoUtc(row.start_time) ?? row.start_time,
    durationMs: row.duration_ms,
    model: row.model,
    provider: row.provider,
    inputTokens: row.input_tokens,
    outputTokens: row.output_tokens,
    totalTokens: row.total_tokens,
    costUsd: row.cost_usd,
    functionId: row.function_id,
    functionName: row.function_name,
    hasChildren: row.has_children === 1,
  };
}

/**
 * Transform ClickHouse row to API span detail (snake_case -> camelCase).
 */
function transformToSpanDetail(row: SpanDetailRow): SpanDetail {
  return {
    traceId: row.trace_id,
    spanId: row.span_id,
    parentSpanId: row.parent_span_id,
    environmentId: row.environment_id,
    projectId: row.project_id,
    organizationId: row.organization_id,
    startTime: toIsoUtc(row.start_time) ?? row.start_time,
    endTime: toIsoUtc(row.end_time) ?? row.end_time,
    durationMs: row.duration_ms,
    name: row.name,
    kind: row.kind,
    statusCode: row.status_code,
    statusMessage: row.status_message,
    model: row.model,
    provider: row.provider,
    inputTokens: row.input_tokens,
    outputTokens: row.output_tokens,
    totalTokens: row.total_tokens,
    costUsd: row.cost_usd,
    functionId: row.function_id,
    functionName: row.function_name,
    functionVersion: row.function_version,
    errorType: row.error_type,
    errorMessage: row.error_message,
    attributes: row.attributes,
    events: row.events,
    links: row.links,
    serviceName: row.service_name,
    serviceVersion: row.service_version,
    resourceAttributes: row.resource_attributes,
  };
}
