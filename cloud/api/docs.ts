import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema, Effect } from "effect";
import { generateOpenApiSpec } from "./generate-openapi";

// ============================================================================
// Schemas
// ============================================================================

// OpenAPI spec is a complex object, so we use Schema.Any for now
// The actual structure is validated by generateOpenApiSpec
export const OpenApiSpecSchema = Schema.Any;

export type OpenApiSpec = typeof OpenApiSpecSchema.Type;

// ============================================================================
// API Group
// ============================================================================

export class DocsApi extends HttpApiGroup.make("docs").add(
  HttpApiEndpoint.get("openapi", "/docs/openapi.json").addSuccess(
    OpenApiSpecSchema,
  ),
) {}

// ============================================================================
// Handler Effects
// ============================================================================

export const getOpenApiSpecHandler = Effect.gen(function* () {
  const spec = generateOpenApiSpec();
  return spec as OpenApiSpec;
});
