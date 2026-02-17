/**
 * Cloudflare tunnel config management service.
 */
import { readFile, writeFile } from "node:fs/promises";

import { Context, Effect } from "effect";
import YAML from "yaml";

import { ExecError, SystemError } from "../errors.js";
import { Exec } from "./exec.js";

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

export class Tunnel extends Context.Tag("Tunnel")<
  Tunnel,
  {
    readonly addRoute: (
      configPath: string,
      hostname: string,
      localPort: number,
    ) => Effect.Effect<void, SystemError>;
    readonly removeRoute: (
      configPath: string,
      hostname: string,
    ) => Effect.Effect<void, SystemError>;
    readonly hasRoute: (
      configPath: string,
      hostname: string,
    ) => Effect.Effect<boolean, SystemError>;
    readonly getRouteCount: (
      configPath: string,
    ) => Effect.Effect<number, SystemError>;
    readonly restartCloudflared: () => Effect.Effect<void, ExecError>;
    readonly readTunnelConfig: (
      configPath: string,
    ) => Effect.Effect<TunnelConfig, SystemError>;
  }
>() {}

// Pure functions for tunnel config manipulation (exported for testing)
export function readTunnelConfigSync(content: string): TunnelConfig {
  return YAML.parse(content) as TunnelConfig;
}

export function writeTunnelConfigSync(config: TunnelConfig): string {
  return YAML.stringify(config, { lineWidth: 0 });
}

export async function readTunnelConfigFromFile(
  configPath: string,
): Promise<TunnelConfig> {
  const content = await readFile(configPath, "utf-8");
  return YAML.parse(content) as TunnelConfig;
}

export async function writeTunnelConfigToFile(
  configPath: string,
  config: TunnelConfig,
): Promise<void> {
  const content = YAML.stringify(config, { lineWidth: 0 });
  await writeFile(configPath, content, "utf-8");
}

export async function addRouteToConfig(
  configPath: string,
  hostname: string,
  localPort: number,
): Promise<void> {
  const config = await readTunnelConfigFromFile(configPath);

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

  await writeTunnelConfigToFile(configPath, config);
}

export async function removeRouteFromConfig(
  configPath: string,
  hostname: string,
): Promise<void> {
  const config = await readTunnelConfigFromFile(configPath);
  config.ingress = config.ingress.filter((r) => r.hostname !== hostname);

  const last = config.ingress[config.ingress.length - 1];
  if (!last || last.hostname) {
    config.ingress.push({ service: "http_status:404" });
  }

  await writeTunnelConfigToFile(configPath, config);
}

export async function hasRouteInConfig(
  configPath: string,
  hostname: string,
): Promise<boolean> {
  const config = await readTunnelConfigFromFile(configPath);
  return config.ingress.some((r) => r.hostname === hostname);
}

export async function getRouteCountFromConfig(
  configPath: string,
): Promise<number> {
  const config = await readTunnelConfigFromFile(configPath);
  return config.ingress.filter((r) => r.hostname).length;
}

export const TunnelLive = Effect.gen(function* () {
  const exec = yield* Exec;

  const addRoute = (
    configPath: string,
    hostname: string,
    localPort: number,
  ): Effect.Effect<void, SystemError> =>
    Effect.tryPromise({
      try: () => addRouteToConfig(configPath, hostname, localPort),
      catch: (e) =>
        new SystemError({
          message: `Failed to add tunnel route: ${hostname}`,
          cause: e,
        }),
    });

  const removeRoute = (
    configPath: string,
    hostname: string,
  ): Effect.Effect<void, SystemError> =>
    Effect.tryPromise({
      try: () => removeRouteFromConfig(configPath, hostname),
      catch: (e) =>
        new SystemError({
          message: `Failed to remove tunnel route: ${hostname}`,
          cause: e,
        }),
    });

  const hasRoute = (
    configPath: string,
    hostname: string,
  ): Effect.Effect<boolean, SystemError> =>
    Effect.tryPromise({
      try: () => hasRouteInConfig(configPath, hostname),
      catch: (e) =>
        new SystemError({ message: `Failed to check route`, cause: e }),
    });

  const getRouteCount = (
    configPath: string,
  ): Effect.Effect<number, SystemError> =>
    Effect.tryPromise({
      try: () => getRouteCountFromConfig(configPath),
      catch: (e) =>
        new SystemError({
          message: `Failed to get route count`,
          cause: e,
        }),
    });

  const restartCloudflared = (): Effect.Effect<void, ExecError> =>
    Effect.gen(function* () {
      yield* exec.run("launchctl", ["stop", "com.cloudflare.cloudflared"], {
        sudo: true,
      });
      yield* Effect.sleep("2 seconds");
      yield* exec.run("launchctl", ["start", "com.cloudflare.cloudflared"], {
        sudo: true,
      });
    });

  const readTunnelConfig = (
    configPath: string,
  ): Effect.Effect<TunnelConfig, SystemError> =>
    Effect.tryPromise({
      try: () => readTunnelConfigFromFile(configPath),
      catch: (e) =>
        new SystemError({
          message: `Failed to read tunnel config`,
          cause: e,
        }),
    });

  return {
    addRoute,
    removeRoute,
    hasRoute,
    getRouteCount,
    restartCloudflared,
    readTunnelConfig,
  };
});
