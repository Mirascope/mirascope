import {
  createStartHandler,
  defaultStreamHandler,
} from "@tanstack/react-start/server";
import clickhouseCron, { type CronTriggerEnv } from "@/workers/clickhouseCron";

interface ScheduledEvent {
  readonly scheduledTime: number;
  readonly cron: string;
}

const fetchHandler = createStartHandler(defaultStreamHandler);
const scheduled = clickhouseCron.scheduled.bind(clickhouseCron);

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
  }

  return fetchHandler(request);
};

export default {
  fetch,
  scheduled,
};
