import { readFile, writeFile } from "node:fs/promises";
import YAML from "yaml";

/**
 * Cloudflare tunnel (cloudflared) config management.
 *
 * Manages ingress rules in the cloudflared config.yml to route
 * traffic from tunnel hostnames to local claw ports.
 */
import { type ExecFn, exec as defaultExec } from "../lib/exec.js";

export interface TunnelIngress {
  hostname?: string;
  service: string;
  path?: string;
}

export interface TunnelConfig {
  tunnel: string;
  credentials_file?: string;
  ingress: TunnelIngress[];
  [key: string]: unknown;
}

/**
 * Read the cloudflared config file.
 */
export async function readTunnelConfig(
  configPath: string,
): Promise<TunnelConfig> {
  const content = await readFile(configPath, "utf-8");
  return YAML.parse(content) as TunnelConfig;
}

/**
 * Write the cloudflared config file.
 */
export async function writeTunnelConfig(
  configPath: string,
  config: TunnelConfig,
): Promise<void> {
  const content = YAML.stringify(config, { lineWidth: 0 });
  await writeFile(configPath, content, "utf-8");
}

/**
 * Add an ingress rule for a claw to the cloudflared config.
 * The rule is inserted before the catch-all (last) rule.
 */
export async function addRoute(
  configPath: string,
  hostname: string,
  localPort: number,
): Promise<void> {
  const config = await readTunnelConfig(configPath);

  // Check if route already exists
  if (config.ingress.some((r) => r.hostname === hostname)) {
    console.log(`[tunnel] Route for ${hostname} already exists, updating`);
    config.ingress = config.ingress.map((r) =>
      r.hostname === hostname
        ? { hostname, service: `http://localhost:${localPort}` }
        : r,
    );
  } else {
    // Insert before the catch-all rule (always the last one, has no hostname)
    const catchAll = config.ingress[config.ingress.length - 1];
    const hasCatchAll = catchAll && !catchAll.hostname;

    if (hasCatchAll) {
      config.ingress.splice(config.ingress.length - 1, 0, {
        hostname,
        service: `http://localhost:${localPort}`,
      });
    } else {
      // No catch-all, just append and add one
      config.ingress.push({
        hostname,
        service: `http://localhost:${localPort}`,
      });
      config.ingress.push({ service: "http_status:404" });
    }
  }

  await writeTunnelConfig(configPath, config);
  console.log(`[tunnel] Added route: ${hostname} → localhost:${localPort}`);
}

/**
 * Remove an ingress rule for a claw from the cloudflared config.
 */
export async function removeRoute(
  configPath: string,
  hostname: string,
): Promise<void> {
  const config = await readTunnelConfig(configPath);
  config.ingress = config.ingress.filter((r) => r.hostname !== hostname);

  // Ensure there's always a catch-all
  const last = config.ingress[config.ingress.length - 1];
  if (!last || last.hostname) {
    config.ingress.push({ service: "http_status:404" });
  }

  await writeTunnelConfig(configPath, config);
  console.log(`[tunnel] Removed route: ${hostname}`);
}

/**
 * Check if a route exists for a given hostname.
 */
export async function hasRoute(
  configPath: string,
  hostname: string,
): Promise<boolean> {
  const config = await readTunnelConfig(configPath);
  return config.ingress.some((r) => r.hostname === hostname);
}

/**
 * Restart cloudflared to pick up config changes.
 */
export async function restartCloudflared(
  execFn: ExecFn = defaultExec,
): Promise<void> {
  console.log("[tunnel] Restarting cloudflared...");
  await execFn("launchctl", ["stop", "com.cloudflare.cloudflared"], {
    sudo: true,
  });
  // Give it a moment to stop
  await new Promise((resolve) => setTimeout(resolve, 2000));
  await execFn("launchctl", ["start", "com.cloudflare.cloudflared"], {
    sudo: true,
  });
  console.log("[tunnel] cloudflared restarted");
}

/**
 * Get the number of active (non-catch-all) ingress routes.
 */
export async function getRouteCount(configPath: string): Promise<number> {
  const config = await readTunnelConfig(configPath);
  return config.ingress.filter((r) => r.hostname).length;
}
