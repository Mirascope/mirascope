import { os } from "@orpc/server";
import { z } from "zod";

const CheckHealthResponseSchema = z.object({
  status: z.literal("ok"),
  timestamp: z.iso.datetime(),
  environment: z.string(),
});

export type CheckHealthResponse = z.infer<typeof CheckHealthResponseSchema>;

export const checkHealth = os
  .$context<{ environment?: string }>()
  .route({ method: "GET", path: "/health" })
  .output(CheckHealthResponseSchema)
  .handler(
    async ({ context }): Promise<CheckHealthResponse> => ({
      status: "ok",
      timestamp: new Date().toISOString(),
      environment: context.environment || "unknown",
    }),
  );

export const router = os.tag("health").router({
  check: checkHealth,
});
