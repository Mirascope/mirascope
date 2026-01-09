import {
  createStartHandler,
  defaultStreamHandler,
} from "@tanstack/react-start/server";
import clickhouseCron, { type CronTriggerEnv } from "@/workers/clickhouseCron";
import reservationExpiryCron from "@/workers/reservationExpiryCron";
import billingReconciliationCron from "@/workers/billingReconciliationCron";

interface ScheduledEvent {
  readonly scheduledTime: number;
  readonly cron: string;
}

const fetchHandler = createStartHandler(defaultStreamHandler);

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

const fetch: ExportedHandlerFetchHandler<CronTriggerEnv> = (
  request,
  env,
  ctx,
) => {
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
};
