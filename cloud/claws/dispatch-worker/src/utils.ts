/**
 * Extract clawId from the Host header.
 *
 * The Mirascope Cloud backend (LiveCloudflareContainerService) sets
 * Host: {clawId}.claws.mirascope.com when making requests.
 */
export function extractClawId(host: string): string | null {
  // Expected: {clawId}.claws.mirascope.com
  const parts = host.split(".");
  if (parts.length < 2) return null;
  return parts[0] || null;
}

/**
 * Derive a user-facing hint from a gateway startup error message.
 *
 * Helps users diagnose common failures (missing API keys, OOM, crashes)
 * without reading raw container logs.
 */
export function startupErrorHint(message: string): string | undefined {
  if (/api.?key/i.test(message) || /unauthorized/i.test(message)) {
    return "Check that the provider API key is set correctly in Claw settings.";
  }
  if (/oom|out of memory/i.test(message)) {
    return "The container ran out of memory. Try reducing concurrency or upgrading the instance type.";
  }
  if (/econnrefused|connection refused/i.test(message)) {
    return "Gateway process started but refused connections — it may have crashed on startup.";
  }
  return undefined;
}
