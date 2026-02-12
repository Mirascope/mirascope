/**
 * Environment validation for the Dispatch Worker.
 *
 * Validates that all required Cloudflare Worker bindings are present
 * at request time. Throws a descriptive error listing any missing bindings.
 */

import type { DispatchEnv } from "./types";

/**
 * Validate that all required environment bindings are present.
 *
 * Call this early in the request lifecycle to fail fast with a clear
 * error message rather than cryptic "cannot read property of undefined"
 * errors deep in the request handler.
 */
export function validateEnv(env: DispatchEnv): void {
  const missing: string[] = [];

  if (!env.Sandbox) {
    missing.push("Sandbox (DurableObjectNamespace)");
  }

  if (!env.MIRASCOPE_CLOUD) {
    missing.push("MIRASCOPE_CLOUD (service binding)");
  }

  if (!env.SITE_URL) {
    missing.push("SITE_URL");
  }

  if (missing.length > 0) {
    throw new Error(
      `Dispatch worker env validation failed — missing required bindings:\n  - ${missing.join("\n  - ")}`,
    );
  }
}
