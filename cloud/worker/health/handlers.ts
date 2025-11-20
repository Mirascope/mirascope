import type { Environment } from "@/worker/environment";
import type { Context } from "hono";
import type { HealthResponse } from "./schemas";

export function handleHealth(c: Context<{ Bindings: Environment }>) {
  const response: HealthResponse = {
    status: "ok",
    timestamp: new Date().toISOString(),
    environment: c.env.ENVIRONMENT || "unknown",
  };

  return c.json(response, 200);
}
