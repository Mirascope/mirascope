/**
 * @fileoverview Effect interface and types for realtime span access.
 *
 * Provides a shared contract for Durable Object backed span caching used
 * by ingestion and realtime search paths.
 */

import { Context, Effect } from "effect";
import type {
  SpanSearchInput,
  SearchResponse,
  TraceDetailInput,
  TraceDetailResponse,
} from "@/clickhouse/search";

// =============================================================================
// Types
// =============================================================================

export type RealtimeSpanStatus = {
  code?: number;
  message?: string;
};

export type RealtimeSpanInput = {
  traceId: string;
  spanId: string;
  parentSpanId?: string | null;
  name: string;
  kind?: number;
  startTimeUnixNano?: string;
  endTimeUnixNano?: string;
  attributes?: Record<string, unknown> | null;
  droppedAttributesCount?: number;
  events?: ReadonlyArray<unknown>;
  droppedEventsCount?: number;
  status?: RealtimeSpanStatus;
  links?: ReadonlyArray<unknown>;
  droppedLinksCount?: number;
};

export type RealtimeSpansUpsertRequest = {
  environmentId: string;
  projectId: string;
  organizationId: string;
  receivedAt: number;
  serviceName: string | null;
  serviceVersion: string | null;
  resourceAttributes: Record<string, unknown> | null;
  spans: RealtimeSpanInput[];
};

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

export class RealtimeSpans extends Context.Tag("RealtimeSpans")<
  RealtimeSpans,
  {
    readonly upsert: (
      request: RealtimeSpansUpsertRequest,
    ) => Effect.Effect<void, Error>;
    readonly search: (
      input: SpanSearchInput,
    ) => Effect.Effect<SearchResponse, Error>;
    readonly getTraceDetail: (
      input: TraceDetailInput,
    ) => Effect.Effect<TraceDetailResponse, Error>;
    readonly existsSpan: (
      input: RealtimeSpanExistsInput,
    ) => Effect.Effect<boolean, Error>;
  }
>() {}
