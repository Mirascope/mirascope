import { Effect } from "effect";
import { generateOpenApiSpec } from "@/api/generate-openapi";
import { type OpenApiSpec } from "@/api/docs.schema";

// Re-export schema types for convenience
export * from "@/api/docs.schema";

// ============================================================================
// Handler Effects
// ============================================================================

export const getOpenApiSpecHandler = Effect.sync(() => {
  const spec = generateOpenApiSpec();
  // eslint-disable-next-line @typescript-eslint/no-unsafe-return
  return spec as OpenApiSpec;
});
