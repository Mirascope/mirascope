/**
 * @fileoverview Effect interface and types for realtime span access.
 *
 * Provides a shared contract for Durable Object backed span caching used
 * by ingestion and realtime search paths.
 *
 * ## Pending → Final Span Update Semantics
 *
 * The Durable Object cache supports partial span updates to enable realtime
 * display of in-progress spans. When a span is upserted:
 *
 * - **Key**: `(traceId, spanId)` uniquely identifies a span.
 * - **Merge**: Incoming fields overwrite existing when non-null/undefined.
 *   Missing, null, or undefined fields preserve existing values.
 * - **Start time**: Preserve the earliest `startTimeUnixNano` if both exist.
 * - **End time**: Accept the largest (latest timestamp) `endTimeUnixNano`;
 *   if incoming is null/undefined, keep existing.
 * - **Attributes/Events/Links**: If incoming field is provided and non-empty,
 *   replace existing; otherwise keep existing.
 * - **Status/Counts**: Overwrite when provided, preserve otherwise.
 * - **TTL**: Update `receivedAt` and `expiresAt` on each upsert to extend
 *   cache lifetime for active spans.
 *
 * ClickHouse remains the source of truth. The Durable Object is a best-effort
 * cache for realtime UI display.
 */

import type {
  DurableObjectNamespace,
  DurableObjectStub,
  RequestInit,
} from "@cloudflare/workers-types";

import { Context, Effect, Layer } from "effect";

import type {
  SpanSearchInput,
  SearchResponse,
  TraceDetailInput,
  TraceDetailResponse,
} from "@/db/clickhouse/search";
import type { SpansBatchRequest } from "@/db/clickhouse/types";

// =============================================================================
// Types
// =============================================================================

export type RealtimeSpanExistsInput = {
  environmentId: string;
  traceId: string;
  spanId: string;
};

// =============================================================================
// Helpers
// =============================================================================

export const createSpanCacheKey = (traceId: string, spanId: string): string =>
  `${traceId}:${spanId}`;

// =============================================================================
// Service
// =============================================================================

const BASE_URL = "https://realtime-spans";

const buildUrl = (path: string): string => new URL(path, BASE_URL).toString();

const getStub = (namespace: DurableObjectNamespace, environmentId: string) =>
  namespace.get(namespace.idFromName(environmentId));

const fetchJson = <T>(
  stub: DurableObjectStub,
  path: string,
  init: RequestInit,
): Effect.Effect<T, Error> =>
  Effect.try({
    try: () => {
      // Wrap in try-catch to handle any synchronous errors from stub operations
      const fetchPromise = stub.fetch(buildUrl(path), init);
      return fetchPromise;
    },
    catch: (error) =>
      new Error(
        `RealtimeSpansDurableObject stub error: ${error instanceof Error ? error.message : String(error)}`,
      ),
  }).pipe(
    Effect.flatMap((fetchPromise) =>
      Effect.tryPromise({
        try: () => fetchPromise,
        catch: (error) =>
          new Error(
            `RealtimeSpansDurableObject request failed: ${error instanceof Error ? error.message : String(error)}`,
          ),
      }),
    ),
    Effect.flatMap((response) => {
      if (!response.ok) {
        return Effect.fail(
          new Error(
            `RealtimeSpansDurableObject request failed: ${response.status}`,
          ),
        );
      }
      return Effect.tryPromise({
        try: (): Promise<T> => response.json(),
        catch: (error) =>
          new Error(
            `RealtimeSpansDurableObject JSON parse failed: ${error instanceof Error ? error.message : String(error)}`,
          ),
      });
    }),
  );

const fetchNoContent = (
  stub: DurableObjectStub,
  path: string,
  init: RequestInit,
): Effect.Effect<void, Error> =>
  Effect.try({
    try: () => {
      // Wrap in try-catch to handle any synchronous errors from stub operations
      const fetchPromise = stub.fetch(buildUrl(path), init);
      return fetchPromise;
    },
    catch: (error) =>
      new Error(
        `RealtimeSpansDurableObject stub error: ${error instanceof Error ? error.message : String(error)}`,
      ),
  }).pipe(
    Effect.flatMap((fetchPromise) =>
      Effect.tryPromise({
        try: () => fetchPromise,
        catch: (error) =>
          new Error(
            `RealtimeSpansDurableObject request failed: ${error instanceof Error ? error.message : String(error)}`,
          ),
      }),
    ),
    Effect.flatMap((response) => {
      if (!response.ok) {
        return Effect.fail(
          new Error(
            `RealtimeSpansDurableObject request failed: ${response.status}`,
          ),
        );
      }
      return Effect.void;
    }),
  );

/**
 * RealtimeSpans service interface.
 *
 * Provides Effect-native access to the realtime span cache backed by a
 * Durable Object. Use `RealtimeSpans.Live(namespace)` to create a layer
 * that implements this service.
 */
export class RealtimeSpans extends Context.Tag("RealtimeSpans")<
  RealtimeSpans,
  {
    readonly upsert: (request: SpansBatchRequest) => Effect.Effect<void, Error>;
    readonly search: (
      input: SpanSearchInput,
    ) => Effect.Effect<SearchResponse, Error>;
    readonly getTraceDetail: (
      input: TraceDetailInput,
    ) => Effect.Effect<TraceDetailResponse, Error>;
    readonly exists: (
      input: RealtimeSpanExistsInput,
    ) => Effect.Effect<boolean, Error>;
  }
>() {
  /**
   * Creates a live implementation of the RealtimeSpans service.
   *
   * @param namespace - Cloudflare Durable Object namespace binding
   */
  static Live(namespace: DurableObjectNamespace): Layer.Layer<RealtimeSpans> {
    // Helper to safely get stub and handle any errors
    const safeGetStub = (environmentId: string) =>
      Effect.try({
        try: () => getStub(namespace, environmentId),
        catch: (error) =>
          new Error(
            `Failed to get Durable Object stub: ${error instanceof Error ? error.message : String(error)}`,
          ),
      });

    return Layer.succeed(RealtimeSpans, {
      upsert: (request: SpansBatchRequest) =>
        safeGetStub(request.environmentId).pipe(
          Effect.flatMap((stub) =>
            fetchNoContent(stub, "/upsert", {
              method: "POST",
              headers: { "content-type": "application/json" },
              body: JSON.stringify(request),
            }),
          ),
        ),
      search: (input: SpanSearchInput) =>
        safeGetStub(input.environmentId).pipe(
          Effect.flatMap((stub) =>
            fetchJson<SearchResponse>(stub, "/search", {
              method: "POST",
              headers: { "content-type": "application/json" },
              body: JSON.stringify(input),
            }),
          ),
        ),
      getTraceDetail: (input: TraceDetailInput) =>
        safeGetStub(input.environmentId).pipe(
          Effect.flatMap((stub) => {
            const traceId = encodeURIComponent(input.traceId);
            return fetchJson<TraceDetailResponse>(stub, `/trace/${traceId}`, {
              method: "GET",
            });
          }),
        ),
      exists: (input: RealtimeSpanExistsInput) =>
        safeGetStub(input.environmentId).pipe(
          Effect.flatMap((stub) =>
            fetchJson<{ exists: boolean }>(stub, "/exists", {
              method: "POST",
              headers: { "content-type": "application/json" },
              body: JSON.stringify(input),
            }),
          ),
          Effect.map((result) => result.exists),
        ),
    });
  }
}

// =============================================================================
// Global Layer
// =============================================================================

/**
 * Global realtime spans layer.
 *
 * Initialized by server-entry.ts when the Cloudflare binding is available.
 * Route handlers can import this layer to access the realtime spans service.
 */
export let realtimeSpansLayer: Layer.Layer<RealtimeSpans> = Layer.succeed(
  RealtimeSpans,
  {
    upsert: () => Effect.fail(new Error("RealtimeSpans not initialized")),
    search: () => Effect.fail(new Error("RealtimeSpans not initialized")),
    getTraceDetail: () =>
      Effect.fail(new Error("RealtimeSpans not initialized")),
    exists: () => Effect.fail(new Error("RealtimeSpans not initialized")),
  },
);

/**
 * Sets the global realtime spans layer.
 *
 * Called by server-entry.ts to initialize the layer with the Cloudflare binding.
 */
export const setRealtimeSpansLayer = (
  layer: Layer.Layer<RealtimeSpans>,
): void => {
  realtimeSpansLayer = layer;
};
