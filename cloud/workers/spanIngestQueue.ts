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
import { ClickHouse } from "@/clickhouse/client";
import { transformSpanForClickHouse } from "@/clickhouse/transform";
import {
  SettingsService,
  getSettingsFromEnvironment,
  type CloudflareEnvironment,
} from "@/settings";
import {
  RealtimeSpans,
  type RealtimeSpansUpsertRequest,
} from "@/realtimeSpans";
import { RealtimeSpansLive } from "@/workers/realtimeSpansClient";

// =============================================================================
// Types
// =============================================================================

export type SpansIngestMessage = RealtimeSpansUpsertRequest;

// =============================================================================
// Queue Service
// =============================================================================

/**
 * Spans ingest queue service.
 *
 * Provides Effect-native access to the Cloudflare Queue binding for
 * enqueueing span ingestion messages.
 */
export class SpansIngestQueueService extends Context.Tag("SpansIngestQueue")<
  SpansIngestQueueService,
  { readonly send: (message: SpansIngestMessage) => Effect.Effect<void, Error> }
>() {
  /**
   * Creates a live implementation of the SpansIngestQueue service.
   *
   * @param queue - Cloudflare Queue binding from environment
   */
  static Live(queue: { send: (message: SpansIngestMessage) => Promise<void> }) {
    return Layer.succeed(
      SpansIngestQueueService,
      SpansIngestQueueService.of({
        send: (message) =>
          Effect.tryPromise({
            try: () => queue.send(message),
            catch: (error) =>
              new Error(
                `Failed to enqueue spans: ${error instanceof Error ? error.message : /* v8 ignore next 1 */ String(error)}`,
              ),
          }),
      }),
    );
  }
}

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
      Effect.catchAll((error) => {
        console.warn(
          "[spanIngestQueue] DurableObject upsert failed (best-effort):",
          error,
        );
        return Effect.void;
      }),
    );
  });

// =============================================================================
// Queue Handler
// =============================================================================

type SpanIngestEnvironment = CloudflareEnvironment & {
  readonly RECENT_SPANS_DURABLE_OBJECT?: DurableObjectNamespace;
};

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

    if (!env.RECENT_SPANS_DURABLE_OBJECT) {
      console.warn(
        "[spanIngestQueue] RECENT_SPANS_DURABLE_OBJECT not configured, skipping realtime cache",
      );
    }

    const settingsLayer = Layer.succeed(
      SettingsService,
      getSettingsFromEnvironment(env),
    );

    const clickhouseLayer = ClickHouse.Default.pipe(
      Layer.provide(settingsLayer),
    );

    /* v8 ignore start - no-op layer when DurableObject unavailable, covered by unit tests */
    const realtimeLayer = env.RECENT_SPANS_DURABLE_OBJECT
      ? RealtimeSpansLive(env.RECENT_SPANS_DURABLE_OBJECT)
      : Layer.succeed(RealtimeSpans, {
          upsert: () => Effect.void,
          search: () => Effect.fail(new Error("RealtimeSpans not configured")),
          getTraceDetail: () =>
            Effect.fail(new Error("RealtimeSpans not configured")),
          exists: () => Effect.fail(new Error("RealtimeSpans not configured")),
        });
    /* v8 ignore stop */

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
