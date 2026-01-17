import {
  createStartHandler,
  defaultStreamHandler,
} from "@tanstack/react-start/server";
import reservationExpiryCron from "@/workers/reservationExpiryCron";
import billingReconciliationCron from "@/workers/billingReconciliationCron";
import routerMeteringQueue, {
  RouterMeteringQueueService,
} from "@/workers/routerMeteringQueue";
import spanIngestQueue, { SpansIngestQueue } from "@/workers/spanIngestQueue";
import { RealtimeSpans } from "@/workers/realtimeSpans";
import { RealtimeSpansDurableObjectBase } from "@/workers/realtimeSpans/durableObject";
import type { RouterMeteringMessage } from "@/workers/routerMeteringQueue";
import type { SpansIngestMessage } from "@/workers/spanIngestQueue";
import type { MessageBatch } from "@cloudflare/workers-types";
import { type WorkerEnv } from "@/workers/config";
import { Effect, Layer, Context } from "effect";
import { RateLimiter } from "@/rate-limiting";

/**
 * ExecutionContext service tag for Effect dependency injection.
 *
 * Provides access to the Cloudflare Workers ExecutionContext, which allows
 * route handlers to use ctx.waitUntil() for background tasks.
 *
 * @example
 * ```ts
 * const program = Effect.gen(function* () {
 *   const ctx = yield* ExecutionContext;
 *
 *   // Fork a background task and keep worker alive
 *   const fiber = yield* Effect.fork(backgroundTask);
 *   ctx.waitUntil(Effect.runPromise(Fiber.await(fiber)));
 * });
 * ```
 */
export class ExecutionContext extends Context.Tag("ExecutionContext")<
  ExecutionContext,
  globalThis.ExecutionContext
>() {}

/**
 * Global execution context layer.
 *
 * Set by the fetch handler and exported for route handlers to include
 * when providing Effect layers. This allows route handlers to use
 * ctx.waitUntil() for background tasks.
 */
export let executionContextLayer: Layer.Layer<ExecutionContext> = Layer.succeed(
  ExecutionContext,
  {
    waitUntil: () => {},
    passThroughOnException: () => {},
    props: undefined,
  } as globalThis.ExecutionContext,
);

interface ScheduledEvent {
  readonly scheduledTime: number;
  readonly cron: string;
}

const fetchHandler = createStartHandler(defaultStreamHandler);

/**
 * Global router metering queue layer.
 *
 * Set by the fetch handler and exported for route handlers to include
 * when providing Effect layers.
 */
export let routerMeteringQueueLayer: Layer.Layer<RouterMeteringQueueService> =
  Layer.succeed(RouterMeteringQueueService, {
    send: () => Effect.fail(new Error("RouterMeteringQueue not initialized")),
  });

/**
 * Global spans ingest queue layer.
 *
 * Set by the fetch handler and exported for route handlers to include
 * when providing Effect layers.
 */
export let spansIngestQueueLayer: Layer.Layer<SpansIngestQueue> = Layer.succeed(
  SpansIngestQueue,
  {
    send: () => Effect.fail(new Error("SpansIngestQueue not initialized")),
  },
);

/**
 * Global realtime spans layer.
 *
 * Set by the fetch handler when REALTIME_SPANS_DURABLE_OBJECT binding is available.
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
 * Global rate limiter layer.
 *
 * Set by the fetch handler and exported for route handlers to include
 * when providing Effect layers. Uses Cloudflare's native rate limiting API
 * for atomic, distributed rate limit tracking.
 */
export let rateLimiterLayer: Layer.Layer<RateLimiter> = Layer.succeed(
  RateLimiter,
  {
    checkRateLimit: () =>
      Effect.succeed({
        allowed: true,
        limit: 0,
        resetAt: new Date(),
      }),
    addRateLimitHeaders: ({ response }) => response,
    createRateLimitErrorResponse: ({ error }) =>
      new Response(JSON.stringify({ error: error.message }), {
        status: 429,
        headers: { "Content-Type": "application/json" },
      }),
  },
);

/**
 * Scheduled event handler that routes to the appropriate cron job.
 *
 * - `* /5 * * * *`: Reservation expiry + billing reconciliation (every 5 minutes)
 *
 * @param event - Cloudflare scheduled event containing the cron expression
 * @param environment - Cloudflare Workers environment bindings
 */
const scheduled = async (
  event: ScheduledEvent,
  environment: WorkerEnv,
): Promise<void> => {
  if (event.cron === "*/5 * * * *" || event.cron === "local") {
    // Reservation expiry must run before billing reconciliation
    // to ensure expired reservations are properly marked
    await reservationExpiryCron.scheduled(event, environment);
    await billingReconciliationCron.scheduled(event, environment);
  }
};

const fetch: ExportedHandlerFetchHandler<WorkerEnv> = (
  request,
  environment,
  context,
) => {
  // Set execution context layer for route handlers
  executionContextLayer = Layer.succeed(ExecutionContext, context);

  // Set router metering queue layer for route handlers
  if (environment.ROUTER_METERING_QUEUE) {
    routerMeteringQueueLayer = RouterMeteringQueueService.Live(
      environment.ROUTER_METERING_QUEUE,
    );
  }
  if (environment.SPANS_INGEST_QUEUE) {
    spansIngestQueueLayer = SpansIngestQueue.Live(
      environment.SPANS_INGEST_QUEUE,
    );
  }
  if (environment.REALTIME_SPANS_DURABLE_OBJECT) {
    realtimeSpansLayer = RealtimeSpans.Live(
      environment.REALTIME_SPANS_DURABLE_OBJECT,
    );
  }

  // Set rate limiter layer for route handlers
  if (
    environment.RATE_LIMITER_FREE &&
    environment.RATE_LIMITER_PRO &&
    environment.RATE_LIMITER_TEAM
  ) {
    rateLimiterLayer = RateLimiter.Live({
      free: environment.RATE_LIMITER_FREE,
      pro: environment.RATE_LIMITER_PRO,
      team: environment.RATE_LIMITER_TEAM,
    });
  }

  if (environment.ENVIRONMENT === "local") {
    const { pathname } = new URL(request.url);
    if (pathname === "/__scheduled") {
      const event: ScheduledEvent = {
        cron: "local",
        scheduledTime: Date.now(),
      };
      context.waitUntil(scheduled(event, environment));
      return new Response("Ran scheduled event");
    }
    if (pathname === "/__scheduled/billing") {
      const event: ScheduledEvent = {
        cron: "*/5 * * * *",
        scheduledTime: Date.now(),
      };
      context.waitUntil(scheduled(event, environment));
      return new Response("Ran billing reconciliation cron");
    }
  }

  return fetchHandler(request);
};

const queue = async (
  batch: MessageBatch,
  environment: WorkerEnv,
): Promise<void> => {
  if (batch.queue === "router-metering") {
    await routerMeteringQueue.queue(
      batch as MessageBatch<RouterMeteringMessage>,
      environment,
    );
    return;
  }
  if (batch.queue === "spans-ingest") {
    await spanIngestQueue.queue(
      batch as MessageBatch<SpansIngestMessage>,
      environment,
    );
    return;
  }

  console.error(`[queue] Unhandled queue: ${batch.queue}`);
  batch.retryAll();
};

/**
 * Durable Object class for Cloudflare Workers.
 *
 * Cloudflare Workers requires Durable Object classes to be defined and
 * exported from the main entry point. This class extends the base
 * implementation to satisfy the class discovery requirements.
 *
 * The class_name in wrangler.jsonc must match this exported class name.
 */
export class RealtimeSpansDurableObject extends RealtimeSpansDurableObjectBase {}

export default {
  fetch,
  scheduled,
  queue,
};
