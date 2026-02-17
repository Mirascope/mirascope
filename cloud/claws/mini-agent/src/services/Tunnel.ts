/**
 * Cloudflare tunnel (cloudflared) config management service.
 */
import { readFile, writeFile } from "node:fs/promises";

import { Context, Effect, Layer } from "effect";
import YAML from "yaml";

import { Exec } from "../Exec.js";

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

export interface TunnelService {
  readonly readConfig: (configPath: string) => Effect.Effect<TunnelConfig>;
  readonly addRoute: (
    configPath: string,
    hostname: string,
    localPort: number,
  ) => Effect.Effect<void>;
  readonly removeRoute: (
    configPath: string,
    hostname: string,
  ) => Effect.Effect<void>;
  readonly hasRoute: (
    configPath: string,
    hostname: string,
  ) => Effect.Effect<boolean>;
  readonly getRouteCount: (configPath: string) => Effect.Effect<number>;
  readonly restartCloudflared: () => Effect.Effect<void>;
}

export class Tunnel extends Context.Tag("MiniAgent/Tunnel")<
  Tunnel,
  TunnelService
>() {}

export const TunnelLive = Layer.effect(
  Tunnel,
  Effect.gen(function* () {
    const exec = yield* Exec;

    const readTunnelConfig = (configPath: string) =>
      Effect.promise(async () => {
        const content = await readFile(configPath, "utf-8");
        return YAML.parse(content) as TunnelConfig;
      });

    const writeTunnelConfig = (configPath: string, config: TunnelConfig) =>
      Effect.promise(async () => {
        const content = YAML.stringify(config, { lineWidth: 0 });
        await writeFile(configPath, content, "utf-8");
      });

    return {
      readConfig: readTunnelConfig,

      addRoute: (configPath, hostname, localPort) =>
        Effect.gen(function* () {
          const config = yield* readTunnelConfig(configPath);

          if (config.ingress.some((r) => r.hostname === hostname)) {
            config.ingress = config.ingress.map((r) =>
              r.hostname === hostname
                ? { hostname, service: `http://localhost:${localPort}` }
                : r,
            );
          } else {
            const catchAll = config.ingress[config.ingress.length - 1];
            const hasCatchAll = catchAll && !catchAll.hostname;

            if (hasCatchAll) {
              config.ingress.splice(config.ingress.length - 1, 0, {
                hostname,
                service: `http://localhost:${localPort}`,
              });
            } else {
              config.ingress.push({
                hostname,
                service: `http://localhost:${localPort}`,
              });
              config.ingress.push({ service: "http_status:404" });
            }
          }

          yield* writeTunnelConfig(configPath, config);
          console.log(
            `[tunnel] Added route: ${hostname} → localhost:${localPort}`,
          );
        }),

      removeRoute: (configPath, hostname) =>
        Effect.gen(function* () {
          const config = yield* readTunnelConfig(configPath);
          config.ingress = config.ingress.filter(
            (r) => r.hostname !== hostname,
          );

          const last = config.ingress[config.ingress.length - 1];
          if (!last || last.hostname) {
            config.ingress.push({ service: "http_status:404" });
          }

          yield* writeTunnelConfig(configPath, config);
          console.log(`[tunnel] Removed route: ${hostname}`);
        }),

      hasRoute: (configPath, hostname) =>
        Effect.gen(function* () {
          const config = yield* readTunnelConfig(configPath);
          return config.ingress.some((r) => r.hostname === hostname);
        }),

      getRouteCount: (configPath) =>
        Effect.gen(function* () {
          const config = yield* readTunnelConfig(configPath);
          return config.ingress.filter((r) => r.hostname).length;
        }),

      restartCloudflared: () =>
        Effect.gen(function* () {
          console.log("[tunnel] Restarting cloudflared...");
          yield* exec.run(
            "launchctl",
            ["stop", "com.cloudflare.cloudflared"],
            { sudo: true },
          );
          yield* Effect.sleep("2 seconds");
          yield* exec.run(
            "launchctl",
            ["start", "com.cloudflare.cloudflared"],
            { sudo: true },
          );
          console.log("[tunnel] cloudflared restarted");
        }),
    };
  }),
);
