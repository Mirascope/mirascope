import {
  createStartHandler,
  defaultStreamHandler,
} from "@tanstack/react-start/server";
import reservationExpiryCron from "@/workers/reservationExpiryCron";
import billingReconciliationCron from "@/workers/billingReconciliationCron";
import routerMeteringQueue, {
  RouterMeteringQueueService,
  setRouterMeteringQueueLayer,
} from "@/workers/routerMeteringQueue";
import spanIngestQueue, {
  SpansIngestQueue,
  setSpansIngestQueueLayer,
} from "@/workers/spanIngestQueue";
import spansMeteringQueue, {
  SpansMeteringQueueService,
  setSpansMeteringQueueLayer,
} from "@/workers/spansMeteringQueue";
import { RealtimeSpans, setRealtimeSpansLayer } from "@/workers/realtimeSpans";
import { RealtimeSpansDurableObjectBase } from "@/workers/realtimeSpans/durableObject";
import type { RouterMeteringMessage } from "@/workers/routerMeteringQueue";
import type { SpansIngestMessage } from "@/workers/spanIngestQueue";
import type { SpanMeteringMessage } from "@/workers/spansMeteringQueue";
import type { MessageBatch } from "@cloudflare/workers-types";
import { type WorkerEnv } from "@/workers/cron-config";
import { Layer, Context } from "effect";

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
 * Scheduled event handler that routes to the appropriate cron job.
 *
 * - `* /5 * * * *`: Reservation expiry + billing reconciliation (every 5 minutes)
 *
 * @param event - Cloudflare scheduled event containing the cron expression
 * @param env - Cloudflare Workers environment bindings
 */
const scheduled = async (
  event: ScheduledEvent,
  env: WorkerEnv,
): Promise<void> => {
  if (event.cron === "*/5 * * * *" || event.cron === "local") {
    // Reservation expiry must run before billing reconciliation
    // to ensure expired reservations are properly marked
    await reservationExpiryCron.scheduled(event, env);
    await billingReconciliationCron.scheduled(event, env);
  }
};

const fetch: ExportedHandlerFetchHandler<WorkerEnv> = (request, env, ctx) => {
  // Set execution context layer for route handlers
  executionContextLayer = Layer.succeed(ExecutionContext, ctx);

  // Initialize queue layers from Cloudflare bindings
  if (env.ROUTER_METERING_QUEUE) {
    setRouterMeteringQueueLayer(
      RouterMeteringQueueService.Live(env.ROUTER_METERING_QUEUE),
    );
  }
  if (env.SPANS_INGEST_QUEUE) {
    setSpansIngestQueueLayer(SpansIngestQueue.Live(env.SPANS_INGEST_QUEUE));
  }
  if (env.SPANS_METERING_QUEUE) {
    setSpansMeteringQueueLayer(
      SpansMeteringQueueService.Live(env.SPANS_METERING_QUEUE),
    );
  }
  if (env.REALTIME_SPANS_DURABLE_OBJECT) {
    setRealtimeSpansLayer(
      RealtimeSpans.Live(env.REALTIME_SPANS_DURABLE_OBJECT),
    );
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

const queue = async (batch: MessageBatch, env: WorkerEnv): Promise<void> => {
  if (batch.queue === "router-metering") {
    await routerMeteringQueue.queue(
      batch as MessageBatch<RouterMeteringMessage>,
      env,
    );
    return;
  }
  if (batch.queue === "spans-ingest") {
    await spanIngestQueue.queue(batch as MessageBatch<SpansIngestMessage>, env);
    return;
  }
  if (batch.queue === "spans-metering") {
    await spansMeteringQueue.queue(
      batch as MessageBatch<SpanMeteringMessage>,
      env,
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
