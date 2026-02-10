/**
 * Client for the Docker OpenClaw gateway used in integration tests.
 *
 * The OpenClaw gateway is primarily WebSocket-based and has no REST health
 * endpoint. Liveness is determined by checking that the HTTP server responds
 * (any status code, including 404, indicates the server is running).
 */

export const GATEWAY_URL = process.env.GATEWAY_URL || "http://localhost:18789";
export const GATEWAY_TOKEN =
  process.env.OPENCLAW_GATEWAY_TOKEN || "test-gateway-token";

/** Fetch against the Docker OpenClaw gateway with auth header. */
export async function gatewayFetch(
  path: string,
  init?: RequestInit,
): Promise<Response> {
  const url = `${GATEWAY_URL}${path}`;
  return fetch(url, {
    ...init,
    headers: {
      ...init?.headers,
      Authorization: `Bearer ${GATEWAY_TOKEN}`,
    },
  });
}

/**
 * Wait for the gateway HTTP server to become reachable.
 * Any HTTP response (even 404) means the server is alive.
 */
export async function waitForGateway(timeoutMs = 60_000): Promise<void> {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await fetch(`${GATEWAY_URL}/`, {
        signal: AbortSignal.timeout(3000),
      });
      // Any response means the server is up
      if (res.status > 0) return;
    } catch {
      // not ready yet
    }
    await new Promise((r) => setTimeout(r, 2000));
  }
  throw new Error(`Gateway not ready after ${timeoutMs}ms`);
}
