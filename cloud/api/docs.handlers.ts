import { Effect } from "effect";
import { generateOpenApiSpec } from "@/api/generate-openapi";
import { type OpenApiSpec } from "@/api/docs.schemas";

export * from "@/api/docs.schemas";

export const getOpenApiSpecHandler = Effect.sync(() => {
  const spec = generateOpenApiSpec();
  // eslint-disable-next-line @typescript-eslint/no-unsafe-return
  return spec as OpenApiSpec;
});
