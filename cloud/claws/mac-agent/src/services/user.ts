/**
 * macOS user creation/deletion service.
 */
import { randomBytes } from "node:crypto";
import { writeFile } from "node:fs/promises";
import path from "node:path";

import { Context, Effect } from "effect";

import { ProvisioningError } from "../errors.js";
import { Exec } from "./exec.js";

export interface CreateUserOptions {
  readonly macUsername: string;
  readonly clawId: string;
  readonly localPort: number;
  readonly gatewayToken: string;
  readonly tunnelHostname: string;
  readonly envVars: Record<string, string>;
}

export class UserManager extends Context.Tag("UserManager")<
  UserManager,
  {
    readonly createClawUser: (
      options: CreateUserOptions,
    ) => Effect.Effect<void, ProvisioningError>;
    readonly deleteClawUser: (
      macUsername: string,
    ) => Effect.Effect<void, ProvisioningError>;
    readonly userExists: (
      macUsername: string,
    ) => Effect.Effect<boolean, ProvisioningError>;
  }
>() {}

const ZSHRC_TEMPLATE = `
# Mirascope Claw user profile
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

# Node.js
export PATH="/opt/homebrew/opt/node/bin:$PATH"

# Playwright
export PLAYWRIGHT_BROWSERS_PATH="/opt/playwright-browsers"
`.trim();

export const UserManagerLive = Effect.gen(function* () {
  const exec = yield* Exec;

  const writeFileAsSudo = (
    filePath: string,
    content: string,
    owner: string,
  ): Effect.Effect<void, ProvisioningError> =>
    Effect.gen(function* () {
      const tmpPath = `/tmp/mac-agent-${Date.now()}-${Math.random().toString(36).slice(2)}`;
      yield* Effect.tryPromise({
        try: () => writeFile(tmpPath, content, "utf-8"),
        catch: (e) =>
          new ProvisioningError({
            message: `Failed to write temp file: ${tmpPath}`,
            cause: e,
          }),
      });
      yield* exec.runUnsafe("mv", [tmpPath, filePath], { sudo: true }).pipe(
        Effect.mapError(
          (e) => new ProvisioningError({ message: e.message, cause: e }),
        ),
      );
      yield* exec
        .runUnsafe("chown", [`${owner}:staff`, filePath], { sudo: true })
        .pipe(
          Effect.mapError(
            (e) => new ProvisioningError({ message: e.message, cause: e }),
          ),
        );
    });

  const createClawUser = (
    options: CreateUserOptions,
  ): Effect.Effect<void, ProvisioningError> =>
    Effect.gen(function* () {
      const { macUsername, clawId, localPort, gatewayToken, envVars } = options;
      const homeDir = `/Users/${macUsername}`;
      const password = randomBytes(32).toString("hex");

      // 1. Create macOS user
      const createResult = yield* exec
        .run(
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
        )
        .pipe(
          Effect.mapError(
            (e) => new ProvisioningError({ message: e.message, cause: e }),
          ),
        );

      if (createResult.exitCode !== 0) {
        return yield* Effect.fail(
          new ProvisioningError({
            message: `Failed to create user ${macUsername}: ${createResult.stderr}`,
          }),
        );
      }

      // 2. Create and lock down home directory (sysadminctl assigns but doesn't create it)
      yield* exec
        .runUnsafe("mkdir", ["-p", homeDir], { sudo: true })
        .pipe(
          Effect.mapError(
            (e) => new ProvisioningError({ message: e.message, cause: e }),
          ),
        );
      yield* exec
        .runUnsafe("chown", [`${macUsername}:staff`, homeDir], { sudo: true })
        .pipe(
          Effect.mapError(
            (e) => new ProvisioningError({ message: e.message, cause: e }),
          ),
        );
      yield* exec
        .runUnsafe("chmod", ["700", homeDir], { sudo: true })
        .pipe(
          Effect.mapError(
            (e) => new ProvisioningError({ message: e.message, cause: e }),
          ),
        );

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

      yield* exec
        .runUnsafe("mkdir", ["-p", workspaceDir, logsDir], {
          sudoUser: macUsername,
        })
        .pipe(
          Effect.mapError(
            (e) => new ProvisioningError({ message: e.message, cause: e }),
          ),
        );

      // 5. Write openclaw.json
      const openclawConfig = {
        gateway: { host: "127.0.0.1", port: localPort, token: gatewayToken },
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
    });

  const deleteClawUser = (
    macUsername: string,
  ): Effect.Effect<void, ProvisioningError> =>
    Effect.gen(function* () {
      const result = yield* exec
        .run("sysadminctl", ["-deleteUser", macUsername, "-secure"], {
          sudo: true,
          timeout: 60_000,
        })
        .pipe(
          Effect.mapError(
            (e) => new ProvisioningError({ message: e.message, cause: e }),
          ),
        );

      if (result.exitCode !== 0) {
        return yield* Effect.fail(
          new ProvisioningError({
            message: `Failed to delete user ${macUsername}: ${result.stderr}`,
          }),
        );
      }
    });

  const userExists = (
    macUsername: string,
  ): Effect.Effect<boolean, ProvisioningError> =>
    exec
      .run("id", [macUsername])
      .pipe(
        Effect.map((r) => r.exitCode === 0),
        Effect.mapError(
          (e) => new ProvisioningError({ message: e.message, cause: e }),
        ),
      );

  return { createClawUser, deleteClawUser, userExists };
});
