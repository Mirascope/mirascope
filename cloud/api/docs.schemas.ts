import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";

export const OpenApiSpecSchema = Schema.Any;

export type OpenApiSpec = typeof OpenApiSpecSchema.Type;

export class DocsApi extends HttpApiGroup.make("docs").add(
  HttpApiEndpoint.get("openapi", "/docs/openapi.json").addSuccess(
    OpenApiSpecSchema,
  ),
) {}
