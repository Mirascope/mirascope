/**
 * Gateway URL utilities and reachability checks.
 */

/**
 * Convert a WebSocket gateway URL to its HTTP equivalent.
 * ws:// → http://, wss:// → https://
 */
export function gatewayToHttpUrl(wsUrl: string): string {
  return wsUrl.replace(/^ws(s?):\/\//, "http$1://");
}

/**
 * Check if the gateway's HTTP endpoint is reachable.
 * The OpenClaw gateway serves its Control UI over HTTP on the same port.
 */
export async function checkGatewayReachable(
  httpUrl: string,
  timeoutMs = 5000,
): Promise<boolean> {
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    const res = await fetch(httpUrl, {
      signal: controller.signal,
      redirect: "follow",
    });
    clearTimeout(timer);
    // Any response (even 404) means the server is up
    return res.status > 0;
  } catch {
    return false;
  }
}
