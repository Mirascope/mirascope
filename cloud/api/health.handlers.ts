import { Effect } from "effect";
import { SettingsService } from "@/settings";
import { type CheckHealthResponse } from "@/api/health.schemas";

export * from "@/api/health.schemas";

export const checkHealthHandler = Effect.gen(function* () {
  const settings = yield* SettingsService;

  const response: CheckHealthResponse = {
    status: "ok",
    timestamp: new Date().toISOString(),
    environment: settings.env,
  };

  return response;
});
