import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema, Effect } from "effect";
import { EnvironmentService } from "@/environment";

// ============================================================================
// Schemas
// ============================================================================

export const CheckHealthResponseSchema = Schema.Struct({
  status: Schema.Literal("ok"),
  timestamp: Schema.String,
  environment: Schema.String,
});

export type CheckHealthResponse = typeof CheckHealthResponseSchema.Type;

// ============================================================================
// API Group
// ============================================================================

export class HealthApi extends HttpApiGroup.make("health").add(
  HttpApiEndpoint.get("check", "/health").addSuccess(CheckHealthResponseSchema),
) {}

// ============================================================================
// Handler Effect
// ============================================================================

export const checkHealthHandler = Effect.gen(function* () {
  const environment = yield* EnvironmentService;

  const response: CheckHealthResponse = {
    status: "ok",
    timestamp: new Date().toISOString(),
    environment: environment.env,
  };

  return response;
});
