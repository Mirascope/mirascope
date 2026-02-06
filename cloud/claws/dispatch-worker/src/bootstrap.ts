/**
 * Bootstrap config fetcher.
 *
 * Fetches the OpenClawConfig for a claw from the Mirascope internal API.
 * In production this will use a Cloudflare service binding (in-process RPC,
 * no network). For now it falls back to HTTP with a bearer token.
 */

import type { DispatchEnv, OpenClawConfig } from "./types";

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
  const baseUrl = env.MIRASCOPE_API_BASE_URL;
  if (!baseUrl) {
    throw new Error(
      "MIRASCOPE_API_BASE_URL is not set. Required for bootstrap config fetch.",
    );
  }

  const url = `${baseUrl}/api/internal/claws/${clawId}/bootstrap`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (env.MIRASCOPE_API_BEARER_TOKEN) {
    headers["Authorization"] = `Bearer ${env.MIRASCOPE_API_BEARER_TOKEN}`;
  }

  const response = await fetch(url, { method: "GET", headers });

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
  const baseUrl = env.MIRASCOPE_API_BASE_URL;
  if (!baseUrl) {
    throw new Error(
      "MIRASCOPE_API_BASE_URL is not set. Required for claw resolution.",
    );
  }

  const url = `${baseUrl}/api/internal/claws/resolve/${orgSlug}/${clawSlug}`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (env.MIRASCOPE_API_BEARER_TOKEN) {
    headers["Authorization"] = `Bearer ${env.MIRASCOPE_API_BEARER_TOKEN}`;
  }

  const response = await fetch(url, { method: "GET", headers });

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
  const baseUrl = env.MIRASCOPE_API_BASE_URL;
  if (!baseUrl) {
    console.error(
      "MIRASCOPE_API_BASE_URL is not set. Cannot report claw status.",
    );
    return;
  }

  const url = `${baseUrl}/api/internal/claws/${clawId}/status`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (env.MIRASCOPE_API_BEARER_TOKEN) {
    headers["Authorization"] = `Bearer ${env.MIRASCOPE_API_BEARER_TOKEN}`;
  }

  try {
    const response = await fetch(url, {
      method: "POST",
      headers,
      body: JSON.stringify(status),
    });

    if (!response.ok) {
      console.error(
        `Status report failed for claw ${clawId}: ${response.status} ${response.statusText}`,
      );
    }
  } catch (err) {
    console.error(`Status report error for claw ${clawId}:`, err);
  }
}
