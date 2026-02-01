import { OpenApi } from "@effect/platform";

import { MirascopeCloudApi } from "@/api/api";

type OpenApiSpec = {
  openapi: string;
  info: { title: string; version: string; description?: string };
  servers: Array<{
    url: string;
    description: string;
    "x-fern-server-name"?: string;
  }>;
  paths: Record<string, unknown>;
  components?: Record<string, unknown>;
};

/**
 * Recursively renames "_tag" to "tag" in an object.
 * This is needed because Fern SDK generator doesn't support
 * discriminator property names starting with underscore.
 *
 * This handles:
 * - Object keys: { "_tag": value } -> { "tag": value }
 * - String values in arrays (e.g., required arrays): ["_tag"] -> ["tag"]
 */
function renameTagProperty<T>(obj: T): T {
  if (obj === null || typeof obj !== "object") {
    // Handle string values (e.g., "_tag" in required arrays)
    if (typeof obj === "string" && obj === "_tag") {
      return "tag" as T;
    }
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map(renameTagProperty) as T;
  }

  const result: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(obj)) {
    const newKey = key === "_tag" ? "tag" : key;
    result[newKey] = renameTagProperty(value);
  }
  return result as T;
}

/**
 * Generates the OpenAPI specification for the Mirascope Cloud API
 */
export function generateOpenApiSpec(): OpenApiSpec {
  const baseSpec = OpenApi.fromApi(MirascopeCloudApi);
  const spec = {
    ...baseSpec,
    info: {
      ...baseSpec.info,
      title: "Mirascope Cloud API",
      version: "0.1.0",
      description: "Complete API documentation for Mirascope Cloud",
    },
    servers: [
      {
        url: "https://mirascope.com/api/v2",
        description: "Production server",
        "x-fern-server-name": "production",
      },
      {
        url: "https://staging.mirascope.com/api/v2",
        description: "Staging server",
        "x-fern-server-name": "staging",
      },
      {
        url: "http://localhost:3000/api/v2",
        description: "Local development server",
        "x-fern-server-name": "local",
      },
    ],
  };

  // Rename _tag to tag for Fern SDK compatibility
  return renameTagProperty(spec) as unknown as OpenApiSpec;
}

// NOTE: we test this, but it runs as a sub-process, so coverage doesn't catch it.
/* v8 ignore start */
if (import.meta.main) {
  // When run as a script, output the JSON
  const spec = generateOpenApiSpec();
  console.log(JSON.stringify(spec, null, 2));
}
/* v8 ignore stop */
