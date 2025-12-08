import { HttpApi, HttpApiBuilder } from "@effect/platform";
import { Layer } from "effect";
import { HealthApi, checkHealthHandler } from "@/api/health";
import { TracesApi, createTraceHandler } from "@/api/traces";
import { DocsApi, getOpenApiSpecHandler } from "@/api/docs";

// ============================================================================
// Combined API Definition
// ============================================================================

export class MirascopeCloudApi extends HttpApi.make("MirascopeCloudApi")
  .add(HealthApi)
  .add(TracesApi)
  .add(DocsApi) {}

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

const DocsHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "docs",
  (handlers) => handlers.handle("openapi", () => getOpenApiSpecHandler),
);

// ============================================================================
// Combined API Layer
// ============================================================================

export const ApiLive = HttpApiBuilder.api(MirascopeCloudApi).pipe(
  Layer.provide(HealthHandlersLive),
  Layer.provide(TracesHandlersLive),
  Layer.provide(DocsHandlersLive),
);
