import { Effect } from "effect";
import { EnvironmentService } from "@/environment";
import { type CheckHealthResponse } from "@/api/health.schemas";

export * from "@/api/health.schemas";

export const checkHealthHandler = Effect.gen(function* () {
  const environment = yield* EnvironmentService;

  const response: CheckHealthResponse = {
    status: "ok",
    timestamp: new Date().toISOString(),
    environment: environment.env,
  };

  return response;
});
