import {
  createStartHandler,
  defaultStreamHandler,
} from "@tanstack/react-start/server";
import reservationExpiryCron from "@/workers/reservationExpiryCron";
import billingReconciliationCron from "@/workers/billingReconciliationCron";
import routerMeteringQueue, {
  RouterMeteringQueueService,
} from "@/workers/routerMeteringQueue";
import spanIngestQueue, {
  SpansIngestQueueService,
} from "@/workers/spanIngestQueue";
import { RealtimeSpans } from "@/realtimeSpans";
import { RealtimeSpansLive } from "@/workers/realtimeSpansClient";
import type { RouterMeteringMessage } from "@/workers/routerMeteringQueue";
import type { SpansIngestMessage } from "@/workers/spanIngestQueue";
import type { MessageBatch } from "@cloudflare/workers-types";
import { type WorkerEnv } from "@/workers/cron-config";
import { Effect, Layer } from "effect";

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
export let spansIngestQueueLayer: Layer.Layer<SpansIngestQueueService> =
  Layer.succeed(SpansIngestQueueService, {
    send: () => Effect.fail(new Error("SpansIngestQueue not initialized")),
  });

/**
 * Global realtime spans layer.
 *
 * Set by the fetch handler when RECENT_SPANS_DURABLE_OBJECT binding is available.
 */
export let realtimeSpansLayer: Layer.Layer<RealtimeSpans> = Layer.succeed(
  RealtimeSpans,
  {
    upsert: () => Effect.void,
    search: () => Effect.succeed({ spans: [], total: 0, hasMore: false }),
    getTraceDetail: () =>
      Effect.succeed({
        traceId: "",
        spans: [],
        rootSpanId: null,
        totalDurationMs: null,
      }),
    exists: () => Effect.succeed(false),
  },
);

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
  // Set router metering queue layer for route handlers
  if (env.ROUTER_METERING_QUEUE) {
    routerMeteringQueueLayer = RouterMeteringQueueService.Live(
      env.ROUTER_METERING_QUEUE,
    );
  }
  if (env.SPANS_INGEST_QUEUE) {
    spansIngestQueueLayer = SpansIngestQueueService.Live(
      env.SPANS_INGEST_QUEUE,
    );
  }
  if (env.RECENT_SPANS_DURABLE_OBJECT) {
    realtimeSpansLayer = RealtimeSpansLive(env.RECENT_SPANS_DURABLE_OBJECT);
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

  console.error(`[queue] Unhandled queue: ${batch.queue}`);
  batch.retryAll();
};

export { RecentSpansDurableObject } from "@/workers/recentSpansDurableObject";

export default {
  fetch,
  scheduled,
  queue,
};
