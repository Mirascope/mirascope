/**
 * @fileoverview Cloudflare Queue Consumer for span ingestion.
 *
 * Processes OTLP spans asynchronously, writing to ClickHouse (source of truth)
 * and updating the realtime spans cache (Durable Object). ClickHouse insert is
 * prioritized; DurableObject upsert is best-effort and failures are logged but
 * don't block the ingestion. Failed ClickHouse inserts are retried via the
 * queue mechanism.
 *
 * ## Design Notes
 *
 * **Span lifecycle**: The current implementation processes completed spans only.
 * Each span received has both start and end times populated. The OTLP SDK batches
 * and sends spans after they end, so we don't need to handle pending→final updates.
 *
 * **Durable Object contract**: The DurableObject cache accepts partial span updates
 * and merges them with existing records. This enables future pending→final UI where
 * spans can be displayed in-progress and updated when they complete. The queue
 * currently sends completed spans only, but the DurableObject layer is designed to handle
 * incremental updates without data loss.
 *
 * **Batching**: Messages are processed individually to ensure proper retry handling.
 * ClickHouse batching happens at the SDK level (buffered inserts). If throughput
 * becomes an issue, we can optimize by batching multiple messages into a single
 * ClickHouse insert within this consumer.
 */

import { Context, Effect, Layer } from "effect";
import type {
  DurableObjectNamespace,
  MessageBatch,
} from "@cloudflare/workers-types";
import { ClickHouse } from "@/db/clickhouse/client";
import { transformSpanForClickHouse } from "@/db/clickhouse/transform";
import {
  SettingsService,
  getSettingsFromEnvironment,
  type CloudflareEnvironment,
} from "@/settings";
import { RealtimeSpans } from "@/workers/realtimeSpans";
import type { CompletedSpansBatchRequest } from "@/db/clickhouse/types";

// =============================================================================
// Types
// =============================================================================

/**
 * Message payload for the spans ingest queue.
 *
 * **Completed spans only**: This message type guarantees all spans have
 * both startTimeUnixNano and endTimeUnixNano set. The OTLP SDK batches
 * and sends spans after they end.
 *
 * The Durable Object cache accepts partial SpansBatchRequest for future
 * pending→final span UI. This queue, however, only receives completed
 * spans and uses the stricter CompletedSpansBatchRequest type.
 */
export type SpansIngestMessage = CompletedSpansBatchRequest;

// =============================================================================
// Queue Service
// =============================================================================

/**
 * Spans ingest queue service.
 *
 * Provides Effect-native access to the Cloudflare Queue binding for
 * enqueueing span ingestion messages.
 */
export class SpansIngestQueue extends Context.Tag("SpansIngestQueue")<
  SpansIngestQueue,
  { readonly send: (message: SpansIngestMessage) => Effect.Effect<void, Error> }
>() {
  /**
   * Creates a live implementation of the SpansIngestQueue service.
   *
   * @param queue - Cloudflare Queue binding from environment
   */
  /* v8 ignore start - Cloudflare Worker binding, covered by integration tests */
  static Live(queue: { send: (message: SpansIngestMessage) => Promise<void> }) {
    return Layer.succeed(
      SpansIngestQueue,
      SpansIngestQueue.of({
        send: (message) =>
          Effect.tryPromise({
            try: () => queue.send(message),
            catch: (error) =>
              new Error(
                `Failed to enqueue spans: ${error instanceof Error ? error.message : String(error)}`,
              ),
          }),
      }),
    );
  }
  /* v8 ignore stop */
}

// =============================================================================
// Global Layer
// =============================================================================

/**
 * Global spans ingest queue layer.
 *
 * Initialized by server-entry.ts when the Cloudflare binding is available.
 * Route handlers can import this layer to access the queue service.
 */
export let spansIngestQueueLayer: Layer.Layer<SpansIngestQueue> = Layer.succeed(
  SpansIngestQueue,
  {
    send: () => Effect.fail(new Error("SpansIngestQueue not initialized")),
  },
);

/**
 * Sets the global spans ingest queue layer.
 *
 * Called by server-entry.ts to initialize the layer with the Cloudflare binding.
 */
export const setSpansIngestQueueLayer = (
  layer: Layer.Layer<SpansIngestQueue>,
): void => {
  spansIngestQueueLayer = layer;
};

// =============================================================================
// Message Processing
// =============================================================================

/**
 * Effect program to ingest a spans message.
 *
 * Writes to ClickHouse (source of truth) and updates the realtime cache
 * (DurableObject). DurableObject upsert is best-effort: failures are logged
 * but don't block ClickHouse insert. This ensures data durability even when
 * the DurableObject is temporarily unavailable.
 *
 * @param data - Span ingestion message data
 */
export const ingestSpansMessage = (
  data: SpansIngestMessage,
): Effect.Effect<void, Error, ClickHouse | RealtimeSpans> =>
  Effect.gen(function* () {
    const clickhouse = yield* ClickHouse;
    const realtimeSpans = yield* RealtimeSpans;

    const clickhouseRows = data.spans.map((span) =>
      transformSpanForClickHouse({
        span,
        environmentId: data.environmentId,
        projectId: data.projectId,
        organizationId: data.organizationId,
        receivedAt: data.receivedAt,
        serviceName: data.serviceName,
        serviceVersion: data.serviceVersion,
        resourceAttributes: data.resourceAttributes,
      }),
    );

    yield* clickhouse.insert("spans_analytics", clickhouseRows);

    yield* realtimeSpans.upsert(data).pipe(
      /* v8 ignore start - Best-effort fallback, covered by integration tests */
      Effect.catchAll((error) => {
        console.warn(
          "[spanIngestQueue] DurableObject upsert failed (best-effort):",
          error,
        );
        return Effect.void;
      }),
      /* v8 ignore stop */
    );
  });

// =============================================================================
// Queue Handler
// =============================================================================

type SpanIngestEnvironment = CloudflareEnvironment & {
  readonly REALTIME_SPANS_DURABLE_OBJECT: DurableObjectNamespace;
};

/* v8 ignore start - Cloudflare Worker queue consumer, tested via integration */
export default {
  /**
   * Queue consumer handler for span ingestion messages.
   *
   * @param batch - Batch of messages from the queue
   * @param env - Cloudflare Workers environment bindings
   */
  async queue(
    batch: MessageBatch<SpansIngestMessage>,
    env: SpanIngestEnvironment,
  ): Promise<void> {
    if (!env.CLICKHOUSE_URL) {
      console.error("[spanIngestQueue] Missing CLICKHOUSE_URL binding");
      for (const message of batch.messages) {
        message.retry({ delaySeconds: 60 });
      }
      return;
    }

    const settingsLayer = Layer.succeed(
      SettingsService,
      getSettingsFromEnvironment(env),
    );

    const clickhouseLayer = ClickHouse.Default.pipe(
      Layer.provide(settingsLayer),
    );

    const realtimeLayer = RealtimeSpans.Live(env.REALTIME_SPANS_DURABLE_OBJECT);

    for (const message of batch.messages) {
      const program = ingestSpansMessage(message.body);

      await Effect.runPromise(
        program.pipe(
          Effect.provide(Layer.mergeAll(clickhouseLayer, realtimeLayer)),
          Effect.catchAll((error) => {
            console.error(`[spanIngestQueue] Error processing message:`, error);
            message.retry({ delaySeconds: 60 });
            return Effect.void;
          }),
        ),
      );
    }
  },
};
/* v8 ignore stop */
