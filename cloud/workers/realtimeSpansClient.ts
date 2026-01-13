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
  Effect.tryPromise({
    try: async () => {
      const response = await stub.fetch(buildUrl(path), init);
      if (!response.ok) {
        throw new Error(
          `RecentSpansDurableObject request failed: ${response.status}`,
        );
      }
      return (await response.json()) as T;
    },
    catch: (error) =>
      new Error(
        `RecentSpansDurableObject request failed: ${error instanceof Error ? error.message : String(error)}`,
      ),
  });

const fetchNoContent = (
  stub: DurableObjectStub,
  path: string,
  init: CfRequestInit,
): Effect.Effect<void, Error> =>
  Effect.tryPromise({
    try: async () => {
      const response = await stub.fetch(buildUrl(path), init);
      if (!response.ok) {
        throw new Error(
          `RecentSpansDurableObject request failed: ${response.status}`,
        );
      }
    },
    catch: (error) =>
      new Error(
        `RecentSpansDurableObject request failed: ${error instanceof Error ? error.message : String(error)}`,
      ),
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
    existsSpan: (input: RealtimeSpanExistsInput) => {
      const stub = getStub(namespace, input.environmentId);
      return fetchJson<{ exists: boolean }>(stub, "/exists", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(input),
      }).pipe(Effect.map((result) => result.exists));
    },
  });
