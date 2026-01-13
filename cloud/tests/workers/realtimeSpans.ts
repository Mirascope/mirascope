/**
 * @fileoverview Test utilities for RealtimeSpans Durable Object.
 *
 * Provides mock implementations and factory functions for testing the
 * RealtimeSpansDurableObject in isolation.
 */

import type { DurableObjectState } from "@cloudflare/workers-types";

// =============================================================================
// Test Constants
// =============================================================================

/** Default environment ID for tests. */
export const DEFAULT_ENV_ID = "env-1";

/** Default project ID for tests. */
export const DEFAULT_PROJECT_ID = "proj-1";

/** Default organization ID for tests. */
export const DEFAULT_ORG_ID = "org-1";

/** Default service name for tests. */
export const DEFAULT_SERVICE_NAME = "service";

/** Default service version for tests. */
export const DEFAULT_SERVICE_VERSION = "1.0.0";

// =============================================================================
// Mock Storage
// =============================================================================

/**
 * In-memory mock implementation of Durable Object storage.
 *
 * Provides the minimal storage interface required by RealtimeSpansDurableObject:
 * - get: Retrieve a value by key
 * - put: Store a value by key
 * - delete: Remove one or more keys
 * - list: List entries with optional prefix filter
 */
export class MockStorage {
  private store = new Map<string, unknown>();

  /**
   * Retrieves a value from storage.
   */
  get<T>(key: string): Promise<T | undefined> {
    return Promise.resolve(this.store.get(key) as T | undefined);
  }

  /**
   * Stores a value in storage.
   */
  put<T>(key: string, value: T): Promise<void> {
    this.store.set(key, value);
    return Promise.resolve();
  }

  /**
   * Deletes one or more keys from storage.
   */
  delete(keys: string | string[]): Promise<void> {
    if (Array.isArray(keys)) {
      for (const key of keys) {
        this.store.delete(key);
      }
      return Promise.resolve();
    }
    this.store.delete(keys);
    return Promise.resolve();
  }

  /**
   * Lists entries with optional prefix filter.
   */
  list<T>(options?: { prefix?: string }): Promise<Map<string, T>> {
    if (!options?.prefix) {
      return Promise.resolve(new Map(this.store.entries()) as Map<string, T>);
    }
    const entries = Array.from(this.store.entries()).filter(([key]) =>
      key.startsWith(options.prefix ?? ""),
    );
    return Promise.resolve(new Map(entries) as Map<string, T>);
  }
}

/**
 * Parses JSON response body with type assertion.
 */
export const parseJson = async <T>(response: Response): Promise<T> =>
  (await response.json()) as T;

/**
 * Creates a mock DurableObjectState with in-memory storage.
 */
export const createState = (): DurableObjectState =>
  ({
    storage: new MockStorage(),
  }) as unknown as DurableObjectState;

// =============================================================================
// Time Helpers
// =============================================================================

/**
 * Converts milliseconds to nanoseconds as a string.
 *
 * @param ms - Milliseconds value
 * @returns Nanoseconds as string for span timestamps
 */
export const msToNano = (ms: number): string =>
  (BigInt(ms) * 1_000_000n).toString();

/**
 * Creates a time context for consistent timestamp generation in tests.
 *
 * @param baseMs - Base time in milliseconds (defaults to Date.now())
 * @returns Object with time helpers
 */
export const createTimeContext = (baseMs: number = Date.now()) => ({
  nowMs: baseMs,
  startNano: msToNano(baseMs),
  endNano: (offsetMs: number) => msToNano(baseMs + offsetMs),
  laterStartNano: (offsetMs: number) => msToNano(baseMs + offsetMs),
});

// =============================================================================
// Payload Factories
// =============================================================================

/** Options for creating a span batch payload. */
export type SpanBatchOptions = {
  environmentId?: string;
  projectId?: string;
  organizationId?: string;
  receivedAt?: number;
  serviceName?: string | null;
  serviceVersion?: string | null;
  resourceAttributes?: Record<string, unknown> | null;
  spans?: Array<Partial<SpanData>>;
};

/** Span data for test payloads. */
export type SpanData = {
  traceId: string;
  spanId: string;
  parentSpanId?: string | null;
  name: string;
  kind?: number;
  startTimeUnixNano?: string;
  endTimeUnixNano?: string;
  attributes?: Record<string, unknown>;
  status?: { code: number; message?: string };
  events?: Array<{ name: string }>;
  links?: Array<{ traceId: string }>;
  droppedAttributesCount?: number;
  droppedEventsCount?: number;
  droppedLinksCount?: number;
};

/**
 * Creates a default span batch payload for tests.
 *
 * @param options - Optional overrides
 * @returns Complete SpansBatchRequest-compatible payload
 */
export const createSpanBatch = (options: SpanBatchOptions = {}) => {
  const now = BigInt(Date.now());
  const start = now * 1_000_000n;
  const mid = start + 500_000_000n;
  const end = start + 1_000_000_000n;
  const end2 = start + 1_500_000_000n;

  const defaultSpans: SpanData[] = [
    {
      traceId: "trace-1",
      spanId: "span-1",
      parentSpanId: null,
      name: "alpha",
      kind: 1,
      startTimeUnixNano: start.toString(),
      endTimeUnixNano: end.toString(),
      attributes: { "gen_ai.request.model": "gpt-4" },
      status: { code: 1, message: "OK" },
      events: [{ name: "event-1" }],
      links: [{ traceId: "trace-2" }],
      droppedAttributesCount: 0,
      droppedEventsCount: 0,
      droppedLinksCount: 0,
    },
    {
      traceId: "trace-1",
      spanId: "span-2",
      parentSpanId: "span-1",
      name: "beta",
      kind: 1,
      startTimeUnixNano: mid.toString(),
      endTimeUnixNano: end2.toString(),
      attributes: { "gen_ai.request.model": "gpt-4" },
    },
  ];

  return {
    environmentId: options.environmentId ?? DEFAULT_ENV_ID,
    projectId: options.projectId ?? DEFAULT_PROJECT_ID,
    organizationId: options.organizationId ?? DEFAULT_ORG_ID,
    receivedAt: options.receivedAt ?? Date.now(),
    serviceName: options.serviceName ?? DEFAULT_SERVICE_NAME,
    serviceVersion: options.serviceVersion ?? DEFAULT_SERVICE_VERSION,
    resourceAttributes: options.resourceAttributes ?? { region: "us-east-1" },
    spans: options.spans ?? defaultSpans,
  };
};

/**
 * Creates a test payload for span upsert operations.
 *
 * @param overrides - Optional overrides for any payload fields
 * @returns A complete SpansBatchRequest-compatible payload
 * @deprecated Use createSpanBatch instead for better type safety
 */
export const createSpanPayload = (
  overrides?: Partial<Record<string, unknown>>,
) => {
  const now = BigInt(Date.now());
  const start = now * 1_000_000n;
  const mid = start + 500_000_000n;
  const end = start + 1_000_000_000n;
  const end2 = start + 1_500_000_000n;

  return {
    environmentId: DEFAULT_ENV_ID,
    projectId: DEFAULT_PROJECT_ID,
    organizationId: DEFAULT_ORG_ID,
    receivedAt: Date.now(),
    serviceName: DEFAULT_SERVICE_NAME,
    serviceVersion: DEFAULT_SERVICE_VERSION,
    resourceAttributes: { region: "us-east-1" },
    spans: [
      {
        traceId: "trace-1",
        spanId: "span-1",
        parentSpanId: null,
        name: "alpha",
        kind: 1,
        startTimeUnixNano: start.toString(),
        endTimeUnixNano: end.toString(),
        attributes: { "gen_ai.request.model": "gpt-4" },
        status: { code: 1, message: "OK" },
        events: [{ name: "event-1" }],
        links: [{ traceId: "trace-2" }],
        droppedAttributesCount: 0,
        droppedEventsCount: 0,
        droppedLinksCount: 0,
      },
      {
        traceId: "trace-1",
        spanId: "span-2",
        parentSpanId: "span-1",
        name: "beta",
        kind: 1,
        startTimeUnixNano: mid.toString(),
        endTimeUnixNano: end2.toString(),
        attributes: { "gen_ai.request.model": "gpt-4" },
      },
    ],
    ...overrides,
  };
};

// =============================================================================
// Request Helpers
// =============================================================================

const BASE_URL = "https://realtime-spans";

/**
 * Creates an upsert request for testing.
 *
 * @param payload - Span batch payload
 * @returns Request object
 */
export const createUpsertRequest = (
  payload: ReturnType<typeof createSpanBatch>,
) =>
  new Request(`${BASE_URL}/upsert`, {
    method: "POST",
    body: JSON.stringify(payload),
    headers: { "content-type": "application/json" },
  });

/**
 * Creates a search request for testing.
 *
 * @param input - Search input parameters
 * @returns Request object
 */
export const createSearchRequest = (input: {
  environmentId?: string;
  startTime?: string;
  endTime?: string;
  query?: string;
  sortBy?: "start_time" | "duration_ms" | "total_tokens";
  sortOrder?: "asc" | "desc";
}) => {
  const now = Date.now();
  return new Request(`${BASE_URL}/search`, {
    method: "POST",
    body: JSON.stringify({
      environmentId: input.environmentId ?? DEFAULT_ENV_ID,
      startTime: input.startTime ?? new Date(now - 60_000).toISOString(),
      endTime: input.endTime ?? new Date(now + 60_000).toISOString(),
      ...input,
    }),
    headers: { "content-type": "application/json" },
  });
};

/**
 * Creates a trace detail request for testing.
 *
 * @param traceId - Trace ID to retrieve
 * @returns Request object
 */
export const createTraceRequest = (traceId: string) =>
  new Request(`${BASE_URL}/trace/${traceId}`, { method: "GET" });

/**
 * Creates an exists check request for testing.
 *
 * @param input - Exists input parameters
 * @returns Request object
 */
export const createExistsRequest = (input: {
  environmentId?: string;
  traceId: string;
  spanId: string;
}) =>
  new Request(`${BASE_URL}/exists`, {
    method: "POST",
    body: JSON.stringify({
      environmentId: input.environmentId ?? DEFAULT_ENV_ID,
      traceId: input.traceId,
      spanId: input.spanId,
    }),
    headers: { "content-type": "application/json" },
  });
