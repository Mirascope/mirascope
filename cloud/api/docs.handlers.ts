import { Effect } from "effect";

import { type OpenApiSpec } from "@/api/docs.schemas";
import { generateOpenApiSpec } from "@/api/generate-openapi";

export * from "@/api/docs.schemas";

export const getOpenApiSpecHandler = Effect.sync(() => {
  const spec = generateOpenApiSpec();
  // eslint-disable-next-line @typescript-eslint/no-unsafe-return
  return spec as OpenApiSpec;
});
