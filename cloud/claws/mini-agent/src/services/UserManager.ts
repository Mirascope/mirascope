/**
 * macOS user creation/deletion service.
 */
import { randomBytes } from "node:crypto";
import { writeFile } from "node:fs/promises";
import path from "node:path";

import { Context, Effect, Layer } from "effect";

import { Exec } from "../Exec.js";

const ZSHRC_TEMPLATE = `
# Mirascope Claw user profile
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

# Node.js
export PATH="/opt/homebrew/opt/node/bin:$PATH"

# Playwright
export PLAYWRIGHT_BROWSERS_PATH="/opt/homebrew/var/playwright"
`.trim();

export interface CreateUserOptions {
  readonly macUsername: string;
  readonly clawId: string;
  readonly localPort: number;
  readonly gatewayToken: string;
  readonly tunnelHostname: string;
  readonly envVars: Record<string, string>;
}

export interface UserManagerService {
  readonly createClawUser: (options: CreateUserOptions) => Effect.Effect<void>;
  readonly deleteClawUser: (macUsername: string) => Effect.Effect<void>;
  readonly userExists: (macUsername: string) => Effect.Effect<boolean>;
  readonly listClawUsers: () => Effect.Effect<string[]>;
}

export class UserManager extends Context.Tag("MiniAgent/UserManager")<
  UserManager,
  UserManagerService
>() {}

export const UserManagerLive = Layer.effect(
  UserManager,
  Effect.gen(function* () {
    const exec = yield* Exec;

    const writeFileAsSudo = (
      filePath: string,
      content: string,
      owner: string,
    ) =>
      Effect.gen(function* () {
        const tmpPath = `/tmp/mini-agent-${Date.now()}-${Math.random().toString(36).slice(2)}`;
        yield* Effect.promise(() => writeFile(tmpPath, content, "utf-8"));
        yield* exec.run("mv", [tmpPath, filePath], { sudo: true });
        yield* exec.run("chown", [`${owner}:staff`, filePath], {
          sudo: true,
        });
      });

    return {
      createClawUser: (options: CreateUserOptions) =>
        Effect.gen(function* () {
          const { macUsername, clawId, localPort, gatewayToken, envVars } =
            options;
          const homeDir = `/Users/${macUsername}`;
          const password = randomBytes(32).toString("hex");

          // 1. Create macOS user
          const createResult = yield* exec.run(
            "sysadminctl",
            [
              "-addUser",
              macUsername,
              "-fullName",
              `Claw ${clawId}`,
              "-password",
              password,
              "-home",
              homeDir,
              "-shell",
              "/bin/zsh",
            ],
            { sudo: true, timeout: 30_000 },
          );

          if (createResult.exitCode !== 0) {
            yield* Effect.die(
              `Failed to create user ${macUsername}: ${createResult.stderr}`,
            );
          }

          // 2. Lock down home directory
          yield* exec.run("chmod", ["700", homeDir], { sudo: true });

          // 3. Write .zshrc
          yield* writeFileAsSudo(
            path.join(homeDir, ".zshrc"),
            ZSHRC_TEMPLATE,
            macUsername,
          );

          // 4. Create .openclaw directories
          const openclawDir = path.join(homeDir, ".openclaw");
          const workspaceDir = path.join(openclawDir, "workspace");
          const logsDir = path.join(openclawDir, "logs");

          yield* exec.run("mkdir", ["-p", workspaceDir, logsDir], {
            sudoUser: macUsername,
          });

          // 5. Write openclaw.json
          const openclawConfig = {
            gateway: {
              host: "127.0.0.1",
              port: localPort,
              token: gatewayToken,
            },
          };
          yield* writeFileAsSudo(
            path.join(openclawDir, "openclaw.json"),
            JSON.stringify(openclawConfig, null, 2),
            macUsername,
          );

          // 6. Write .env with injected environment variables
          if (Object.keys(envVars).length > 0) {
            const envContent = Object.entries(envVars)
              .map(([k, v]) => `${k}=${v}`)
              .join("\n");
            yield* writeFileAsSudo(
              path.join(openclawDir, ".env"),
              envContent,
              macUsername,
            );
          }
        }),

      deleteClawUser: (macUsername: string) =>
        Effect.gen(function* () {
          const result = yield* exec.run(
            "sysadminctl",
            ["-deleteUser", macUsername, "-secure"],
            { sudo: true, timeout: 60_000 },
          );

          if (result.exitCode !== 0) {
            yield* Effect.die(
              `Failed to delete user ${macUsername}: ${result.stderr}`,
            );
          }
        }),

      userExists: (macUsername: string) =>
        Effect.gen(function* () {
          const result = yield* exec.run("id", [macUsername]);
          return result.exitCode === 0;
        }),

      listClawUsers: () =>
        Effect.gen(function* () {
          const result = yield* exec.run("dscl", [".", "-list", "/Users"]);
          if (result.exitCode !== 0) return [];

          return result.stdout
            .split("\n")
            .map((l) => l.trim())
            .filter((l) => l.startsWith("claw-"));
        }),
    };
  }),
);
