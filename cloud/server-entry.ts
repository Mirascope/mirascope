import {
  createStartHandler,
  defaultStreamHandler,
} from "@tanstack/react-start/server";
import clickhouseCron, { type CronTriggerEnv } from "@/workers/clickhouseCron";
import reservationExpiryCron from "@/workers/reservationExpiryCron";
import billingReconciliationCron from "@/workers/billingReconciliationCron";
import routerMeteringQueue, {
  RouterMeteringQueueService,
} from "@/workers/routerMeteringQueue";
import spansMeteringQueue, {
  SpansMeteringQueueService,
} from "@/workers/spansMeteringQueue";
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
 * Global spans metering queue layer.
 *
 * Set by the fetch handler and exported for route handlers to include
 * when providing Effect layers.
 */
export let spansMeteringQueueLayer: Layer.Layer<SpansMeteringQueueService> =
  Layer.succeed(SpansMeteringQueueService, {
    send: () => Effect.fail(new Error("SpansMeteringQueue not initialized")),
  });

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
 * - `* /1 * * * *`: ClickHouse synchronization (every minute)
 * - `* /5 * * * *`: Reservation expiry + billing reconciliation (every 5 minutes)
 *
 * @param event - Cloudflare scheduled event containing the cron expression
 * @param env - Cloudflare Workers environment bindings
 */
const scheduled = async (
  event: ScheduledEvent,
  env: CronTriggerEnv,
): Promise<void> => {
  if (event.cron === "*/1 * * * *" || event.cron === "local") {
    // ClickHouse synchronization runs every minute
    await clickhouseCron.scheduled(event, env);
  } else if (event.cron === "*/5 * * * *") {
    // Reservation expiry must run before billing reconciliation
    // to ensure expired reservations are properly marked
    await reservationExpiryCron.scheduled(event, env);
    await billingReconciliationCron.scheduled(event, env);
  }
};

const fetch: ExportedHandlerFetchHandler<WorkerEnv> = (request, env, ctx) => {
  // Set execution context layer for route handlers
  executionContextLayer = Layer.succeed(ExecutionContext, ctx);

  // Set router metering queue layer for route handlers
  if (env.ROUTER_METERING_QUEUE) {
    routerMeteringQueueLayer = RouterMeteringQueueService.Live(
      env.ROUTER_METERING_QUEUE,
    );
  }

  // Set spans metering queue layer for route handlers
  if (env.SPANS_METERING_QUEUE) {
    spansMeteringQueueLayer = SpansMeteringQueueService.Live(
      env.SPANS_METERING_QUEUE,
    );
  }

  // Set rate limiter layer for route handlers
  if (env.RATE_LIMITER_FREE && env.RATE_LIMITER_PRO && env.RATE_LIMITER_TEAM) {
    rateLimiterLayer = RateLimiter.Live({
      free: env.RATE_LIMITER_FREE,
      pro: env.RATE_LIMITER_PRO,
      team: env.RATE_LIMITER_TEAM,
    });
  }

  if (env.ENVIRONMENT === "local") {
    const { pathname } = new URL(request.url);
    if (pathname === "/__scheduled") {
      const event: ScheduledEvent = {
        cron: "local",
        scheduledTime: Date.now(),
      };
      ctx.waitUntil(scheduled(event, env));
      return new Response("Ran scheduled event");
    }
    if (pathname === "/__scheduled/billing") {
      const event: ScheduledEvent = {
        cron: "*/5 * * * *",
        scheduledTime: Date.now(),
      };
      ctx.waitUntil(scheduled(event, env));
      return new Response("Ran billing reconciliation cron");
    }
  }

  return fetchHandler(request);
};

export default {
  fetch,
  scheduled,
  queue(batch: unknown, env: WorkerEnv) {
    // Route to appropriate queue handler based on queue name
    // Cloudflare Workers passes the queue name in the batch metadata
    const queueName = (batch as { queue?: string }).queue;

    if (queueName === "spans-metering") {
      return spansMeteringQueue.queue(batch as never, env);
    }

    // Default to router metering queue for backwards compatibility
    return routerMeteringQueue.queue(batch as never, env);
  },
};
