/**
 * Bootstrap config fetcher.
 *
 * Fetches the OpenClawConfig for a claw from the Mirascope internal API
 * via the `env.MIRASCOPE_CLOUD` Cloudflare service binding (in-process
 * RPC — no network hop, no bearer token).
 *
 * There is no HTTP fallback. Local dev relies on unit tests with mocked
 * service bindings; integration testing happens on a deployed staging
 * environment.
 */

import type { DispatchEnv, OpenClawConfig } from "./types";

// ---------------------------------------------------------------------------
// Internal fetch via service binding
// ---------------------------------------------------------------------------

/**
 * Perform a fetch against the Mirascope internal API via service binding.
 *
 * Service binding requests use a synthetic origin (`https://internal`) since
 * the binding ignores the hostname and routes in-process.
 */
function internalFetch(
  env: DispatchEnv,
  path: string,
  init?: RequestInit,
): Promise<Response> {
  return env.MIRASCOPE_CLOUD.fetch(`https://internal${path}`, init);
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Fetch the bootstrap config for a claw by its ID.
 *
 * @param clawId - The unique claw identifier
 * @param env - Worker environment bindings
 * @returns The full OpenClawConfig including R2 credentials and container env vars
 * @throws Error if the API call fails or returns a non-OK response
 */
export async function fetchBootstrapConfig(
  clawId: string,
  env: DispatchEnv,
): Promise<OpenClawConfig> {
  const response = await internalFetch(
    env,
    `/api/internal/claws/${clawId}/bootstrap`,
    {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    },
  );

  if (!response.ok) {
    const body = await response.text().catch(() => "(no body)");
    throw new Error(
      `Bootstrap config fetch failed for claw ${clawId}: ${response.status} ${response.statusText} — ${body}`,
    );
  }

  return (await response.json()) as OpenClawConfig;
}

/**
 * Resolve org/claw slugs to a clawId.
 *
 * The dispatch worker receives requests at {clawSlug}.{orgSlug}.mirascope.com
 * and needs the stable clawId to key the Durable Object. This endpoint
 * resolves the slugs.
 *
 * @param orgSlug - Organization slug from hostname
 * @param clawSlug - Claw slug from hostname
 * @param env - Worker environment bindings
 * @returns The resolved clawId and organizationId
 */
export async function resolveClawId(
  orgSlug: string,
  clawSlug: string,
  env: DispatchEnv,
): Promise<{ clawId: string; organizationId: string }> {
  const response = await internalFetch(
    env,
    `/api/internal/claws/resolve/${orgSlug}/${clawSlug}`,
    {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    },
  );

  if (!response.ok) {
    const body = await response.text().catch(() => "(no body)");
    throw new Error(
      `Claw resolution failed for ${clawSlug}.${orgSlug}: ${response.status} ${response.statusText} — ${body}`,
    );
  }

  return (await response.json()) as { clawId: string; organizationId: string };
}

/**
 * Report claw status back to the Mirascope API.
 *
 * @param clawId - The claw identifier
 * @param status - Status report payload
 * @param env - Worker environment bindings
 */
export async function reportClawStatus(
  clawId: string,
  status: {
    status: string;
    errorMessage?: string;
    startedAt?: string;
  },
  env: DispatchEnv,
): Promise<void> {
  try {
    const response = await internalFetch(
      env,
      `/api/internal/claws/${clawId}/status`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(status),
      },
    );

    if (!response.ok) {
      console.error(
        `Status report failed for claw ${clawId}: ${response.status} ${response.statusText}`,
      );
    }
  } catch (err) {
    console.error(`Status report error for claw ${clawId}:`, err);
  }
}
