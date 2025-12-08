import { HttpApiBuilder } from "@effect/platform";
import { Layer } from "effect";
import { checkHealthHandler } from "@/api/health";
import { createTraceHandler } from "@/api/traces";
import { getOpenApiSpecHandler } from "@/api/docs";
import {
  listOrganizationsHandler,
  createOrganizationHandler,
  deleteOrganizationHandler,
} from "@/api/organizations";
import { MirascopeCloudApi } from "@/api/api";

// Re-export the API definition for convenience
export { MirascopeCloudApi };

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

const OrganizationsHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "organizations",
  (handlers) =>
    handlers
      .handle("list", () => listOrganizationsHandler)
      .handle("create", ({ payload }) => createOrganizationHandler(payload))
      .handle("delete", ({ path }) => deleteOrganizationHandler(path)),
);

// ============================================================================
// Combined API Layer
// ============================================================================

export const ApiLive = HttpApiBuilder.api(MirascopeCloudApi).pipe(
  Layer.provide(HealthHandlersLive),
  Layer.provide(TracesHandlersLive),
  Layer.provide(DocsHandlersLive),
  Layer.provide(OrganizationsHandlersLive),
);
