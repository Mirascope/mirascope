/**
 * @fileoverview Durable Object client for realtime span access.
 *
 * Provides an Effect-native layer that targets the RecentSpansDurableObject
 * for realtime search, trace detail, and span existence checks.
 */

import { Effect, Layer } from "effect";
import type {
  DurableObjectNamespace,
  DurableObjectStub,
  // Aliased to avoid conflict with global RequestInit type
  RequestInit as CfRequestInit,
} from "@cloudflare/workers-types";
import {
  RealtimeSpans,
  type RealtimeSpansUpsertRequest,
  type RealtimeSpanExistsInput,
} from "@/realtimeSpans";
import type {
  SpanSearchInput,
  SearchResponse,
  TraceDetailInput,
  TraceDetailResponse,
} from "@/clickhouse/search";

// =============================================================================
// Helpers
// =============================================================================

const BASE_URL = "https://recent-spans";

const buildUrl = (path: string): string => new URL(path, BASE_URL).toString();

const getStub = (namespace: DurableObjectNamespace, environmentId: string) =>
  namespace.get(namespace.idFromName(environmentId));

const fetchJson = <T>(
  stub: DurableObjectStub,
  path: string,
  init: CfRequestInit,
): Effect.Effect<T, Error> =>
  Effect.gen(function* () {
    const response = yield* Effect.tryPromise({
      try: () => stub.fetch(buildUrl(path), init),
      catch: (error) =>
        new Error(
          `RecentSpansDurableObject request failed: ${error instanceof Error ? error.message : String(error)}`,
        ),
    });

    if (!response.ok) {
      return yield* Effect.fail(
        new Error(
          `RecentSpansDurableObject request failed: ${response.status}`,
        ),
      );
    }

    return (yield* Effect.tryPromise({
      try: () => response.json() as Promise<T>,
      catch: (error) =>
        new Error(
          `RecentSpansDurableObject JSON parse failed: ${error instanceof Error ? error.message : String(error)}`,
        ),
    })) as T;
  });

const fetchNoContent = (
  stub: DurableObjectStub,
  path: string,
  init: CfRequestInit,
): Effect.Effect<void, Error> =>
  Effect.gen(function* () {
    const response = yield* Effect.tryPromise({
      try: () => stub.fetch(buildUrl(path), init),
      catch: (error) =>
        new Error(
          `RecentSpansDurableObject request failed: ${error instanceof Error ? error.message : String(error)}`,
        ),
    });

    if (!response.ok) {
      return yield* Effect.fail(
        new Error(
          `RecentSpansDurableObject request failed: ${response.status}`,
        ),
      );
    }
  });

// =============================================================================
// Layer
// =============================================================================

export const RealtimeSpansLive = (namespace: DurableObjectNamespace) =>
  Layer.succeed(RealtimeSpans, {
    upsert: (request: RealtimeSpansUpsertRequest) => {
      const stub = getStub(namespace, request.environmentId);
      return fetchNoContent(stub, "/upsert", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(request),
      });
    },
    search: (input: SpanSearchInput) => {
      const stub = getStub(namespace, input.environmentId);
      return fetchJson<SearchResponse>(stub, "/search", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(input),
      });
    },
    getTraceDetail: (input: TraceDetailInput) => {
      const stub = getStub(namespace, input.environmentId);
      const traceId = encodeURIComponent(input.traceId);
      return fetchJson<TraceDetailResponse>(stub, `/trace/${traceId}`, {
        method: "GET",
      });
    },
    exists: (input: RealtimeSpanExistsInput) => {
      const stub = getStub(namespace, input.environmentId);
      return fetchJson<{ exists: boolean }>(stub, "/exists", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(input),
      }).pipe(Effect.map((result) => result.exists));
    },
  });
