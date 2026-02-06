/**
 * @fileoverview Cloudflare Queue Consumer for router metering.
 *
 * Processes successful router requests asynchronously, ensuring usage data
 * is persisted even if the initial database update fails.
 *
 * ## Responsibilities
 *
 * 1. **Process Metering**: Update router request with usage/cost and settle funds
 * 2. **Retry Handling**: Automatic retry via Cloudflare Queue retry mechanism
 * 3. **DLQ Fallback**: Failed messages go to dead letter queue after max retries
 */

import type { MessageBatch, Message } from "@cloudflare/workers-types";

import { Effect, Context, Layer } from "effect";

import type { MeteringCostBreakdown } from "@/api/router/cost-utils";
import type { TokenUsage } from "@/api/router/pricing";
import type { RouterRequestIdentifiers } from "@/api/router/utils";

import { Database } from "@/db/database";
import { Payments } from "@/payments";
import { Settings } from "@/settings";
import { type WorkerEnv } from "@/workers/config";

// =============================================================================
// Types
// =============================================================================

/**
 * Message payload for router metering queue.
 *
 * NOTE: we have `*Centicents: number` for serialization purposes.
 * These translate to their `MeteringCostBreakdown` equivalents, which
 * are properly typed with `CostInCenticents`.
 */
export interface RouterMeteringMessage {
  routerRequestId: string;
  reservationId: string;
  request: RouterRequestIdentifiers;
  usage: TokenUsage;
  /** Total cost in centi-cents (1 = $0.0001 USD) - sum of token and tool costs */
  costCenticents: number;
  /** Token cost in centi-cents (1 = $0.0001 USD) */
  tokenCostCenticents: number;
  /** Tool cost in centi-cents (1 = $0.0001 USD) */
  toolCostCenticents?: number;
  timestamp: number;
}

// =============================================================================
// Queue Service
// =============================================================================

/**
 * Router metering queue service.
 *
 * Provides Effect-native access to the Cloudflare Queue binding for
 * enqueueing metering messages.
 */
export class RouterMeteringQueueService extends Context.Tag(
  "RouterMeteringQueue",
)<
  RouterMeteringQueueService,
  {
    readonly send: (
      message: RouterMeteringMessage,
    ) => Effect.Effect<void, Error>;
  }
>() {
  /**
   * Creates a live implementation of the RouterMeteringQueue service.
   *
   * @param queue - Cloudflare Queue binding from environment
   */
  static Live(queue: {
    send: (message: RouterMeteringMessage) => Promise<void>;
  }) {
    return Layer.succeed(
      RouterMeteringQueueService,
      RouterMeteringQueueService.of({
        send: (message) =>
          Effect.tryPromise({
            try: () => queue.send(message),
            catch: (error) =>
              new Error(
                `Failed to enqueue metering: ${error instanceof Error ? error.message : /* v8 ignore next 1 */ String(error)}`,
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
 * Global router metering queue layer.
 *
 * Initialized by server-entry.ts when the Cloudflare binding is available.
 * Route handlers can import this layer to access the queue service.
 */
export let routerMeteringQueueLayer: Layer.Layer<RouterMeteringQueueService> =
  Layer.succeed(RouterMeteringQueueService, {
    send: () => Effect.fail(new Error("RouterMeteringQueue not initialized")),
  });

/**
 * Sets the global router metering queue layer.
 *
 * Called by server-entry.ts to initialize the layer with the Cloudflare binding.
 */
export const setRouterMeteringQueueLayer = (
  layer: Layer.Layer<RouterMeteringQueueService>,
): void => {
  routerMeteringQueueLayer = layer;
};

// =============================================================================
// Message Processing
// =============================================================================

/**
 * Effect program to update router request and settle funds.
 *
 * Exported for testing purposes.
 *
 * @param data - Metering message data
 * @param costs - Cost breakdown with token, tool, and total costs
 */
export function updateAndSettleRouterRequest(
  data: RouterMeteringMessage,
  costs: MeteringCostBreakdown,
): Effect.Effect<void, Error, Database | Payments> {
  return Effect.gen(function* () {
    const db = yield* Database;
    const payments = yield* Payments;

    // Update router request with usage and cost
    yield* db.organizations.projects.environments.apiKeys.routerRequests.update(
      {
        userId: data.request.userId,
        organizationId: data.request.organizationId,
        projectId: data.request.projectId,
        environmentId: data.request.environmentId,
        apiKeyId: data.request.apiKeyId,
        routerRequestId: data.routerRequestId,
        data: {
          inputTokens: data.usage.inputTokens
            ? BigInt(data.usage.inputTokens)
            : null,
          outputTokens: data.usage.outputTokens
            ? BigInt(data.usage.outputTokens)
            : null,
          cacheReadTokens: data.usage.cacheReadTokens
            ? BigInt(data.usage.cacheReadTokens)
            : null,
          cacheWriteTokens: data.usage.cacheWriteTokens
            ? BigInt(data.usage.cacheWriteTokens)
            : null,
          cacheWriteBreakdown: data.usage.cacheWriteBreakdown || null,
          toolUsage: data.usage.toolUsage || null,
          costCenticents: costs.totalCost,
          tokenCostCenticents: costs.tokenCost,
          toolCostCenticents: costs.toolCost ?? null,
          status: "success",
          completedAt: new Date(),
        },
      },
    );

    if (data.request.clawId) {
      // Claw request: record usage (checks per-claw guardrail),
      // then check if within included credits pool
      yield* db.organizations.claws.recordUsage({
        clawId: data.request.clawId,
        organizationId: data.request.organizationId,
        amountCenticents: costs.totalCost,
      });

      const pool = yield* db.organizations.claws.getInternalPoolUsage({
        organizationId: data.request.organizationId,
      });

      if (pool.totalUsageCenticents <= BigInt(pool.limitCenticents)) {
        // Within included credits — release reservation without charging meter
        yield* payments.products.router.releaseFunds(data.reservationId);
      } else {
        // Over included credits — charge the Stripe meter
        yield* payments.products.router.settleFunds(
          data.reservationId,
          costs.totalCost,
        );
      }
    } else {
      // Non-claw request — settle normally
      yield* payments.products.router.settleFunds(
        data.reservationId,
        costs.totalCost,
      );
    }
  });
}

/**
 * Processes a single metering message.
 *
 * Updates the router request with usage/cost data and settles the fund reservation.
 * This is the core metering logic that runs asynchronously for every successful
 * router request.
 *
 * @param message - Queue message containing metering data
 * @param env - Cloudflare Workers environment bindings
 */
async function processMessage(
  message: Message<RouterMeteringMessage>,
  env: WorkerEnv,
): Promise<void> {
  const data = message.body;

  // Database connection string from Hyperdrive
  const databaseUrl = env.HYPERDRIVE?.connectionString;
  if (!databaseUrl) {
    console.error("[routerMeteringQueue] HYPERDRIVE binding not configured");
    message.retry({ delaySeconds: 60 });
    return;
  }

  // Build cost breakdown (converting to bigint for database and payments)
  const costs: MeteringCostBreakdown = {
    tokenCost:
      typeof data.tokenCostCenticents === "bigint"
        ? data.tokenCostCenticents
        : BigInt(data.tokenCostCenticents),
    // Use != null to handle 0 correctly
    toolCost:
      data.toolCostCenticents != null
        ? typeof data.toolCostCenticents === "bigint"
          ? data.toolCostCenticents
          : BigInt(data.toolCostCenticents)
        : undefined,
    totalCost:
      typeof data.costCenticents === "bigint"
        ? data.costCenticents
        : BigInt(data.costCenticents),
  };

  // Build the program using Settings for validated configuration
  const program = Effect.gen(function* () {
    const settings = yield* Settings;

    // Build Database.Live layer (provides both Database and Payments services)
    const layer = Database.Live({
      database: { connectionString: databaseUrl },
      payments: settings.stripe,
    });

    // Update router request and settle funds
    yield* updateAndSettleRouterRequest(data, costs).pipe(
      Effect.provide(layer),
    );
  });

  // Run with Settings layer from environment
  await Effect.runPromise(
    program.pipe(
      Effect.provide(Settings.LiveFromEnvironment(env)),
      Effect.catchAll((error) => {
        console.error(
          `[routerMeteringQueue] Error processing message for request ${data.routerRequestId}:`,
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
   * Queue consumer handler for router metering messages.
   *
   * @param batch - Batch of messages from the queue
   * @param env - Cloudflare Workers environment bindings
   */
  async queue(
    batch: MessageBatch<RouterMeteringMessage>,
    env: WorkerEnv,
  ): Promise<void> {
    console.log(
      `[routerMeteringQueue] Processing ${batch.messages.length} messages`,
    );

    for (const message of batch.messages) {
      await processMessage(message, env);
    }
  },
};
