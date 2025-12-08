import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";

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
