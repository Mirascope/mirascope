import os from "node:os";

/**
 * System monitoring — CPU, memory, disk stats.
 */
import { exec, type ExecFn } from "../lib/exec.js";

export interface SystemStats {
  hostname: string;
  uptime: number;
  cpu: { usage: number; cores: number };
  memory: { usedGb: number; totalGb: number };
  disk: { usedGb: number; totalGb: number };
  loadAverage: [number, number, number];
}

export async function getSystemStats(
  execFn: ExecFn = exec,
): Promise<SystemStats> {
  const hostname = os.hostname();
  const uptime = os.uptime();
  const cores = os.cpus().length;
  const loadAverage = os.loadavg() as [number, number, number];

  const totalMem = os.totalmem();
  const freeMem = os.freemem();
  const usedMem = totalMem - freeMem;

  // Get disk usage for /
  let diskUsedGb = 0;
  let diskTotalGb = 0;
  try {
    const result = await execFn("df", ["-g", "/"]);
    if (result.exitCode === 0) {
      const lines = result.stdout.trim().split("\n");
      if (lines.length >= 2) {
        const parts = lines[1]!.split(/\s+/);
        diskTotalGb = parseInt(parts[1] ?? "0", 10);
        diskUsedGb = parseInt(parts[2] ?? "0", 10);
      }
    }
  } catch {
    // Ignore disk errors
  }

  // Get CPU usage via vm_stat or top snapshot
  let cpuUsage = loadAverage[0] / cores; // rough estimate from load average
  try {
    const result = await execFn("top", ["-l", "1", "-n", "0", "-s", "0"]);
    if (result.exitCode === 0) {
      const cpuLine = result.stdout
        .split("\n")
        .find((l) => l.includes("CPU usage"));
      if (cpuLine) {
        const idleMatch = cpuLine.match(/([\d.]+)%\s*idle/);
        if (idleMatch) {
          cpuUsage = (100 - parseFloat(idleMatch[1]!)) / 100;
        }
      }
    }
  } catch {
    // Fall back to load average estimate
  }

  return {
    hostname,
    uptime,
    cpu: { usage: Math.round(cpuUsage * 100) / 100, cores },
    memory: {
      usedGb: Math.round((usedMem / 1024 / 1024 / 1024) * 100) / 100,
      totalGb: Math.round((totalMem / 1024 / 1024 / 1024) * 100) / 100,
    },
    disk: { usedGb: diskUsedGb, totalGb: diskTotalGb },
    loadAverage,
  };
}
