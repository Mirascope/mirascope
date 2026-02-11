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
