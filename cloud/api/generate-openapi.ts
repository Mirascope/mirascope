import { OpenApi } from "@effect/platform";
import { MirascopeCloudApi } from "@/api/router";

/**
 * Generates the OpenAPI specification for the Mirascope Cloud API
 */
export function generateOpenApiSpec() {
  const baseSpec = OpenApi.fromApi(MirascopeCloudApi);
  return {
    ...baseSpec,
    info: {
      ...baseSpec.info,
      title: "Mirascope Cloud API",
      version: "0.1.0",
      description: "Complete API documentation for Mirascope Cloud",
    },
    servers: [
      {
        url: "https://v2.mirascope.com/api/v0",
        description: "Production server",
        "x-fern-server-name": "production",
      },
      {
        url: "https://staging.mirascope.com/api/v0",
        description: "Staging server",
        "x-fern-server-name": "staging",
      },
      {
        url: "http://localhost:3000/api/v0",
        description: "Local development server",
        "x-fern-server-name": "local",
      },
    ],
  };
}

// NOTE: we test this, but it runs as a sub-process, so coverage doesn't catch it.
/* v8 ignore start */
if (import.meta.main) {
  // When run as a script, output the JSON
  const spec = generateOpenApiSpec();
  console.log(JSON.stringify(spec, null, 2));
}
/* v8 ignore stop */
