import { createRoute } from "@hono/zod-openapi";
import { HealthResponseSchema } from "./schemas";

export const healthRoute = createRoute({
  method: "get",
  path: "/health",
  tags: ["Health"],
  summary: "Health check endpoint",
  description: "Returns the current health status of the application",
  responses: {
    200: {
      content: {
        "application/json": {
          schema: HealthResponseSchema,
        },
      },
      description: "Application health status",
    },
  },
});
