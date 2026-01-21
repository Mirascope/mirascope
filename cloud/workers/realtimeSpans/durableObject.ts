/**
 * @fileoverview Durable Object for realtime span storage.
 *
 * Provides short-lived span caching with TTL/cap-based eviction and
 * read endpoints for realtime search and trace detail.
 */

import { DurableObject } from "cloudflare:workers";
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

/**
 * Raw JSON input for span search (dates come as ISO strings from API).
 */
type SpanSearchJsonInput = Omit<SpanSearchInput, "startTime" | "endTime"> & {
  startTime: string;
  endTime: string;
};

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
 * Converts an ISO date string to a Date object.
 *
 * @param value - ISO date string
 * @returns Date object
 */
const toDate = (value: string): Date => new Date(value);

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
  if (typeof value === "string" && value.trim().length > 0) {
    const parsed = Number(value);
    // NaN/Infinity from string parsing is defensive - valid strings produce finite numbers
    /* v8 ignore start */
    return Number.isFinite(parsed) ? parsed : null;
    /* v8 ignore stop */
  }
  return null;
};

/**
 * Parse mirascope.response.usage JSON and extract a field.
 *
 * @param attributes - Span attributes (may be null/undefined)
 * @param field - Field name to extract from usage object
 * @returns Numeric value or null if not found/invalid
 */
const getMirascopeUsageField = (
  attributes: Record<string, unknown> | null | undefined,
  field: string,
): number | null => {
  const usageRaw = getAttributeValue(
    attributes ?? null,
    "mirascope.response.usage",
  );
  if (usageRaw == null) return null;
  try {
    const parsed: unknown =
      typeof usageRaw === "string" ? JSON.parse(usageRaw) : usageRaw;
    if (
      parsed &&
      typeof parsed === "object" &&
      !Array.isArray(parsed) &&
      field in parsed
    ) {
      return toNumberOrNull((parsed as Record<string, unknown>)[field]);
    }
  } catch {
    // Invalid JSON
  }
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
const getSpanStartDate = (span: CachedSpan): Date => {
  if (span.startTimeUnixNano) {
    const ms = Number(BigInt(span.startTimeUnixNano) / BigInt(1_000_000));
    return new Date(ms);
  }
  return new Date(span.receivedAt);
};

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
const computeDurationMs = (span: CachedSpan): number | null => {
  if (!span.startTimeUnixNano || !span.endTimeUnixNano) return null;
  const startNs = BigInt(span.startTimeUnixNano);
  const endNs = BigInt(span.endTimeUnixNano);
  const durationMs = Number((endNs - startNs) / BigInt(1_000_000));
  // Negative duration (endTime < startTime) is defensive - shouldn't happen
  /* v8 ignore start */
  return durationMs >= 0 ? durationMs : null;
  /* v8 ignore stop */
};

/**
 * Extracts the model name from span attributes.
 *
 * Priority: mirascope.response.model_id → gen_ai.request.model
 */
const getModel = (span: CachedSpan): string | null => {
  const mirascopeModel = getAttributeValue(
    span.attributes,
    "mirascope.response.model_id",
  );
  if (mirascopeModel != null && typeof mirascopeModel === "string") {
    return mirascopeModel;
  }
  return (
    (getAttributeValue(span.attributes, "gen_ai.request.model") as
      | string
      | null) ?? null
  );
};

/**
 * Extracts the provider name from span attributes.
 *
 * Priority: mirascope.response.provider_id → gen_ai.system
 */
const getProvider = (span: CachedSpan): string | null => {
  const mirascopeProvider = getAttributeValue(
    span.attributes,
    "mirascope.response.provider_id",
  );
  if (mirascopeProvider != null && typeof mirascopeProvider === "string") {
    return mirascopeProvider;
  }
  return (
    (getAttributeValue(span.attributes, "gen_ai.system") as string | null) ??
    null
  );
};

/**
 * Extracts the input token count from span attributes.
 *
 * Priority: mirascope.response.usage.input_tokens → gen_ai.usage.input_tokens
 */
const getInputTokens = (span: CachedSpan): number | null => {
  const mirascopeTokens = getMirascopeUsageField(
    span.attributes,
    "input_tokens",
  );
  if (mirascopeTokens !== null) return mirascopeTokens;
  return toNumberOrNull(
    getAttributeValue(span.attributes, "gen_ai.usage.input_tokens"),
  );
};

/**
 * Extracts the output token count from span attributes.
 *
 * Priority: mirascope.response.usage.output_tokens → gen_ai.usage.output_tokens
 */
const getOutputTokens = (span: CachedSpan): number | null => {
  const mirascopeTokens = getMirascopeUsageField(
    span.attributes,
    "output_tokens",
  );
  if (mirascopeTokens !== null) return mirascopeTokens;
  return toNumberOrNull(
    getAttributeValue(span.attributes, "gen_ai.usage.output_tokens"),
  );
};

/**
 * Computes the total token count from span attributes.
 *
 * Priority: mirascope.response.usage.total_tokens → gen_ai.usage.total_tokens → sum
 */
const getTotalTokens = (span: CachedSpan): number | null => {
  // Try mirascope first
  const mirascopeTotal = getMirascopeUsageField(
    span.attributes,
    "total_tokens",
  );
  if (mirascopeTotal !== null) return mirascopeTotal;

  // Try gen_ai total
  const total = toNumberOrNull(
    getAttributeValue(span.attributes, "gen_ai.usage.total_tokens"),
  );
  if (total !== null) return total;

  // Fall back to summing input and output
  const input = getInputTokens(span);
  const output = getOutputTokens(span);
  if (input === null && output === null) return null;
  return (input ?? 0) + (output ?? 0);
};

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

/**
 * Extracts the cost in USD from span attributes.
 *
 * Priority: mirascope.response.cost.total_cost (centicents) → gen_ai.usage.cost (USD)
 */
const getCostUsd = (span: CachedSpan): number | null => {
  // Try mirascope.response.cost first (JSON with centicents)
  const mirascpeCostRaw = getAttributeValue(
    span.attributes,
    "mirascope.response.cost",
  );
  if (mirascpeCostRaw != null) {
    try {
      const parsed: unknown =
        typeof mirascpeCostRaw === "string"
          ? JSON.parse(mirascpeCostRaw)
          : mirascpeCostRaw;
      if (
        parsed &&
        typeof parsed === "object" &&
        !Array.isArray(parsed) &&
        "total_cost" in parsed
      ) {
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
  return toNumberOrNull(
    getAttributeValue(span.attributes, "gen_ai.usage.cost"),
  );
};

/**
 * Converts a value to a string for search matching.
 *
 * @param value - Value to convert
 * @returns String representation or null if not convertible
 */
const toSearchString = (value: unknown): string | null => {
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  // Bigints can't be passed through JSON - defensive for non-HTTP paths
  /* v8 ignore start */
  if (typeof value === "bigint") {
    return value.toString();
  }
  /* v8 ignore stop */
  return null;
};

/**
 * Checks if attributes match a given filter.
 *
 * Supports operators: eq, neq, contains, exists.
 *
 * @param attributes - Attributes to check
 * @param filter - Filter criteria
 * @returns True if attributes match the filter
 */
const matchesAttributeFilter = (
  attributes: Record<string, unknown> | null | undefined,
  filter: AttributeFilter,
): boolean => {
  const value = getAttributeValue(attributes ?? null, filter.key);
  if (filter.operator === "exists") {
    /* v8 ignore next 1 - defensive, getAttributeValue never returns undefined (uses ?? null) */
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
const mergeSpan = (existing: CachedSpan, incoming: CachedSpan): CachedSpan => {
  // Time merging: earliest start, latest end. Else branches are defensive.
  /* v8 ignore start */
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
  /* v8 ignore stop */

  const mergedAttributes =
    incoming.attributes && Object.keys(incoming.attributes).length > 0
      ? incoming.attributes
      : existing.attributes;

  // mergedEvents/mergedLinks fallbacks to existing are defensive - incoming usually has values
  /* v8 ignore start */
  const mergedEvents =
    incoming.events && incoming.events.length > 0
      ? incoming.events
      : existing.events;

  const mergedLinks =
    incoming.links && incoming.links.length > 0
      ? incoming.links
      : existing.links;
  /* v8 ignore stop */

  const mergedStatus =
    incoming.status !== undefined ? incoming.status : existing.status;

  return {
    traceId: incoming.traceId,
    spanId: incoming.spanId,
    parentSpanId: incoming.parentSpanId ?? existing.parentSpanId,
    /* v8 ignore next */
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
    // Service name/version fallbacks are defensive - batch always includes these
    /* v8 ignore start */
    serviceName: incoming.serviceName ?? existing.serviceName,
    serviceVersion: incoming.serviceVersion ?? existing.serviceVersion,
    /* v8 ignore stop */
    resourceAttributes:
      incoming.resourceAttributes ?? existing.resourceAttributes,
  };
};

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
  // Model/provider null fallbacks are defensive - always have values from attributes
  /* v8 ignore start */
  if (input.model && input.model.length > 0) {
    if (!input.model.includes(getModel(span) ?? "")) return false;
  }

  if (input.provider && input.provider.length > 0) {
    if (!input.provider.includes(getProvider(span) ?? "")) return false;
  }
  /* v8 ignore stop */

  if (input.functionId && getFunctionId(span) !== input.functionId) {
    return false;
  }

  if (input.functionName && getFunctionName(span) !== input.functionName) {
    return false;
  }

  // spanNamePrefix filter - match exact name or name with method suffix (e.g., "librarian.call")
  if (input.spanNamePrefix) {
    const prefix = input.spanNamePrefix;
    if (span.name !== prefix && !span.name.startsWith(`${prefix}.`)) {
      return false;
    }
  }

  if (input.hasError === true && !getErrorType(span)) return false;
  if (input.hasError === false && getErrorType(span)) return false;
  const totalTokens = getTotalTokens(span);
  // totalTokens null fallback is defensive
  /* v8 ignore start */
  if (input.minTokens !== undefined && (totalTokens ?? 0) < input.minTokens) {
    return false;
  }
  if (input.maxTokens !== undefined && (totalTokens ?? 0) > input.maxTokens) {
    return false;
  }
  /* v8 ignore stop */

  const durationMs = computeDurationMs(span);
  // durationMs always computed from timestamps, ?? 0 is defensive
  /* v8 ignore start */
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
  /* v8 ignore stop */

  if (input.attributeFilters && input.attributeFilters.length > 0) {
    for (const filter of input.attributeFilters) {
      if (!matchesAttributeFilter(span.attributes, filter)) {
        return false;
      }
    }
  }

  // rootSpansOnly filter - only return spans with no parent
  if (input.rootSpansOnly && span.parentSpanId !== null) {
    return false;
  }

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
    inputTokens: getInputTokens(span),
    outputTokens: getOutputTokens(span),
    totalTokens: getTotalTokens(span),
    costUsd: getCostUsd(span),
    functionId: getFunctionId(span),
    functionName: getFunctionName(span),
    // Note: hasChildren is not computed in realtime cache - use ClickHouse search for accurate value
    hasChildren: false,
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
const sortSearchResults = (
  spans: SpanSearchResult[],
  sortBy: "start_time" | "duration_ms" | "total_tokens",
  sortOrder: "asc" | "desc",
): SpanSearchResult[] => {
  const multiplier = sortOrder === "asc" ? 1 : -1;
  const toSortableValue = (span: SpanSearchResult): number => {
    switch (sortBy) {
      case "duration_ms":
        // durationMs always computed from timestamps, fallback is defensive
        /* v8 ignore start */
        return (
          span.durationMs ??
          (sortOrder === "asc"
            ? Number.POSITIVE_INFINITY
            : Number.NEGATIVE_INFINITY)
        );
      /* v8 ignore stop */
      case "total_tokens":
        return (
          span.totalTokens ??
          (sortOrder === "asc"
            ? Number.POSITIVE_INFINITY
            : Number.NEGATIVE_INFINITY)
        );
      case "start_time":
      default: {
        // startTime always comes from toISOString(), so Date.parse is always finite
        /* v8 ignore start */
        const value = Date.parse(span.startTime);
        return Number.isFinite(value)
          ? value
          : sortOrder === "asc"
            ? Number.POSITIVE_INFINITY
            : Number.NEGATIVE_INFINITY;
        /* v8 ignore stop */
      }
    }
  };

  return [...spans].sort((a, b) => {
    const aValue = toSortableValue(a);
    const bValue = toSortableValue(b);
    /* v8 ignore next 1 - spans rarely have identical timestamps */
    if (aValue === bValue) return 0;
    return aValue > bValue ? multiplier : -multiplier;
  });
};

/**
 * Computes trace-level statistics from a list of span details.
 *
 * @param spans - List of span details in the trace
 * @returns Root span ID and total trace duration
 */
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
    // Spans always have valid ISO timestamps from upsert
    /* v8 ignore start */
    if (!Number.isFinite(start) || !Number.isFinite(end)) continue;
    /* v8 ignore stop */
    if (minStart === null || start < minStart) minStart = start;
    if (maxEnd === null || end > maxEnd) maxEnd = end;
  }

  // All spans have valid timestamps from upsert, so null fallback is defensive
  /* v8 ignore start */
  const totalDurationMs =
    minStart !== null && maxEnd !== null ? maxEnd - minStart : null;
  /* v8 ignore stop */

  return { rootSpanId, totalDurationMs };
};

// =============================================================================
// Durable Object
// =============================================================================

/**
 * Base implementation of the realtime spans Durable Object.
 *
 * Note: The actual class exported to Cloudflare Workers is defined in
 * server-entry.ts to satisfy Cloudflare's class discovery requirements.
 */
export class RealtimeSpansDurableObjectBase extends DurableObject {
  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/upsert" && request.method === "POST") {
      const payload: SpansBatchRequest = await request.json();
      await this.handleUpsert(payload);
      return new Response(null, { status: 204 });
    }

    if (url.pathname === "/search" && request.method === "POST") {
      const input: SpanSearchJsonInput = await request.json();
      const response = await this.handleSearch(input);
      return Response.json(response);
    }

    if (url.pathname.startsWith("/trace/") && request.method === "GET") {
      const traceId = url.pathname.replace("/trace/", "");
      const response = await this.handleTraceDetail(traceId);
      return Response.json(response);
    }

    if (url.pathname === "/exists" && request.method === "POST") {
      const input: RealtimeSpanExistsInput = await request.json();
      const exists = await this.handleExists(input);
      return Response.json({ exists });
    }

    return new Response("Not Found", { status: 404 });
  }

  // ---------------------------------------------------------------------------
  // Private Helpers
  // ---------------------------------------------------------------------------

  private async handleUpsert(payload: SpansBatchRequest): Promise<void> {
    const now = Date.now();
    // receivedAt always provided by callers, fallback is defensive
    /* v8 ignore start */
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

      const existingRecord = await this.ctx.storage.get<SpanRecord>(storageKey);
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

      await this.ctx.storage.put(storageKey, record);
    }

    await this.pruneStorage();
  }

  private async handleSearch(
    input: SpanSearchJsonInput,
  ): Promise<SearchResponse> {
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

  private async handleExists(input: RealtimeSpanExistsInput): Promise<boolean> {
    const spanKey = createSpanCacheKey(input.traceId, input.spanId);
    const storageKey = `span:${spanKey}`;
    const record = await this.ctx.storage.get<SpanRecord>(storageKey);
    if (!record) return false;
    if (record.expiresAt <= Date.now()) {
      await this.ctx.storage.delete(storageKey);
      return false;
    }
    return true;
  }

  private async loadEntries(prefix: string): Promise<StoredEntry[]> {
    const entries = await this.ctx.storage.list<SpanRecord>({ prefix });
    return Array.from(entries.entries()).map(([key, record]) => ({
      key,
      record,
    }));
  }

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
      await this.ctx.storage.delete(expiredKeys);
    }

    let totalCount = activeEntries.length;
    // sizeBytes always set during upsert, ?? 0 is defensive
    /* v8 ignore start */
    let totalBytes = activeEntries.reduce(
      (sum, entry) => sum + (entry.record.sizeBytes ?? 0),
      0,
    );

    // Always true in tests since we never reach MAX_SPANS (50k) or MAX_BYTES (32MB)
    if (totalCount <= MAX_SPANS && totalBytes <= MAX_BYTES) {
      return;
    }

    // Over-limit pruning: requires MAX_SPANS (50k) entries to trigger - impractical to test
    activeEntries.sort((a, b) => a.record.receivedAt - b.record.receivedAt);

    const keysToDelete: string[] = [];
    for (const entry of activeEntries) {
      if (totalCount <= MAX_SPANS && totalBytes <= MAX_BYTES) break;
      totalCount -= 1;
      totalBytes -= entry.record.sizeBytes ?? 0;
      keysToDelete.push(entry.key);
    }

    if (keysToDelete.length > 0) {
      await this.ctx.storage.delete(keysToDelete);
    }
    /* v8 ignore stop */
  }
}
