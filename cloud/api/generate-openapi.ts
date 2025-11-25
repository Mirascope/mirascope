import { OpenAPIGenerator } from "@orpc/openapi";
import { ZodToJsonSchemaConverter } from "@orpc/zod/zod4";
import { router } from "./router";

const generator = new OpenAPIGenerator({
  schemaConverters: [new ZodToJsonSchemaConverter()],
});

const spec = await generator.generate(router, {
  info: {
    title: "Mirascope Cloud API",
    version: "0.1.0",
    description: "Complete API documentation for Mirascope Cloud",
  },
  servers: [
    {
      url: "https://v2.mirascope.com",
      description: "Production server",
      // @ts-ignore
      "x-fern-server-name": "production",
    },
    {
      url: "https://staging.mirascope.com",
      description: "Staging server",
      // @ts-ignore
      "x-fern-server-name": "staging",
    },
    {
      url: "http://localhost:3000",
      description: "Local development server",
      // @ts-ignore
      "x-fern-server-name": "local",
    },
  ],
});

console.log(JSON.stringify(spec, null, 2));
