/**
 * @fileoverview Durable Object for realtime span storage.
 *
 * Provides short-lived span caching with TTL/cap-based eviction and
 * read endpoints for realtime search and trace detail.
 */

import type { DurableObjectState } from "@cloudflare/workers-types";
import type {
  RealtimeSpanInput,
  RealtimeSpansUpsertRequest,
  RealtimeSpanExistsInput,
} from "@/realtimeSpans";
import { createSpanCacheKey } from "@/realtimeSpans";
import type {
  SearchResponse,
  SpanSearchInput,
  SpanSearchResult,
  SpanDetail,
  TraceDetailResponse,
  AttributeFilter,
} from "@/clickhouse/search";

// =============================================================================
// Constants
// =============================================================================

const TTL_MS = 10 * 60 * 1000;
const MAX_SPANS = 50_000;
const MAX_BYTES = 32 * 1024 * 1024;

// =============================================================================
// Types
// =============================================================================

type CachedSpan = RealtimeSpanInput & {
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

const toDate = (value: Date | string): Date =>
  value instanceof Date ? value : new Date(value);

const estimateSizeBytes = (value: unknown): number =>
  new TextEncoder().encode(JSON.stringify(value)).length;

const getAttributeValue = (
  attributes: Record<string, unknown> | null | undefined,
  key: string,
): unknown => {
  if (!attributes) return null;
  return attributes[key] ?? null;
};

const toNumberOrNull = (value: unknown): number | null => {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim().length > 0) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
};

const getSpanStartDate = (span: CachedSpan): Date => {
  if (span.startTimeUnixNano) {
    const ms = Number(BigInt(span.startTimeUnixNano) / BigInt(1_000_000));
    return new Date(ms);
  }
  return new Date(span.receivedAt);
};

const getSpanEndDate = (span: CachedSpan): Date | null => {
  if (!span.endTimeUnixNano) return null;
  const ms = Number(BigInt(span.endTimeUnixNano) / BigInt(1_000_000));
  return new Date(ms);
};

const computeDurationMs = (span: CachedSpan): number | null => {
  if (!span.startTimeUnixNano || !span.endTimeUnixNano) return null;
  const startNs = BigInt(span.startTimeUnixNano);
  const endNs = BigInt(span.endTimeUnixNano);
  const durationMs = Number((endNs - startNs) / BigInt(1_000_000));
  return durationMs >= 0 ? durationMs : null;
};

const getModel = (span: CachedSpan): string | null =>
  (getAttributeValue(span.attributes, "gen_ai.request.model") as
    | string
    | null) ?? null;

const getProvider = (span: CachedSpan): string | null =>
  (getAttributeValue(span.attributes, "gen_ai.system") as string | null) ??
  null;

const getInputTokens = (span: CachedSpan): number | null =>
  toNumberOrNull(
    getAttributeValue(span.attributes, "gen_ai.usage.input_tokens"),
  );

const getOutputTokens = (span: CachedSpan): number | null =>
  toNumberOrNull(
    getAttributeValue(span.attributes, "gen_ai.usage.output_tokens"),
  );

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

const getFunctionId = (span: CachedSpan): string | null =>
  (getAttributeValue(span.attributes, "mirascope.function_id") as
    | string
    | null) ?? null;

const getFunctionName = (span: CachedSpan): string | null =>
  (getAttributeValue(span.attributes, "mirascope.function_name") as
    | string
    | null) ?? null;

const getFunctionVersion = (span: CachedSpan): string | null =>
  (getAttributeValue(span.attributes, "mirascope.function_version") as
    | string
    | null) ?? null;

const getErrorType = (span: CachedSpan): string | null =>
  (getAttributeValue(span.attributes, "exception.type") as string | null) ??
  null;

const getErrorMessage = (span: CachedSpan): string | null =>
  (getAttributeValue(span.attributes, "exception.message") as string | null) ??
  null;

const getCostUsd = (span: CachedSpan): number | null =>
  toNumberOrNull(getAttributeValue(span.attributes, "gen_ai.usage.cost"));

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

const matchesQueryTokens = (name: string, query: string): boolean => {
  const tokens = query
    .trim()
    .toLowerCase()
    .split(/[^a-z0-9]+/g)
    .filter((token) => token.length > 0);
  const lowerName = name.toLowerCase();
  return tokens.every((token) => lowerName.includes(token));
};

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

  return true;
};

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

// =============================================================================
// Durable Object
// =============================================================================

export class RecentSpansDO {
  private readonly state: DurableObjectState;

  constructor(state: DurableObjectState) {
    this.state = state;
  }

  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/upsert" && request.method === "POST") {
      const payload: RealtimeSpansUpsertRequest = await request.json();
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

    if (url.pathname === "/exists" && request.method === "POST") {
      const input: RealtimeSpanExistsInput = await request.json();
      const exists = await this.handleExists(input);
      return Response.json({ exists });
    }

    return new Response("Not Found", { status: 404 });
  }

  private async handleUpsert(
    payload: RealtimeSpansUpsertRequest,
  ): Promise<void> {
    const now = Date.now();
    const receivedAt = payload.receivedAt ?? now;
    const expiresAt = receivedAt + TTL_MS;
    const entries: Array<Promise<void>> = [];

    for (const span of payload.spans) {
      const cachedSpan: CachedSpan = {
        ...span,
        receivedAt,
        environmentId: payload.environmentId,
        projectId: payload.projectId,
        organizationId: payload.organizationId,
        serviceName: payload.serviceName,
        serviceVersion: payload.serviceVersion,
        resourceAttributes: payload.resourceAttributes,
      };
      const sizeBytes = estimateSizeBytes(cachedSpan);
      const record: SpanRecord = {
        span: cachedSpan,
        receivedAt,
        expiresAt,
        sizeBytes,
      };
      const spanKey = createSpanCacheKey(span.traceId, span.spanId);
      const storageKey = `span:${spanKey}`;
      entries.push(this.state.storage.put(storageKey, record));
    }

    await Promise.all(entries);
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

  private async loadEntries(prefix: string): Promise<StoredEntry[]> {
    const entries = await this.state.storage.list<SpanRecord>({ prefix });
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
}
