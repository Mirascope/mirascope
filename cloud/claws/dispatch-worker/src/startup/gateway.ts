/**
 * Gateway lifecycle: check if running, start, and tee output to log file.
 */

import { execSync } from "child_process";
import { unlinkSync } from "fs";
import { join } from "path";

import { log, logError } from "./logger";

// ============================================================
// Constants
// ============================================================

const GATEWAY_PORT = 18789;
const LOG_FILE = "/tmp/gateway.log";

// ============================================================
// Status checks
// ============================================================

/**
 * Check if the gateway is already running by testing the port.
 * Also logs pgrep results for debugging (informational only).
 */
export function isGatewayRunning(): boolean {
  log("Checking if gateway is already running...");

  let portInUse = false;
  try {
    execSync(
      `node -e "const s=require('net').createConnection(${GATEWAY_PORT},'127.0.0.1');s.on('connect',()=>{s.end();process.exit(0)});s.on('error',()=>process.exit(1));setTimeout(()=>process.exit(1),1000)"`,
      { stdio: "pipe", timeout: 3000 },
    );
    portInUse = true;
    log(`Port ${GATEWAY_PORT} is listening — gateway is running`);
  } catch {
    log(`Port ${GATEWAY_PORT} is not listening`);
  }

  // Secondary: pgrep for debugging
  try {
    const result = execSync("pgrep -af 'openclaw gateway'", { stdio: "pipe" })
      .toString()
      .trim();
    log("pgrep result:", { result: result || "(empty)" });
  } catch {
    log("pgrep: no matching processes");
  }

  return portInUse;
}

/**
 * Check that the openclaw binary exists and log its version.
 * Returns the binary path, or null if not found.
 */
export function checkBinary(): string | null {
  try {
    const path = execSync("which openclaw", { stdio: "pipe" })
      .toString()
      .trim();
    log("openclaw binary found at:", { path });

    try {
      const version = execSync("openclaw --version 2>&1", {
        stdio: "pipe",
        timeout: 5000,
      })
        .toString()
        .trim();
      log("openclaw version:", { version });
    } catch (err) {
      logError("Failed to get openclaw version (non-fatal)", err);
    }

    return path;
  } catch (err) {
    logError("Failed to find openclaw binary!", err);
    return null;
  }
}

// ============================================================
// Gateway args
// ============================================================

/**
 * Build the command-line args for starting the gateway.
 */
export function buildGatewayArgs(gatewayToken?: string): string[] {
  const args = [
    "gateway",
    "--port",
    String(GATEWAY_PORT),
    "--verbose",
    "--allow-unconfigured",
    "--bind",
    "lan",
  ];

  if (gatewayToken) {
    args.push("--token", gatewayToken);
  }

  return args;
}

/**
 * Redact token from args for safe logging.
 */
export function redactArgs(args: string[], gatewayToken?: string): string[] {
  return args.map((a) =>
    gatewayToken && a === gatewayToken ? "***REDACTED***" : a,
  );
}

// ============================================================
// Cleanup
// ============================================================

/**
 * Remove stale lock files that might prevent gateway startup.
 */
export function cleanupLockFiles(configDir: string): void {
  for (const path of [
    "/tmp/openclaw-gateway.lock",
    join(configDir, "gateway.lock"),
  ]) {
    try {
      unlinkSync(path);
      log(`Removed stale file: ${path}`);
    } catch {
      // File didn't exist — fine
    }
  }
}

// ============================================================
// Gateway process
// ============================================================

export interface GatewayResult {
  exitCode: number;
}

/**
 * Spawn the gateway process and tee its output to console + log file.
 * Returns when the gateway exits.
 */
export async function startGateway(
  args: string[],
  gatewayToken?: string,
): Promise<GatewayResult> {
  const safeArgs = redactArgs(args, gatewayToken);
  log("Spawning gateway:", { command: `openclaw ${safeArgs.join(" ")}` });

  // Open local log file
  const logFile = Bun.file(LOG_FILE);
  const logWriter = logFile.writer();

  const startupHeader = [
    `\n${"=".repeat(60)}`,
    `Gateway startup: ${new Date().toISOString()}`,
    `Token present: ${!!gatewayToken}`,
    `Args: openclaw ${safeArgs.join(" ")}`,
    `${"=".repeat(60)}\n`,
  ].join("\n");
  logWriter.write(startupHeader);
  logWriter.flush();

  log("Spawning gateway process now...");

  const proc = Bun.spawn(["openclaw", ...args], {
    stdio: ["inherit", "pipe", "pipe"],
    env: process.env,
  });

  log("Gateway process spawned", { pid: proc.pid });

  // Tee streams to both console and log file
  async function tee(
    stream: ReadableStream<Uint8Array>,
    target: NodeJS.WriteStream,
  ): Promise<void> {
    const reader = stream.getReader();
    const decoder = new TextDecoder();
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const text = decoder.decode(value, { stream: true });
        target.write(text);
        logWriter.write(text);
        logWriter.flush();
      }
    } catch {
      // Stream closed
    }
  }

  const [exitCode] = await Promise.all([
    proc.exited,
    tee(proc.stdout as ReadableStream<Uint8Array>, process.stdout),
    tee(proc.stderr as ReadableStream<Uint8Array>, process.stderr),
  ]);

  log(`Gateway exited with code ${exitCode}`);
  logWriter.write(`\nGateway exited with code ${exitCode}\n`);
  logWriter.flush();
  logWriter.end();

  return { exitCode };
}
