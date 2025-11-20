import { z } from "@hono/zod-openapi";

export const HealthResponseSchema = z.object({
  status: z.literal("ok"),
  timestamp: z.string().datetime(),
  environment: z.string(),
});

export type HealthResponse = z.infer<typeof HealthResponseSchema>;
