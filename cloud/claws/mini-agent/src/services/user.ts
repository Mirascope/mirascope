import { randomBytes } from "node:crypto";
import { writeFile } from "node:fs/promises";
import path from "node:path";

/**
 * macOS user creation/deletion via sysadminctl.
 */
import { type ExecFn, exec as defaultExec } from "../lib/exec.js";

const ZSHRC_TEMPLATE = `
# Mirascope Claw user profile
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

# Node.js
export PATH="/opt/homebrew/opt/node/bin:$PATH"

# Playwright
export PLAYWRIGHT_BROWSERS_PATH="/opt/homebrew/var/playwright"
`.trim();

export interface CreateUserOptions {
  macUsername: string;
  clawId: string;
  localPort: number;
  gatewayToken: string;
  tunnelHostname: string;
  envVars: Record<string, string>;
}

/**
 * Create a macOS user for a claw and set up the home directory.
 */
export async function createClawUser(
  options: CreateUserOptions,
  execFn: ExecFn = defaultExec,
): Promise<void> {
  const { macUsername, clawId, localPort, gatewayToken, envVars } = options;
  const homeDir = `/Users/${macUsername}`;
  const password = randomBytes(32).toString("hex");

  // 1. Create macOS user
  const createResult = await execFn(
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
    throw new Error(
      `Failed to create user ${macUsername}: ${createResult.stderr}`,
    );
  }

  // 2. Lock down home directory
  await execFn("chmod", ["700", homeDir], { sudo: true });

  // 3. Write .zshrc
  const zshrcPath = path.join(homeDir, ".zshrc");
  await writeFileAsSudo(zshrcPath, ZSHRC_TEMPLATE, macUsername, execFn);

  // 4. Create .openclaw directories
  const openclawDir = path.join(homeDir, ".openclaw");
  const workspaceDir = path.join(openclawDir, "workspace");
  const logsDir = path.join(openclawDir, "logs");

  await execFn("mkdir", ["-p", workspaceDir, logsDir], {
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
  const configPath = path.join(openclawDir, "openclaw.json");
  await writeFileAsSudo(
    configPath,
    JSON.stringify(openclawConfig, null, 2),
    macUsername,
    execFn,
  );

  // 6. Write .env with injected environment variables
  if (Object.keys(envVars).length > 0) {
    const envContent = Object.entries(envVars)
      .map(([k, v]) => `${k}=${v}`)
      .join("\n");
    const envPath = path.join(openclawDir, ".env");
    await writeFileAsSudo(envPath, envContent, macUsername, execFn);
  }
}

/**
 * Delete a macOS user and their home directory.
 */
export async function deleteClawUser(
  macUsername: string,
  execFn: ExecFn = defaultExec,
): Promise<void> {
  // Delete user and home directory
  const result = await execFn(
    "sysadminctl",
    ["-deleteUser", macUsername, "-secure"],
    { sudo: true, timeout: 60_000 },
  );

  if (result.exitCode !== 0) {
    throw new Error(`Failed to delete user ${macUsername}: ${result.stderr}`);
  }
}

/**
 * Check if a macOS user exists.
 */
export async function userExists(
  macUsername: string,
  execFn: ExecFn = defaultExec,
): Promise<boolean> {
  const result = await execFn("id", [macUsername]);
  return result.exitCode === 0;
}

/** Write a file owned by a specific user using sudo tee */
async function writeFileAsSudo(
  filePath: string,
  content: string,
  owner: string,
  execFn: ExecFn,
): Promise<void> {
  // Write via a temp approach: write to tmp, then move and chown
  const tmpPath = `/tmp/mini-agent-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  await writeFile(tmpPath, content, "utf-8");
  await execFn("mv", [tmpPath, filePath], { sudo: true });
  await execFn("chown", [`${owner}:staff`, filePath], { sudo: true });
}
