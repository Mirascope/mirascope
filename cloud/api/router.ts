import { HttpApi, HttpApiBuilder } from "@effect/platform";
import { Layer } from "effect";
import { HealthApi, checkHealthHandler } from "./health";
import { TracesApi, createTraceHandler } from "./traces";

// ============================================================================
// Combined API Definition
// ============================================================================

export class MirascopeCloudApi extends HttpApi.make("MirascopeCloudApi")
  .add(HealthApi)
  .add(TracesApi) {}

// ============================================================================
// Handlers Layer
// ============================================================================

const HealthHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "health",
  (handlers) => handlers.handle("check", () => checkHealthHandler),
);

const TracesHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "traces",
  (handlers) =>
    handlers.handle("create", ({ payload }) => createTraceHandler(payload)),
);

// ============================================================================
// Combined API Layer
// ============================================================================

export const ApiLive = HttpApiBuilder.api(MirascopeCloudApi).pipe(
  Layer.provide(HealthHandlersLive),
  Layer.provide(TracesHandlersLive),
);
