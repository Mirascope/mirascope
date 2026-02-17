/**
 * Per-claw resource monitoring service.
 */
import { Context, Effect, Layer } from "effect";

import { Exec } from "../Exec.js";

export interface ClawResourceUsage {
  readonly memoryUsageMb: number | null;
  readonly gatewayPid: number | null;
  readonly gatewayUptime: number | null;
  readonly chromiumPid: number | null;
  readonly processCount: number;
}

export interface MonitoringService {
  readonly getClawResources: (
    macUsername: string,
  ) => Effect.Effect<ClawResourceUsage>;
  readonly getClawDiskUsage: (
    macUsername: string,
  ) => Effect.Effect<number | null>;
}

export class Monitoring extends Context.Tag("MiniAgent/Monitoring")<
  Monitoring,
  MonitoringService
>() {}

export const MonitoringLive = Layer.effect(
  Monitoring,
  Effect.gen(function* () {
    const exec = yield* Exec;

    return {
      getClawResources: (macUsername: string) =>
        Effect.gen(function* () {
          const result = yield* exec.run("ps", [
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

          const lines = result.stdout.trim().split("\n").slice(1);
          let totalRss = 0;
          let gatewayPid: number | null = null;
          let gatewayUptime: number | null = null;
          let chromiumPid: number | null = null;

          for (const line of lines) {
            const parts = line.trim().split(/\s+/);
            if (parts.length < 4) continue;

            const pid = parseInt(parts[0]!, 10);
            const rss = parseInt(parts[1]!, 10);
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
        }),

      getClawDiskUsage: (macUsername: string) =>
        Effect.gen(function* () {
          const result = yield* exec.run(
            "du",
            ["-sm", `/Users/${macUsername}`],
            { sudo: true },
          );
          if (result.exitCode !== 0) return null;

          const match = result.stdout.match(/^(\d+)/);
          return match ? parseInt(match[1]!, 10) : null;
        }),
    };
  }),
);

function parseEtime(etime: string): number {
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
