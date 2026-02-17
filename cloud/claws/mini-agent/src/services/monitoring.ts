/**
 * Per-claw resource monitoring.
 */
import { type ExecFn, exec as defaultExec } from "../lib/exec.js";

export interface ClawResourceUsage {
  memoryUsageMb: number | null;
  gatewayPid: number | null;
  gatewayUptime: number | null;
  chromiumPid: number | null;
  processCount: number;
}

/**
 * Get resource usage for a specific claw user.
 */
export async function getClawResources(
  macUsername: string,
  execFn: ExecFn = defaultExec,
): Promise<ClawResourceUsage> {
  // Get all processes for this user
  const result = await execFn("ps", [
    "-u",
    macUsername,
    "-o",
    "pid,rss,etime,comm",
  ]);

  if (result.exitCode !== 0) {
    return {
      memoryUsageMb: null,
      gatewayPid: null,
      gatewayUptime: null,
      chromiumPid: null,
      processCount: 0,
    };
  }

  const lines = result.stdout.trim().split("\n").slice(1); // skip header
  let totalRss = 0;
  let gatewayPid: number | null = null;
  let gatewayUptime: number | null = null;
  let chromiumPid: number | null = null;

  for (const line of lines) {
    const parts = line.trim().split(/\s+/);
    if (parts.length < 4) continue;

    const pid = parseInt(parts[0]!, 10);
    const rss = parseInt(parts[1]!, 10); // KB
    const etime = parts[2]!;
    const comm = parts.slice(3).join(" ");

    totalRss += rss;

    if (comm.includes("openclaw") || comm.includes("gateway")) {
      gatewayPid = pid;
      gatewayUptime = parseEtime(etime);
    }

    if (
      comm.includes("Chromium") ||
      comm.includes("chromium") ||
      comm.includes("chrome")
    ) {
      chromiumPid = pid;
    }
  }

  return {
    memoryUsageMb: Math.round(totalRss / 1024),
    gatewayPid,
    gatewayUptime,
    chromiumPid,
    processCount: lines.length,
  };
}

/**
 * Get disk usage for a user's home directory in MB.
 */
export async function getClawDiskUsage(
  macUsername: string,
  execFn: ExecFn = defaultExec,
): Promise<number | null> {
  const result = await execFn("du", ["-sm", `/Users/${macUsername}`], {
    sudo: true,
  });
  if (result.exitCode !== 0) return null;

  const match = result.stdout.match(/^(\d+)/);
  return match ? parseInt(match[1]!, 10) : null;
}

/**
 * Parse ps etime format (e.g., "01:23:45" or "1-02:03:04") to seconds.
 */
function parseEtime(etime: string): number {
  // Format: [[dd-]hh:]mm:ss
  let days = 0;
  let rest = etime;

  const dayMatch = rest.match(/^(\d+)-/);
  if (dayMatch) {
    days = parseInt(dayMatch[1]!, 10);
    rest = rest.slice(dayMatch[0].length);
  }

  const parts = rest.split(":").map((p) => parseInt(p, 10));

  if (parts.length === 3) {
    return days * 86400 + parts[0]! * 3600 + parts[1]! * 60 + parts[2]!;
  } else if (parts.length === 2) {
    return days * 86400 + parts[0]! * 60 + parts[1]!;
  }

  return 0;
}
