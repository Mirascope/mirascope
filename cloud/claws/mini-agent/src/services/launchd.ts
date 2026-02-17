import { writeFile } from "node:fs/promises";

/**
 * launchd plist management for claw gateway services.
 */
import { type ExecFn, exec as defaultExec } from "../lib/exec.js";

const PLIST_DIR = "/Library/LaunchDaemons";

function plistLabel(macUsername: string): string {
  return `com.mirascope.claw.${macUsername}`;
}

function plistPath(macUsername: string): string {
  return `${PLIST_DIR}/${plistLabel(macUsername)}.plist`;
}

export interface LaunchdConfig {
  macUsername: string;
  localPort: number;
  gatewayToken: string;
  envVars?: Record<string, string>;
}

/**
 * Generate the launchd plist XML for a claw gateway.
 */
export function generatePlist(config: LaunchdConfig): string {
  const label = plistLabel(config.macUsername);
  const homeDir = `/Users/${config.macUsername}`;

  // Build environment variables dict
  const envEntries = [
    ["PORT", String(config.localPort)],
    ["OPENCLAW_HOME", `${homeDir}/.openclaw`],
    ...(config.envVars ? Object.entries(config.envVars) : []),
  ];

  const envXml = envEntries
    .map(
      ([k, v]) =>
        `            <key>${escapeXml(k)}</key>\n            <string>${escapeXml(v)}</string>`,
    )
    .join("\n");

  return `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${escapeXml(label)}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/openclaw</string>
        <string>gateway</string>
        <string>start</string>
    </array>
    <key>UserName</key>
    <string>${escapeXml(config.macUsername)}</string>
    <key>WorkingDirectory</key>
    <string>${escapeXml(homeDir)}/.openclaw/workspace</string>
    <key>EnvironmentVariables</key>
    <dict>
${envXml}
    </dict>
    <key>KeepAlive</key>
    <true/>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>${escapeXml(homeDir)}/.openclaw/logs/gateway.log</string>
    <key>StandardErrorPath</key>
    <string>${escapeXml(homeDir)}/.openclaw/logs/gateway.err</string>
    <key>ThrottleInterval</key>
    <integer>5</integer>
</dict>
</plist>`;
}

/**
 * Install and load a launchd plist for a claw.
 */
export async function installAndLoad(
  config: LaunchdConfig,
  execFn: ExecFn = defaultExec,
): Promise<void> {
  const plist = generatePlist(config);
  const path = plistPath(config.macUsername);

  // Write plist file
  const tmpPath = `/tmp/mini-agent-plist-${Date.now()}`;
  await writeFile(tmpPath, plist, "utf-8");
  await execFn("mv", [tmpPath, path], { sudo: true });
  await execFn("chmod", ["644", path], { sudo: true });
  await execFn("chown", ["root:wheel", path], { sudo: true });

  // Load the service
  const result = await execFn("launchctl", ["load", path], { sudo: true });
  if (result.exitCode !== 0) {
    throw new Error(`Failed to load launchd service: ${result.stderr}`);
  }
}

/**
 * Stop and unload a claw's launchd service.
 */
export async function stopAndUnload(
  macUsername: string,
  execFn: ExecFn = defaultExec,
): Promise<void> {
  const label = plistLabel(macUsername);
  const path = plistPath(macUsername);

  // Try to stop first
  await execFn("launchctl", ["stop", label], { sudo: true });

  // Unload
  const result = await execFn("launchctl", ["unload", path], { sudo: true });
  if (result.exitCode !== 0) {
    console.warn(
      `[launchd] Warning: unload failed for ${label}: ${result.stderr}`,
    );
  }

  // Remove plist file
  try {
    await execFn("rm", ["-f", path], { sudo: true });
  } catch {
    // Ignore cleanup errors
  }
}

/**
 * Restart a claw's gateway using launchctl kickstart.
 */
export async function restart(
  macUsername: string,
  execFn: ExecFn = defaultExec,
): Promise<void> {
  const label = plistLabel(macUsername);
  const result = await execFn(
    "launchctl",
    ["kickstart", "-k", `system/${label}`],
    { sudo: true },
  );
  if (result.exitCode !== 0) {
    throw new Error(`Failed to restart ${label}: ${result.stderr}`);
  }
}

/**
 * Get the launchd status of a claw service.
 */
export async function getStatus(
  macUsername: string,
  execFn: ExecFn = defaultExec,
): Promise<"loaded" | "unloaded" | "error"> {
  const label = plistLabel(macUsername);
  const result = await execFn("launchctl", ["list", label], { sudo: true });

  if (result.exitCode !== 0) {
    return "unloaded";
  }

  // Check if there's an error status
  const statusMatch = result.stdout.match(/"LastExitStatus"\s*=\s*(\d+)/);
  if (statusMatch && parseInt(statusMatch[1]!, 10) !== 0) {
    return "error";
  }

  return "loaded";
}

/**
 * Get the PID of a running claw gateway.
 */
export async function getPid(
  macUsername: string,
  execFn: ExecFn = defaultExec,
): Promise<number | null> {
  const label = plistLabel(macUsername);
  const result = await execFn("launchctl", ["list", label], { sudo: true });

  if (result.exitCode !== 0) return null;

  const pidMatch = result.stdout.match(/"PID"\s*=\s*(\d+)/);
  if (pidMatch) return parseInt(pidMatch[1]!, 10);

  // Also try the tabular format: PID\tStatus\tLabel
  const lines = result.stdout.trim().split("\n");
  for (const line of lines) {
    const parts = line.split("\t");
    if (parts.length >= 3 && parts[2] === label && parts[0] !== "-") {
      return parseInt(parts[0]!, 10);
    }
  }

  return null;
}

function escapeXml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}
