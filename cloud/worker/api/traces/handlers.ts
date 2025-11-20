import type { Environment } from "@/worker/environment";
import type { Context } from "hono";
import type { TraceRequest, TraceResponse } from "./schemas";

export async function handleTraces(c: Context<{ Bindings: Environment }>) {
  const traceData = await c.req.json<TraceRequest>();

  const serviceName =
    traceData.resourceSpans?.[0]?.resource?.attributes?.find(
      (attr) => attr.key === "service.name",
    )?.value?.stringValue || "unknown";

  let totalSpans = 0;
  traceData.resourceSpans?.forEach((rs) => {
    rs.scopeSpans?.forEach((ss) => {
      totalSpans += ss.spans?.length || 0;
    });
  });

  console.log(
    `[TRACE DEBUG] Received ${totalSpans} spans from service: ${serviceName}`,
  );
  console.log(
    "[TRACE DEBUG] Full trace data:",
    JSON.stringify(traceData, null, 2),
  );

  const response: TraceResponse = {
    partialSuccess: {},
  };

  return c.json(response);
}
