import { Effect } from "effect";

import { type CheckHealthResponse } from "@/api/health.schemas";
import { Settings } from "@/settings";

export * from "@/api/health.schemas";

export const checkHealthHandler = Effect.gen(function* () {
  const settings = yield* Settings;

  const response: CheckHealthResponse = {
    status: "ok",
    timestamp: new Date().toISOString(),
    environment: settings.env,
  };

  return response;
});
