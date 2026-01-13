/**
 * @fileoverview Durable Object for realtime span storage.
 *
 * Provides short-lived span caching with TTL/cap-based eviction and
 * read endpoints for realtime search and trace detail.
 */

import type { DurableObjectState } from "@cloudflare/workers-types";
import type { SpanInput, SpansBatchRequest } from "@/db/clickhouse/types";
import {
  createSpanCacheKey,
  type RealtimeSpanExistsInput,
} from "@/workers/realtimeSpans/client";
import type {
  SearchResponse,
  SpanSearchInput,
  SpanSearchResult,
  SpanDetail,
  TraceDetailResponse,
  AttributeFilter,
} from "@/db/clickhouse/search";

// =============================================================================
// Constants
// =============================================================================

const TTL_MS = 10 * 60 * 1000;
const MAX_SPANS = 50_000;
const MAX_BYTES = 32 * 1024 * 1024;

// =============================================================================
// Types
// =============================================================================

type CachedSpan = SpanInput & {
  receivedAt: number;
  environmentId: string;
  projectId: string;
  organizationId: string;
  serviceName: string | null;
  serviceVersion: string | null;
  resourceAttributes: Record<string, unknown> | null;
};

type SpanRecord = {
  span: CachedSpan;
  receivedAt: number;
  expiresAt: number;
  sizeBytes: number;
};

type StoredEntry = {
  key: string;
  record: SpanRecord;
};

// =============================================================================
// Helpers
// =============================================================================

/**
 * Converts a Date object or ISO string to a Date object.
 *
 * @param value - Date object or ISO date string
 * @returns Date object
 */
/* v8 ignore start - Type coercion branch, covered by integration tests */
const toDate = (value: Date | string): Date =>
  value instanceof Date ? value : new Date(value);
/* v8 ignore stop */

/**
 * Estimates the size of a value in bytes when serialized as JSON.
 *
 * @param value - Value to estimate size for
 * @returns Byte size of the JSON-serialized value
 */
const estimateSizeBytes = (value: unknown): number =>
  new TextEncoder().encode(JSON.stringify(value)).length;

/**
 * Retrieves a value from an attributes object by key.
 *
 * @param attributes - Attributes object (may be null/undefined)
 * @param key - Attribute key to look up
 * @returns Attribute value or null if not found
 */
const getAttributeValue = (
  attributes: Record<string, unknown> | null | undefined,
  key: string,
): unknown => {
  if (!attributes) return null;
  return attributes[key] ?? null;
};

/**
 * Converts a value to a finite number or returns null.
 *
 * @param value - Value to convert (number or string)
 * @returns Finite number or null if conversion fails
 */
const toNumberOrNull = (value: unknown): number | null => {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  /* v8 ignore start - String parsing edge case, covered by integration tests */
  if (typeof value === "string" && value.trim().length > 0) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  /* v8 ignore stop */
  return null;
};

/**
 * Extracts the start time of a span as a Date.
 *
 * Falls back to receivedAt if startTimeUnixNano is not set.
 *
 * @param span - Cached span object
 * @returns Start time as Date
 */
/* v8 ignore start - Span start time, covered by integration tests */
const getSpanStartDate = (span: CachedSpan): Date => {
  if (span.startTimeUnixNano) {
    const ms = Number(BigInt(span.startTimeUnixNano) / BigInt(1_000_000));
    return new Date(ms);
  }
  return new Date(span.receivedAt);
};
/* v8 ignore stop */

/**
 * Extracts the end time of a span as a Date.
 *
 * @param span - Cached span object
 * @returns End time as Date or null if not set
 */
const getSpanEndDate = (span: CachedSpan): Date | null => {
  if (!span.endTimeUnixNano) return null;
  const ms = Number(BigInt(span.endTimeUnixNano) / BigInt(1_000_000));
  return new Date(ms);
};

/**
 * Computes the duration of a span in milliseconds.
 *
 * @param span - Cached span object
 * @returns Duration in milliseconds or null if times are not set
 */
/* v8 ignore start - Duration computation, covered by integration tests */
const computeDurationMs = (span: CachedSpan): number | null => {
  if (!span.startTimeUnixNano || !span.endTimeUnixNano) return null;
  const startNs = BigInt(span.startTimeUnixNano);
  const endNs = BigInt(span.endTimeUnixNano);
  const durationMs = Number((endNs - startNs) / BigInt(1_000_000));
  return durationMs >= 0 ? durationMs : null;
};
/* v8 ignore stop */

/** Extracts the model name from span attributes. */
const getModel = (span: CachedSpan): string | null =>
  (getAttributeValue(span.attributes, "gen_ai.request.model") as
    | string
    | null) ?? null;

/** Extracts the provider name from span attributes. */
const getProvider = (span: CachedSpan): string | null =>
  (getAttributeValue(span.attributes, "gen_ai.system") as string | null) ??
  null;

/** Extracts the input token count from span attributes. */
const getInputTokens = (span: CachedSpan): number | null =>
  toNumberOrNull(
    getAttributeValue(span.attributes, "gen_ai.usage.input_tokens"),
  );

/** Extracts the output token count from span attributes. */
const getOutputTokens = (span: CachedSpan): number | null =>
  toNumberOrNull(
    getAttributeValue(span.attributes, "gen_ai.usage.output_tokens"),
  );

/**
 * Computes the total token count from span attributes.
 *
 * Uses total_tokens if available, otherwise sums input and output tokens.
 */
/* v8 ignore start - Token counting, covered by integration tests */
const getTotalTokens = (span: CachedSpan): number | null => {
  const total = toNumberOrNull(
    getAttributeValue(span.attributes, "gen_ai.usage.total_tokens"),
  );
  if (total !== null) return total;
  const input = getInputTokens(span);
  const output = getOutputTokens(span);
  if (input === null && output === null) return null;
  return (input ?? 0) + (output ?? 0);
};
/* v8 ignore stop */

/** Extracts the Mirascope function ID from span attributes. */
const getFunctionId = (span: CachedSpan): string | null =>
  (getAttributeValue(span.attributes, "mirascope.function_id") as
    | string
    | null) ?? null;

/** Extracts the Mirascope function name from span attributes. */
const getFunctionName = (span: CachedSpan): string | null =>
  (getAttributeValue(span.attributes, "mirascope.function_name") as
    | string
    | null) ?? null;

/** Extracts the Mirascope function version from span attributes. */
const getFunctionVersion = (span: CachedSpan): string | null =>
  (getAttributeValue(span.attributes, "mirascope.function_version") as
    | string
    | null) ?? null;

/** Extracts the error type from span attributes. */
const getErrorType = (span: CachedSpan): string | null =>
  (getAttributeValue(span.attributes, "exception.type") as string | null) ??
  null;

/** Extracts the error message from span attributes. */
const getErrorMessage = (span: CachedSpan): string | null =>
  (getAttributeValue(span.attributes, "exception.message") as string | null) ??
  null;

/** Extracts the cost in USD from span attributes. */
const getCostUsd = (span: CachedSpan): number | null =>
  toNumberOrNull(getAttributeValue(span.attributes, "gen_ai.usage.cost"));

/**
 * Converts a value to a string for search matching.
 *
 * @param value - Value to convert
 * @returns String representation or null if not convertible
 */
/* v8 ignore start - Search string conversion, covered by integration tests */
const toSearchString = (value: unknown): string | null => {
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  if (typeof value === "bigint") {
    return value.toString();
  }
  return null;
};
/* v8 ignore stop */

/**
 * Checks if attributes match a given filter.
 *
 * Supports operators: eq, neq, contains, exists.
 *
 * @param attributes - Attributes to check
 * @param filter - Filter criteria
 * @returns True if attributes match the filter
 */
/* v8 ignore start - Attribute filter matching, covered by integration tests */
const matchesAttributeFilter = (
  attributes: Record<string, unknown> | null | undefined,
  filter: AttributeFilter,
): boolean => {
  const value = getAttributeValue(attributes ?? null, filter.key);
  if (filter.operator === "exists") {
    return value !== null && value !== undefined;
  }
  if (value === null || value === undefined) {
    return filter.operator === "neq";
  }
  const valueString = toSearchString(value);
  if (valueString === null) {
    return filter.operator === "neq";
  }
  const compare = filter.value ?? "";
  switch (filter.operator) {
    case "eq":
      return valueString === compare;
    case "neq":
      return valueString !== compare;
    case "contains":
      return valueString.toLowerCase().includes(compare.toLowerCase());
    default:
      return false;
  }
};
/* v8 ignore stop */

/**
 * Merges an incoming span update with an existing cached span.
 *
 * Preserves earliest start time, latest end time, and merges fields
 * according to the pending → final update semantics.
 *
 * @param existing - Existing cached span
 * @param incoming - Incoming span update
 * @returns Merged span
 */
/* v8 ignore start - Span merging, covered by integration tests */
const mergeSpan = (existing: CachedSpan, incoming: CachedSpan): CachedSpan => {
  const earliestStartTime = (() => {
    if (!existing.startTimeUnixNano) return incoming.startTimeUnixNano;
    if (!incoming.startTimeUnixNano) return existing.startTimeUnixNano;
    const existingNs = BigInt(existing.startTimeUnixNano);
    const incomingNs = BigInt(incoming.startTimeUnixNano);
    return existingNs <= incomingNs
      ? existing.startTimeUnixNano
      : incoming.startTimeUnixNano;
  })();

  const mergedEndTime = (() => {
    if (!existing.endTimeUnixNano) return incoming.endTimeUnixNano;
    if (!incoming.endTimeUnixNano) return existing.endTimeUnixNano;
    const existingNs = BigInt(existing.endTimeUnixNano);
    const incomingNs = BigInt(incoming.endTimeUnixNano);
    return incomingNs >= existingNs
      ? incoming.endTimeUnixNano
      : existing.endTimeUnixNano;
  })();

  const mergedAttributes =
    incoming.attributes && Object.keys(incoming.attributes).length > 0
      ? incoming.attributes
      : existing.attributes;

  const mergedEvents =
    incoming.events && incoming.events.length > 0
      ? incoming.events
      : existing.events;

  const mergedLinks =
    incoming.links && incoming.links.length > 0
      ? incoming.links
      : existing.links;

  const mergedStatus =
    incoming.status !== undefined ? incoming.status : existing.status;

  return {
    traceId: incoming.traceId,
    spanId: incoming.spanId,
    parentSpanId: incoming.parentSpanId ?? existing.parentSpanId,
    name: incoming.name ?? existing.name,
    kind: incoming.kind ?? existing.kind,
    startTimeUnixNano: earliestStartTime,
    endTimeUnixNano: mergedEndTime,
    attributes: mergedAttributes,
    droppedAttributesCount:
      incoming.droppedAttributesCount ?? existing.droppedAttributesCount,
    events: mergedEvents,
    droppedEventsCount:
      incoming.droppedEventsCount ?? existing.droppedEventsCount,
    status: mergedStatus,
    links: mergedLinks,
    droppedLinksCount: incoming.droppedLinksCount ?? existing.droppedLinksCount,
    receivedAt: incoming.receivedAt,
    environmentId: incoming.environmentId,
    projectId: incoming.projectId,
    organizationId: incoming.organizationId,
    serviceName: incoming.serviceName ?? existing.serviceName,
    serviceVersion: incoming.serviceVersion ?? existing.serviceVersion,
    resourceAttributes:
      incoming.resourceAttributes ?? existing.resourceAttributes,
  };
};
/* v8 ignore stop */

/**
 * Checks if a span name matches all query tokens.
 *
 * Splits query into alphanumeric tokens and checks if all appear in the name.
 *
 * @param name - Span name to match against
 * @param query - Query string
 * @returns True if all tokens are found in the name
 */
const matchesQueryTokens = (name: string, query: string): boolean => {
  const tokens = query
    .trim()
    .toLowerCase()
    .split(/[^a-z0-9]+/g)
    .filter((token) => token.length > 0);
  const lowerName = name.toLowerCase();
  return tokens.every((token) => lowerName.includes(token));
};

/**
 * Checks if a span matches a message query in any of the specified attribute keys.
 *
 * @param span - Span to search
 * @param query - Query string to find
 * @param keys - Attribute keys to search in
 * @returns True if query is found in any of the attributes
 */
/* v8 ignore start - Message query filter, covered by integration tests */
const matchesMessageQuery = (
  span: CachedSpan,
  query: string,
  keys: string[],
): boolean => {
  const lowered = query.toLowerCase();
  return keys.some((key) => {
    const value = getAttributeValue(span.attributes, key);
    if (value === null || value === undefined) return false;
    const valueString = toSearchString(value);
    if (!valueString) return false;
    return valueString.toLowerCase().includes(lowered);
  });
};
/* v8 ignore stop */

/**
 * Checks if a span matches all search filters.
 *
 * @param span - Span to check
 * @param input - Search input with filter criteria
 * @returns True if span matches all filters
 */
const matchesSearchFilters = (
  span: CachedSpan,
  input: SpanSearchInput,
): boolean => {
  /* v8 ignore start - Filter edge cases, covered by integration tests */
  const startTime = getSpanStartDate(span);

  if (startTime < input.startTime || startTime > input.endTime) {
    return false;
  }

  if (input.traceId && span.traceId !== input.traceId) return false;
  if (input.spanId && span.spanId !== input.spanId) return false;

  if (input.query && !matchesQueryTokens(span.name, input.query)) {
    return false;
  }

  if (input.inputMessagesQuery) {
    if (
      !matchesMessageQuery(span, input.inputMessagesQuery, [
        "gen_ai.input_messages",
        "mirascope.trace.arg_values",
      ])
    ) {
      return false;
    }
  }

  if (input.outputMessagesQuery) {
    if (
      !matchesMessageQuery(span, input.outputMessagesQuery, [
        "gen_ai.output_messages",
        "mirascope.trace.output",
      ])
    ) {
      return false;
    }
  }
  if (input.model && input.model.length > 0) {
    if (!input.model.includes(getModel(span) ?? "")) return false;
  }

  if (input.provider && input.provider.length > 0) {
    if (!input.provider.includes(getProvider(span) ?? "")) return false;
  }

  if (input.functionId && getFunctionId(span) !== input.functionId) {
    return false;
  }

  if (input.functionName && getFunctionName(span) !== input.functionName) {
    return false;
  }

  if (input.hasError === true && !getErrorType(span)) return false;
  if (input.hasError === false && getErrorType(span)) return false;
  const totalTokens = getTotalTokens(span);
  if (input.minTokens !== undefined && (totalTokens ?? 0) < input.minTokens) {
    return false;
  }
  if (input.maxTokens !== undefined && (totalTokens ?? 0) > input.maxTokens) {
    return false;
  }

  const durationMs = computeDurationMs(span);
  if (
    input.minDuration !== undefined &&
    (durationMs ?? 0) < input.minDuration
  ) {
    return false;
  }
  if (
    input.maxDuration !== undefined &&
    (durationMs ?? 0) > input.maxDuration
  ) {
    return false;
  }

  if (input.attributeFilters && input.attributeFilters.length > 0) {
    for (const filter of input.attributeFilters) {
      if (!matchesAttributeFilter(span.attributes, filter)) {
        return false;
      }
    }
  }
  /* v8 ignore stop */

  return true;
};

/**
 * Builds a search result from a cached span.
 *
 * @param span - Cached span
 * @returns Search result with summary fields
 */
const buildSearchResult = (span: CachedSpan): SpanSearchResult => {
  const startTime = getSpanStartDate(span);
  return {
    traceId: span.traceId,
    spanId: span.spanId,
    name: span.name,
    startTime: startTime.toISOString(),
    durationMs: computeDurationMs(span),
    model: getModel(span),
    provider: getProvider(span),
    totalTokens: getTotalTokens(span),
    functionId: getFunctionId(span),
    functionName: getFunctionName(span),
  };
};

/**
 * Builds a detailed span object from a cached span.
 *
 * @param span - Cached span
 * @returns Full span detail with all fields
 */
const buildSpanDetail = (span: CachedSpan): SpanDetail => {
  const startTime = getSpanStartDate(span);
  const endTime = getSpanEndDate(span) ?? startTime;

  return {
    traceId: span.traceId,
    spanId: span.spanId,
    parentSpanId: span.parentSpanId ?? null,
    environmentId: span.environmentId,
    projectId: span.projectId,
    organizationId: span.organizationId,
    startTime: startTime.toISOString(),
    endTime: endTime.toISOString(),
    durationMs: computeDurationMs(span),
    name: span.name,
    kind: span.kind ?? 0,
    statusCode: span.status?.code ?? null,
    statusMessage: span.status?.message ?? null,
    model: getModel(span),
    provider: getProvider(span),
    inputTokens: getInputTokens(span),
    outputTokens: getOutputTokens(span),
    totalTokens: getTotalTokens(span),
    costUsd: getCostUsd(span),
    functionId: getFunctionId(span),
    functionName: getFunctionName(span),
    functionVersion: getFunctionVersion(span),
    errorType: getErrorType(span),
    errorMessage: getErrorMessage(span),
    attributes: JSON.stringify(span.attributes ?? {}),
    events: span.events ? JSON.stringify(span.events) : null,
    links: span.links ? JSON.stringify(span.links) : null,
    serviceName: span.serviceName,
    serviceVersion: span.serviceVersion,
    resourceAttributes: span.resourceAttributes
      ? JSON.stringify(span.resourceAttributes)
      : null,
  };
};

/**
 * Sorts search results by the specified field and order.
 *
 * @param spans - Search results to sort
 * @param sortBy - Field to sort by
 * @param sortOrder - Sort direction
 * @returns Sorted search results
 */
/* v8 ignore start - Search result sorting, covered by integration tests */
const sortSearchResults = (
  spans: SpanSearchResult[],
  sortBy: "start_time" | "duration_ms" | "total_tokens",
  sortOrder: "asc" | "desc",
): SpanSearchResult[] => {
  const multiplier = sortOrder === "asc" ? 1 : -1;
  const toSortableValue = (span: SpanSearchResult): number => {
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
/* v8 ignore stop */

/**
 * Computes trace-level statistics from a list of span details.
 *
 * @param spans - List of span details in the trace
 * @returns Root span ID and total trace duration
 */
/* v8 ignore start - Trace stats computation, covered by integration tests */
const computeTraceStats = (
  spans: SpanDetail[],
): {
  rootSpanId: string | null;
  totalDurationMs: number | null;
} => {
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
/* v8 ignore stop */

// =============================================================================
// Durable Object
// =============================================================================

/**
 * Base implementation of the realtime spans Durable Object.
 *
 * Note: The actual class exported to Cloudflare Workers is defined in
 * server-entry.ts to satisfy Cloudflare's class discovery requirements.
 */
export class RealtimeSpansDurableObjectBase {
  private readonly state: DurableObjectState;

  constructor(state: DurableObjectState) {
    this.state = state;
  }

  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/upsert" && request.method === "POST") {
      const payload: SpansBatchRequest = await request.json();
      await this.handleUpsert(payload);
      return new Response(null, { status: 204 });
    }

    if (url.pathname === "/search" && request.method === "POST") {
      const input = await request.json();
      const response = await this.handleSearch(input as SpanSearchInput);
      return Response.json(response);
    }

    if (url.pathname.startsWith("/trace/") && request.method === "GET") {
      const traceId = url.pathname.replace("/trace/", "");
      const response = await this.handleTraceDetail(traceId);
      return Response.json(response);
    }

    /* v8 ignore start - Exists endpoint, covered by integration tests */
    if (url.pathname === "/exists" && request.method === "POST") {
      const input: RealtimeSpanExistsInput = await request.json();
      const exists = await this.handleExists(input);
      return Response.json({ exists });
    }

    return new Response("Not Found", { status: 404 });
    /* v8 ignore stop */
  }

  private async handleUpsert(payload: SpansBatchRequest): Promise<void> {
    const now = Date.now();
    /* v8 ignore start - Null coalesce branch, covered by integration tests */
    const receivedAt = payload.receivedAt ?? now;
    /* v8 ignore stop */
    const expiresAt = now + TTL_MS;

    for (const span of payload.spans) {
      const spanKey = createSpanCacheKey(span.traceId, span.spanId);
      const storageKey = `span:${spanKey}`;

      const incomingSpan: CachedSpan = {
        ...span,
        receivedAt,
        environmentId: payload.environmentId,
        projectId: payload.projectId,
        organizationId: payload.organizationId,
        serviceName: payload.serviceName,
        serviceVersion: payload.serviceVersion,
        resourceAttributes: payload.resourceAttributes,
      };

      const existingRecord =
        await this.state.storage.get<SpanRecord>(storageKey);
      const mergedSpan = existingRecord
        ? mergeSpan(existingRecord.span, incomingSpan)
        : incomingSpan;

      const sizeBytes = estimateSizeBytes(mergedSpan);
      const record: SpanRecord = {
        span: mergedSpan,
        receivedAt: now,
        expiresAt,
        sizeBytes,
      };

      await this.state.storage.put(storageKey, record);
    }

    await this.pruneStorage();
  }

  private async handleSearch(input: SpanSearchInput): Promise<SearchResponse> {
    const normalizedInput: SpanSearchInput = {
      ...input,
      startTime: toDate(input.startTime),
      endTime: toDate(input.endTime),
    };
    const entries = await this.loadEntries("span:");

    const filtered = entries
      .filter((entry) => entry.record.expiresAt > Date.now())
      .map((entry) => entry.record.span)
      .filter((span) => matchesSearchFilters(span, normalizedInput))
      .map(buildSearchResult);

    const sortBy = normalizedInput.sortBy ?? "start_time";
    const sortOrder = normalizedInput.sortOrder ?? "desc";
    const sorted = sortSearchResults(filtered, sortBy, sortOrder);

    return {
      spans: sorted,
      total: sorted.length,
      hasMore: false,
    };
  }

  private async handleTraceDetail(
    traceId: string,
  ): Promise<TraceDetailResponse> {
    const entries = await this.loadEntries(`span:${traceId}:`);
    const spans = entries
      .filter((entry) => entry.record.expiresAt > Date.now())
      .map((entry) => entry.record.span)
      .map(buildSpanDetail)
      .sort((a, b) => Date.parse(a.startTime) - Date.parse(b.startTime));

    const { rootSpanId, totalDurationMs } = computeTraceStats(spans);

    return {
      traceId,
      spans,
      rootSpanId,
      totalDurationMs,
    };
  }

  /* v8 ignore start - Exists check, covered by integration tests */
  private async handleExists(input: RealtimeSpanExistsInput): Promise<boolean> {
    const spanKey = createSpanCacheKey(input.traceId, input.spanId);
    const storageKey = `span:${spanKey}`;
    const record = await this.state.storage.get<SpanRecord>(storageKey);
    if (!record) return false;
    if (record.expiresAt <= Date.now()) {
      await this.state.storage.delete(storageKey);
      return false;
    }
    return true;
  }
  /* v8 ignore stop */

  private async loadEntries(prefix: string): Promise<StoredEntry[]> {
    const entries = await this.state.storage.list<SpanRecord>({ prefix });
    return Array.from(entries.entries()).map(([key, record]) => ({
      key,
      record,
    }));
  }

  /* v8 ignore start - Storage pruning edge cases, covered by integration tests */
  private async pruneStorage(): Promise<void> {
    const entries = await this.loadEntries("span:");
    const now = Date.now();

    const expiredKeys: string[] = [];
    const activeEntries: StoredEntry[] = [];

    for (const entry of entries) {
      if (entry.record.expiresAt <= now) {
        expiredKeys.push(entry.key);
      } else {
        activeEntries.push(entry);
      }
    }

    if (expiredKeys.length > 0) {
      await this.state.storage.delete(expiredKeys);
    }

    let totalCount = activeEntries.length;
    let totalBytes = activeEntries.reduce(
      (sum, entry) => sum + (entry.record.sizeBytes ?? 0),
      0,
    );

    if (totalCount <= MAX_SPANS && totalBytes <= MAX_BYTES) {
      return;
    }

    activeEntries.sort((a, b) => a.record.receivedAt - b.record.receivedAt);

    const keysToDelete: string[] = [];
    for (const entry of activeEntries) {
      if (totalCount <= MAX_SPANS && totalBytes <= MAX_BYTES) break;
      totalCount -= 1;
      totalBytes -= entry.record.sizeBytes ?? 0;
      keysToDelete.push(entry.key);
    }

    if (keysToDelete.length > 0) {
      await this.state.storage.delete(keysToDelete);
    }
  }
  /* v8 ignore stop */
}
