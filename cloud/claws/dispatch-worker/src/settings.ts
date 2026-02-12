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

  // Validate SITE_URL format
  validateSiteUrl(env.SITE_URL);
}

/**
 * Validate that SITE_URL has the correct format:
 * - Must start with `https://` (or `http://localhost` for local dev)
 * - Must NOT have a trailing slash
 */
function validateSiteUrl(siteUrl: string): void {
  const errors: string[] = [];

  const isLocalhost = /^http:\/\/localhost(:\d+)?(\/|$)/.test(siteUrl);
  if (!siteUrl.startsWith("https://") && !isLocalhost) {
    errors.push(
      `SITE_URL must start with "https://" (or "http://localhost" for dev), got: "${siteUrl}"`,
    );
  }

  if (siteUrl.endsWith("/")) {
    errors.push(`SITE_URL must not have a trailing slash, got: "${siteUrl}"`);
  }

  if (errors.length > 0) {
    throw new Error(
      `Dispatch worker SITE_URL validation failed:\n  - ${errors.join("\n  - ")}`,
    );
  }
}
