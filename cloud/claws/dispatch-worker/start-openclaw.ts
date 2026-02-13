/**
 * Entry point for OpenClaw startup in Cloudflare Sandbox.
 *
 * Run via: bun /usr/local/bin/start-openclaw.ts
 *
 * This is a thin orchestrator — all logic lives in src/startup/ modules
 * for testability.
 */

import { existsSync, readFileSync, writeFileSync, mkdirSync } from "fs";
import { join } from "path";

import type { StartupEnv } from "./src/startup";

import {
  log,
  logEnvironment,
  buildConfig,
  redactConfig,
  isGatewayRunning,
  checkBinary,
  buildGatewayArgs,
  redactArgs,
  cleanupLockFiles,
  startGateway,
  restoreFromR2,
  persistToR2,
  syncFileToR2,
} from "./src/startup";

// ============================================================
// Constants
// ============================================================

const CONFIG_DIR = "/root/.openclaw";
const CONFIG_FILE = join(CONFIG_DIR, "openclaw.json");
const WORKSPACE_DIR = join(CONFIG_DIR, "workspace");
const LOG_FILE = "/tmp/gateway.log";

// ============================================================
// Collect environment
// ============================================================

const env: StartupEnv = {
  OPENCLAW_GATEWAY_TOKEN: process.env.OPENCLAW_GATEWAY_TOKEN,
  OPENCLAW_PRIMARY_MODEL: process.env.OPENCLAW_PRIMARY_MODEL,
  OPENCLAW_SITE_URL: process.env.OPENCLAW_SITE_URL,
  OPENCLAW_ALLOWED_ORIGINS: process.env.OPENCLAW_ALLOWED_ORIGINS,
  ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY,
  ANTHROPIC_BASE_URL: process.env.ANTHROPIC_BASE_URL,
  TELEGRAM_BOT_TOKEN: process.env.TELEGRAM_BOT_TOKEN,
  DISCORD_BOT_TOKEN: process.env.DISCORD_BOT_TOKEN,
  SLACK_BOT_TOKEN: process.env.SLACK_BOT_TOKEN,
  SLACK_APP_TOKEN: process.env.SLACK_APP_TOKEN,
  R2_BUCKET_NAME: process.env.R2_BUCKET_NAME,
  R2_ACCESS_KEY_ID: process.env.R2_ACCESS_KEY_ID,
  R2_SECRET_ACCESS_KEY: process.env.R2_SECRET_ACCESS_KEY,
  CF_ACCOUNT_ID: process.env.CF_ACCOUNT_ID,
};

// ============================================================
// Main startup sequence
// ============================================================

log("=== OpenClaw startup script begin ===");
logEnvironment(env);

// Step 1: Bail if already running
log("Step 1: Checking if gateway is already running");
if (isGatewayRunning()) {
  log("Gateway already running, exiting with code 0");
  process.exit(0);
}
log("Step 1 complete: gateway is NOT running, proceeding with startup");

// Step 2: Create directories
log("Step 2: Creating directories");
mkdirSync(CONFIG_DIR, { recursive: true });
log(`Created/verified: ${CONFIG_DIR}`);
mkdirSync(WORKSPACE_DIR, { recursive: true });
log(`Created/verified: ${WORKSPACE_DIR}`);
log("Step 2 complete");

// Step 3: Restore from R2 (non-fatal)
log("Step 3: R2 restore");
const restoreResult = restoreFromR2(env.R2_BUCKET_NAME, CONFIG_DIR);
if (restoreResult.skipped) {
  log(`Step 3 skipped: ${restoreResult.reason}`);
} else if (restoreResult.success) {
  log("Step 3 complete: config restored from R2");
} else {
  log(`Step 3 failed (non-fatal): ${restoreResult.error}`);
}

// Step 4: Build config
log("Step 4: Building openclaw.json");

let existingConfig = undefined;
if (existsSync(CONFIG_FILE)) {
  log("Found existing config file, loading");
  try {
    const raw = readFileSync(CONFIG_FILE, "utf8");
    existingConfig = JSON.parse(raw);
    log("Loaded existing config successfully", { configLength: raw.length });
  } catch (err) {
    log("Failed to parse existing config, starting fresh");
  }
}

const config = buildConfig(env, existingConfig);
const configJson = JSON.stringify(config, null, 2);
writeFileSync(CONFIG_FILE, configJson);
log("Step 4 complete: config written to " + CONFIG_FILE, {
  configLength: configJson.length,
});

// Log redacted config
const redacted = redactConfig(config);
log("Full config (secrets redacted):", { config: JSON.stringify(redacted) });

// Step 5: Persist to R2 (non-fatal)
log("Step 5: R2 persist");
const persistResult = persistToR2(env.R2_BUCKET_NAME, CONFIG_DIR);
if (persistResult.skipped) {
  log(`Step 5 skipped: ${persistResult.reason}`);
} else if (persistResult.success) {
  log("Step 5 complete: config persisted to R2");
} else {
  log(`Step 5 failed (non-fatal): ${persistResult.error}`);
}

// Step 6: Start gateway
log("Step 6: Starting OpenClaw Gateway");

if (!checkBinary()) {
  log("FATAL: openclaw binary not found, exiting");
  process.exit(1);
}

cleanupLockFiles(CONFIG_DIR);

const args = buildGatewayArgs(env.OPENCLAW_GATEWAY_TOKEN);
log("Gateway args:", {
  args: redactArgs(args, env.OPENCLAW_GATEWAY_TOKEN).join(" "),
});

const { exitCode } = await startGateway(args, env.OPENCLAW_GATEWAY_TOKEN);

// Best-effort: sync gateway log to R2
syncFileToR2(env.R2_BUCKET_NAME, LOG_FILE);

log(`=== OpenClaw startup script exiting with code ${exitCode} ===`);
process.exit(exitCode);
