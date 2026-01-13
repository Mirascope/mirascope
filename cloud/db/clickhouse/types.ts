/**
 * @fileoverview Shared types for ClickHouse span analytics.
 *
 * These types define the canonical span structure used across ingestion,
 * transformation, and realtime caching layers. Workers and other consumers
 * should re-export these types rather than defining their own.
 */

// =============================================================================
// Span Types
// =============================================================================

/**
 * Status information for a span.
 */
export type SpanStatus = {
  code?: number;
  message?: string;
};

/**
 * Input type for a single span.
 *
 * This is the canonical span structure used for ingestion and transformation.
 * All fields except traceId, spanId, and name are optional to support
 * partial updates in the realtime cache.
 */
export type SpanInput = {
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
  status?: SpanStatus;
  links?: ReadonlyArray<unknown>;
  droppedLinksCount?: number;
};

/**
 * Completed span input with required start and end times.
 *
 * Used for ClickHouse ingestion where spans must be complete.
 * The OTLP SDK batches and sends spans after they end.
 */
export type CompletedSpanInput = SpanInput & {
  startTimeUnixNano: string;
  endTimeUnixNano: string;
};

// =============================================================================
// Batch Types
// =============================================================================

/**
 * Batch of spans with shared metadata.
 *
 * Used for both realtime cache upserts and ClickHouse ingestion.
 */
export type SpansBatchRequest = {
  environmentId: string;
  projectId: string;
  organizationId: string;
  receivedAt: number;
  serviceName: string | null;
  serviceVersion: string | null;
  resourceAttributes: Record<string, unknown> | null;
  spans: SpanInput[];
};

/**
 * Batch of completed spans for ClickHouse ingestion.
 *
 * This type guarantees all spans have both start and end times set.
 * The queue consumer only receives completed spans from the OTLP SDK.
 */
export type CompletedSpansBatchRequest = Omit<SpansBatchRequest, "spans"> & {
  spans: CompletedSpanInput[];
};
