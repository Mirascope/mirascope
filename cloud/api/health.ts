import { os } from "@orpc/server";
import { z } from "zod";

const HealthResponseSchema = z.object({
  status: z.literal("ok"),
  timestamp: z.iso.datetime(),
  environment: z.string(),
});

export type HealthResponse = z.infer<typeof HealthResponseSchema>;

export const getHealth = os
  .$context<{ environment?: string }>()
  .route({ method: "GET", path: "/health" })
  .output(HealthResponseSchema)
  .handler(
    async ({ context }): Promise<HealthResponse> => ({
      status: "ok",
      timestamp: new Date().toISOString(),
      environment: context.environment || "unknown",
    }),
  );

export const router = os.tag("health").router({
  check: getHealth,
});
