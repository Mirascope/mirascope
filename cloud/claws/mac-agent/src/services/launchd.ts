/**
 * launchd plist management service.
 */
import { writeFile } from "node:fs/promises";

import { Context, Effect } from "effect";

import { ExecError } from "../errors.js";
import { Exec } from "./exec.js";

const PLIST_DIR = "/Library/LaunchDaemons";

function plistLabel(macUsername: string): string {
  return `com.mirascope.claw.${macUsername}`;
}

function plistPath(macUsername: string): string {
  return `${PLIST_DIR}/${plistLabel(macUsername)}.plist`;
}

export interface LaunchdConfig {
  readonly macUsername: string;
  readonly localPort: number;
  readonly gatewayToken: string;
  readonly envVars?: Record<string, string>;
}

export class Launchd extends Context.Tag("Launchd")<
  Launchd,
  {
    readonly installAndLoad: (
      config: LaunchdConfig,
    ) => Effect.Effect<void, ExecError>;
    readonly stopAndUnload: (
      macUsername: string,
    ) => Effect.Effect<void, ExecError>;
    readonly restart: (macUsername: string) => Effect.Effect<void, ExecError>;
    readonly getStatus: (
      macUsername: string,
    ) => Effect.Effect<"loaded" | "unloaded" | "error", ExecError>;
    readonly getPid: (
      macUsername: string,
    ) => Effect.Effect<number | null, ExecError>;
  }
>() {}

function escapeXml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

export function generatePlist(config: LaunchdConfig): string {
  const label = plistLabel(config.macUsername);
  const homeDir = `/Users/${config.macUsername}`;

  const envEntries = [
    ["PORT", String(config.localPort)],
    ["OPENCLAW_HOME", `${homeDir}/.openclaw`],
    ...(config.envVars ? Object.entries(config.envVars) : []),
  ];

  const envXml = envEntries
    .map(
      ([k, v]) =>
        `            <key>${escapeXml(k!)}</key>\n            <string>${escapeXml(v!)}</string>`,
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

export const LaunchdLive = Effect.gen(function* () {
  const exec = yield* Exec;

  const installAndLoad = (
    config: LaunchdConfig,
  ): Effect.Effect<void, ExecError> =>
    Effect.gen(function* () {
      const plist = generatePlist(config);
      const path = plistPath(config.macUsername);

      const tmpPath = `/tmp/mac-agent-plist-${Date.now()}`;
      yield* Effect.tryPromise({
        try: () => writeFile(tmpPath, plist, "utf-8"),
        catch: (e) =>
          new ExecError({
            message: `Failed to write plist`,
            command: "writeFile",
            exitCode: -1,
            stderr: String(e),
          }),
      });
      yield* exec.runUnsafe("mv", [tmpPath, path], { sudo: true });
      yield* exec.runUnsafe("chmod", ["644", path], { sudo: true });
      yield* exec.runUnsafe("chown", ["root:wheel", path], { sudo: true });
      yield* exec.runUnsafe("launchctl", ["load", path], { sudo: true });
    });

  const stopAndUnload = (
    macUsername: string,
  ): Effect.Effect<void, ExecError> =>
    Effect.gen(function* () {
      const label = plistLabel(macUsername);
      const path = plistPath(macUsername);

      yield* exec.run("launchctl", ["stop", label], { sudo: true });
      yield* exec.run("launchctl", ["unload", path], { sudo: true });
      yield* exec
        .run("rm", ["-f", path], { sudo: true })
        .pipe(Effect.catchAll(() => Effect.void));
    });

  const restart = (macUsername: string): Effect.Effect<void, ExecError> =>
    Effect.gen(function* () {
      const label = plistLabel(macUsername);
      yield* exec.runUnsafe(
        "launchctl",
        ["kickstart", "-k", `system/${label}`],
        { sudo: true },
      );
    });

  const getStatus = (
    macUsername: string,
  ): Effect.Effect<"loaded" | "unloaded" | "error", ExecError> =>
    Effect.gen(function* () {
      const label = plistLabel(macUsername);
      const result = yield* exec.run("launchctl", ["list", label], {
        sudo: true,
      });

      if (result.exitCode !== 0) return "unloaded" as const;

      const statusMatch = result.stdout.match(
        /"LastExitStatus"\s*=\s*(\d+)/,
      );
      if (statusMatch && parseInt(statusMatch[1]!, 10) !== 0) {
        return "error" as const;
      }

      return "loaded" as const;
    });

  const getPid = (
    macUsername: string,
  ): Effect.Effect<number | null, ExecError> =>
    Effect.gen(function* () {
      const label = plistLabel(macUsername);
      const result = yield* exec.run("launchctl", ["list", label], {
        sudo: true,
      });

      if (result.exitCode !== 0) return null;

      const pidMatch = result.stdout.match(/"PID"\s*=\s*(\d+)/);
      if (pidMatch) return parseInt(pidMatch[1]!, 10);

      const lines = result.stdout.trim().split("\n");
      for (const line of lines) {
        const parts = line.split("\t");
        if (parts.length >= 3 && parts[2] === label && parts[0] !== "-") {
          return parseInt(parts[0]!, 10);
        }
      }

      return null;
    });

  return { installAndLoad, stopAndUnload, restart, getStatus, getPid };
});
