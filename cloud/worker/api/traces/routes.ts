import { createRoute } from "@hono/zod-openapi";
import { TraceRequestSchema, TraceResponseSchema } from "./schemas";

export const tracesRoute = createRoute({
  method: "post",
  path: "/v1/traces",
  tags: ["Telemetry"],
  summary: "Debug endpoint for OpenTelemetry traces",
  description:
    "Temporary endpoint to receive and log OpenTelemetry trace data for debugging purposes. This endpoint follows the OTLP/HTTP specification.",
  request: {
    body: {
      content: {
        "application/json": {
          schema: TraceRequestSchema,
        },
      },
    },
  },
  responses: {
    200: {
      content: {
        "application/json": {
          schema: TraceResponseSchema,
        },
      },
      description: "Trace export acknowledged",
    },
    400: {
      description: "Invalid request format",
    },
    500: {
      description: "Internal server error",
    },
  },
});
