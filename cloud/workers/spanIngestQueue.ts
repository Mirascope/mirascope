/**
 * @fileoverview Cloudflare Queue Consumer for span ingestion.
 *
 * Processes OTLP spans asynchronously, writing to ClickHouse (source of truth),
 * charging span metering, and updating the realtime spans cache (Durable Object).
 * ClickHouse insert is
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
 * **Metering**: Metering is executed after ClickHouse insert. Failures are logged
 * but do not trigger queue retries to avoid duplicate ClickHouse inserts.
 *
 * **Batching**: Messages are processed individually to ensure proper retry handling.
 * ClickHouse batching happens at the SDK level (buffered inserts). If throughput
 * becomes an issue, we can optimize by batching multiple messages into a single
 * ClickHouse insert within this consumer.
 */

import type {
  DurableObjectNamespace,
  MessageBatch,
} from "@cloudflare/workers-types";

import { eq } from "drizzle-orm";
import { Context, Effect, Layer } from "effect";

import type { CompletedSpansBatchRequest } from "@/db/clickhouse/types";
import type { BillingCronTriggerEnv } from "@/workers/config";

import { ClickHouse } from "@/db/clickhouse/client";
import { transformSpanForClickHouse } from "@/db/clickhouse/transform";
import { DrizzleORM } from "@/db/client";
import { Database } from "@/db/database";
import { organizations } from "@/db/schema";
import { Payments } from "@/payments";
import { Settings } from "@/settings";
import { RealtimeSpans } from "@/workers/realtimeSpans";

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

const meterSpans = (
  data: SpansIngestMessage,
): Effect.Effect<void, never, DrizzleORM | Payments> =>
  Effect.gen(function* () {
    if (data.spans.length === 0) {
      return;
    }

    const client = yield* DrizzleORM;
    const payments = yield* Payments;

    const [organizationRecord] = yield* client
      .select({ stripeCustomerId: organizations.stripeCustomerId })
      .from(organizations)
      .where(eq(organizations.id, data.organizationId))
      .pipe(
        Effect.catchAll((error) => {
          console.error(
            `[spanIngestQueue] Failed to fetch organization ${data.organizationId} for span metering:`,
            error,
          );
          return Effect.succeed([]);
        }),
      );

    if (!organizationRecord) {
      console.error(
        `[spanIngestQueue] Organization ${data.organizationId} not found for span metering`,
      );
      return;
    }

    for (const span of data.spans) {
      yield* payments.products.spans
        .chargeMeter({
          stripeCustomerId: organizationRecord.stripeCustomerId,
          spanId: span.spanId,
        })
        .pipe(
          Effect.catchAll((error) => {
            console.error(
              `[spanIngestQueue] Failed to meter span ${span.spanId}:`,
              error,
            );
            return Effect.void;
          }),
        );
    }
  });

/**
 * Effect program to ingest a spans message.
 *
 * Writes to ClickHouse (source of truth), meters spans, and updates the
 * realtime cache (DurableObject). DurableObject upsert is best-effort:
 * failures are logged but don't block ClickHouse insert. This ensures
 * data durability even when the DurableObject is temporarily unavailable.
 *
 * @param data - Span ingestion message data
 */
export const ingestSpansMessage = (
  data: SpansIngestMessage,
): Effect.Effect<
  void,
  Error,
  ClickHouse | RealtimeSpans | DrizzleORM | Payments
> =>
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

    yield* meterSpans(data);

    yield* realtimeSpans.upsert(data).pipe(
      /* v8 ignore start */
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

/**
 * Environment type for span ingest queue consumer.
 *
 * Extends BillingCronTriggerEnv since Stripe is required for span metering.
 */
type SpanIngestEnvironment = BillingCronTriggerEnv & {
  readonly REALTIME_SPANS_DURABLE_OBJECT: DurableObjectNamespace;
};

export default {
  /**
   * Queue consumer handler for span ingestion messages.
   *
   * @param batch - Batch of messages from the queue
   * @param environment - Cloudflare Workers environment bindings
   */
  async queue(
    batch: MessageBatch<SpansIngestMessage>,
    environment: SpanIngestEnvironment,
  ): Promise<void> {
    if (!environment.CLICKHOUSE_URL) {
      console.error("[spanIngestQueue] Missing CLICKHOUSE_URL binding");
      for (const message of batch.messages) {
        message.retry({ delaySeconds: 60 });
      }
      return;
    }

    // Prefer Hyperdrive connection string over raw DATABASE_URL
    const databaseUrl =
      environment.HYPERDRIVE?.connectionString ?? environment.DATABASE_URL;
    if (!databaseUrl) {
      console.error("[spanIngestQueue] Missing DATABASE_URL binding");
      for (const message of batch.messages) {
        message.retry({ delaySeconds: 60 });
      }
      return;
    }

    const realtimeLayer = RealtimeSpans.Live(
      environment.REALTIME_SPANS_DURABLE_OBJECT,
    );
    const settingsLayer = Settings.LiveFromEnvironment(environment);

    for (const message of batch.messages) {
      // Build program that uses Settings for validated configuration
      const program = Effect.gen(function* () {
        const settings = yield* Settings;

        // Build layers using validated settings
        const clickhouseLayer = ClickHouse.Default.pipe(
          Layer.provide(Layer.succeed(Settings, settings)),
        );
        const meteringLayer = Database.Live({
          database: { connectionString: databaseUrl },
          payments: settings.stripe,
        });

        const serviceLayer = Layer.merge(
          Layer.mergeAll(clickhouseLayer, realtimeLayer),
          meteringLayer,
        );

        yield* ingestSpansMessage(message.body).pipe(
          Effect.provide(serviceLayer),
        );
      });

      await Effect.runPromise(
        program.pipe(
          Effect.provide(settingsLayer),
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
