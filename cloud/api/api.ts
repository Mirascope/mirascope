import { HttpApi } from "@effect/platform";

// ============================================================================
// Schema Imports (frontend-safe)
// ============================================================================
// These .schema.ts files contain ONLY type definitions and API groups.
// They have no server-side dependencies and can be safely imported by frontend.

import { HealthApi } from "@/api/health.schema";
import { TracesApi } from "@/api/traces.schema";
import { DocsApi } from "@/api/docs.schema";
import { OrganizationsApi } from "@/api/organizations.schema";

// Re-export all schemas and types for convenience
export * from "@/api/errors.schema";
export * from "@/api/health.schema";
export * from "@/api/traces.schema";
export * from "@/api/docs.schema";
export * from "@/api/organizations.schema";

// ============================================================================
// Combined API Definition
// ============================================================================

export class MirascopeCloudApi extends HttpApi.make("MirascopeCloudApi")
  .add(HealthApi)
  .add(TracesApi)
  .add(DocsApi)
  .add(OrganizationsApi) {}
