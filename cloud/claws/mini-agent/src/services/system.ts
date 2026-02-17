/**
 * System monitoring service — CPU, memory, disk stats.
 */
import os from "node:os";

import { Context, Effect } from "effect";

import { ExecError, SystemError } from "../errors.js";
import { Exec } from "./exec.js";

export interface SystemStats {
  readonly hostname: string;
  readonly uptime: number;
  readonly cpu: { readonly usage: number; readonly cores: number };
  readonly memory: { readonly usedGb: number; readonly totalGb: number };
  readonly disk: { readonly usedGb: number; readonly totalGb: number };
  readonly loadAverage: [number, number, number];
}

export class System extends Context.Tag("System")<
  System,
  {
    readonly getSystemStats: () => Effect.Effect<
      SystemStats,
      ExecError | SystemError
    >;
  }
>() {}

export const SystemLive = Effect.gen(function* () {
  const exec = yield* Exec;

  const getSystemStats = (): Effect.Effect<
    SystemStats,
    ExecError | SystemError
  > =>
    Effect.gen(function* () {
      const hostname = os.hostname();
      const uptime = os.uptime();
      const cores = os.cpus().length;
      const loadAverage = os.loadavg() as [number, number, number];

      const totalMem = os.totalmem();
      const freeMem = os.freemem();
      const usedMem = totalMem - freeMem;

      // Get disk usage
      let diskUsedGb = 0;
      let diskTotalGb = 0;
      const dfResult = yield* exec.run("df", ["-g", "/"]);
      if (dfResult.exitCode === 0) {
        const lines = dfResult.stdout.trim().split("\n");
        if (lines.length >= 2) {
          const parts = lines[1]!.split(/\s+/);
          diskTotalGb = parseInt(parts[1] ?? "0", 10);
          diskUsedGb = parseInt(parts[2] ?? "0", 10);
        }
      }

      // Get CPU usage
      let cpuUsage = loadAverage[0] / cores;
      const topResult = yield* exec.run("top", [
        "-l",
        "1",
        "-n",
        "0",
        "-s",
        "0",
      ]);
      if (topResult.exitCode === 0) {
        const cpuLine = topResult.stdout
          .split("\n")
          .find((l) => l.includes("CPU usage"));
        if (cpuLine) {
          const idleMatch = cpuLine.match(/([\d.]+)%\s*idle/);
          if (idleMatch) {
            cpuUsage = (100 - parseFloat(idleMatch[1]!)) / 100;
          }
        }
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
    });

  return { getSystemStats };
});
