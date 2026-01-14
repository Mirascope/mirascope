/**
 * @fileoverview Cloudflare Queue Consumer for spans metering.
 *
 * Processes span ingestion events asynchronously, ensuring usage data
 * is metered even if the initial metering fails.
 *
 * ## Responsibilities
 *
 * 1. **Process Metering**: Charge Stripe Cloud Spans meter for ingested spans
 * 2. **Retry Handling**: Automatic retry via Cloudflare Queue retry mechanism
 * 3. **DLQ Fallback**: Failed messages go to dead letter queue after max retries
 */

import { Effect, Context, Layer } from "effect";
import type { MessageBatch, Message } from "@cloudflare/workers-types";
import { Database } from "@/db";
import { Payments } from "@/payments";
import { type WorkerEnv } from "./cron-config";

// =============================================================================
// Types
// =============================================================================

/**
 * Message payload for spans metering queue.
 */
export interface SpanMeteringMessage {
  spanId: string;
  organizationId: string;
  projectId: string;
  environmentId: string;
  stripeCustomerId: string;
  timestamp: number;
}

// =============================================================================
// Queue Service
// =============================================================================

/**
 * Spans metering queue service.
 *
 * Provides Effect-native access to the Cloudflare Queue binding for
 * enqueueing metering messages.
 */
export class SpansMeteringQueueService extends Context.Tag(
  "SpansMeteringQueue",
)<
  SpansMeteringQueueService,
  {
    readonly send: (message: SpanMeteringMessage) => Effect.Effect<void, Error>;
  }
>() {
  /**
   * Creates a live implementation of the SpansMeteringQueue service.
   *
   * @param queue - Cloudflare Queue binding from environment
   */
  static Live(queue: {
    send: (message: SpanMeteringMessage) => Promise<void>;
  }) {
    return Layer.succeed(
      SpansMeteringQueueService,
      SpansMeteringQueueService.of({
        send: (message) =>
          Effect.tryPromise({
            try: () => queue.send(message),
            catch: (error) =>
              new Error(
                `Failed to enqueue span metering: ${error instanceof Error ? error.message : /* v8 ignore next 1 */ String(error)}`,
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
 * Effect program to charge the spans meter.
 *
 * Exported for testing purposes.
 *
 * @param data - Metering message data
 */
export function chargeSpanMeter(
  data: SpanMeteringMessage,
): Effect.Effect<void, Error, Payments> {
  return Effect.gen(function* () {
    const payments = yield* Payments;

    // Charge the Cloud Spans meter (1 unit per span)
    yield* payments.products.spans.chargeMeter({
      stripeCustomerId: data.stripeCustomerId,
      spanId: data.spanId,
    });
  });
}

/**
 * Processes a single metering message.
 *
 * Charges the Cloud Spans meter for the ingested span.
 * This is the core metering logic that runs asynchronously for every
 * successfully ingested span.
 *
 * @param message - Queue message containing metering data
 * @param env - Cloudflare Workers environment bindings
 */
async function processMessage(
  message: Message<SpanMeteringMessage>,
  env: WorkerEnv,
): Promise<void> {
  const data = message.body;

  // Database connection string from Hyperdrive or direct URL
  const databaseUrl = env.HYPERDRIVE?.connectionString ?? env.DATABASE_URL;
  if (!databaseUrl) {
    console.error(
      "[spansMeteringQueue] No database connection available (HYPERDRIVE or DATABASE_URL required)",
    );
    message.retry({ delaySeconds: 60 });
    return;
  }

  // Stripe configuration validation
  if (
    !env.STRIPE_SECRET_KEY ||
    !env.STRIPE_CLOUD_SPANS_PRICE_ID ||
    !env.STRIPE_CLOUD_SPANS_METER_ID
  ) {
    console.error(
      "[spansMeteringQueue] Missing Stripe configuration (STRIPE_SECRET_KEY, STRIPE_CLOUD_SPANS_PRICE_ID, STRIPE_CLOUD_SPANS_METER_ID required)",
    );
    message.retry({ delaySeconds: 60 });
    return;
  }

  // Charge the spans meter
  const program = chargeSpanMeter(data);

  // Build Database.Live layer (provides both Database and Payments services)
  const layer = Database.Live({
    database: { connectionString: databaseUrl },
    payments: {
      apiKey: env.STRIPE_SECRET_KEY, // Validated above
      routerPriceId: env.STRIPE_ROUTER_PRICE_ID || "",
      routerMeterId: env.STRIPE_ROUTER_METER_ID || "",
      cloudFreePriceId: env.STRIPE_CLOUD_FREE_PRICE_ID || "",
      cloudProPriceId: env.STRIPE_CLOUD_PRO_PRICE_ID || "",
      cloudTeamPriceId: env.STRIPE_CLOUD_TEAM_PRICE_ID || "",
      cloudSpansPriceId: env.STRIPE_CLOUD_SPANS_PRICE_ID, // Validated above
      cloudSpansMeterId: env.STRIPE_CLOUD_SPANS_METER_ID, // Validated above
    },
  });

  // Run the program
  await Effect.runPromise(
    program.pipe(
      Effect.provide(layer),
      Effect.catchAll((error) => {
        console.error(
          `[spansMeteringQueue] Error processing message for span ${data.spanId}:`,
          error,
        );
        // Retry on error (Cloudflare Queue handles max_retries)
        message.retry({ delaySeconds: 60 });
        return Effect.void;
      }),
    ),
  );
}

// =============================================================================
// Queue Handler
// =============================================================================

export default {
  /**
   * Queue consumer handler for spans metering messages.
   *
   * @param batch - Batch of messages from the queue
   * @param env - Cloudflare Workers environment bindings
   */
  async queue(
    batch: MessageBatch<SpanMeteringMessage>,
    env: WorkerEnv,
  ): Promise<void> {
    console.log(
      `[spansMeteringQueue] Processing ${batch.messages.length} messages`,
    );

    for (const message of batch.messages) {
      await processMessage(message, env);
    }
  },
};
