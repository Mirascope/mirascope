/**
 * Startup script for OpenClaw in Cloudflare Sandbox (Claws dispatch worker).
 *
 * Run via: bun /usr/local/bin/start-openclaw.ts
 *
 * 1. Checks if gateway is already running
 * 2. Restores config from R2 via rclone (if available, non-fatal)
 * 3. Builds openclaw.json from environment variables
 * 4. Persists config to R2 via rclone (non-fatal)
 * 5. Starts the gateway
 *
 * Environment variables are passed by the dispatch worker from the
 * bootstrap config fetched via service binding.
 */

import type { OpenClawConfig } from "openclaw/plugin-sdk";

import { execSync } from "child_process";
import {
  existsSync,
  readFileSync,
  writeFileSync,
  mkdirSync,
  unlinkSync,
} from "fs";
import { join } from "path";

export interface OpenClawEnv {
  // Claw-specific configuration (required)
  CLOUDFLARE_ACCOUNT_ID: string;
  R2_BUCKET_NAME: string;

  OPENCLAW_GATEWAY_TOKEN: string;
  OPENCLAW_SITE_URL: string;
  OPENCLAW_ALLOWED_ORIGINS: string;
  PRIMARY_MODEL_ID: string;

  // Anthropic configuration (required)
  ANTHROPIC_BASE_URL: string;
  ANTHROPIC_API_KEY: string;

  // Channel tokens (optional)
  DISCORD_BOT_TOKEN?: string;
  TELEGRAM_BOT_TOKEN?: string;
  SLACK_BOT_TOKEN?: string;
  SLACK_APP_TOKEN?: string;
}

export interface OpenClawConfigOptions {
  workspaceDir: string;
  gatewayPort: number;
  existingConfig?: OpenClawConfig;
}

// ============================================================
// Constants
// ============================================================

const CONFIG_DIR = "/root/.openclaw";
const CONFIG_FILE = join(CONFIG_DIR, "openclaw.json");
const WORKSPACE_DIR = join(CONFIG_DIR, "workspace");
const GATEWAY_PORT = 18789;
const LOG_FILE = "/tmp/gateway.log";

const RCLONE_FLAGS = "--transfers=16 --fast-list --s3-no-check-bucket";
const RCLONE_EXCLUDE =
  "--exclude='*.lock' --exclude='*.log' --exclude='*.tmp' --exclude='.git/**'";

// ============================================================
// Logging
// ============================================================

function log(msg: string, data?: Record<string, unknown>): void {
  const ts = new Date().toISOString();
  if (data) {
    console.log(`[start-openclaw ${ts}] ${msg}`, JSON.stringify(data));
  } else {
    console.log(`[start-openclaw ${ts}] ${msg}`);
  }
}

function logError(msg: string, err: unknown): void {
  const ts = new Date().toISOString();
  const errMsg =
    err instanceof Error
      ? { message: err.message, stack: err.stack }
      : { raw: String(err) };
  console.error(`[start-openclaw ${ts}] ERROR: ${msg}`, JSON.stringify(errMsg));
}

// ============================================================
// Helpers
// ============================================================

/**
 * Configure rclone for R2 access.
 * Idempotent — skips if already configured.
 */
function ensureRcloneConfig(
  r2AccessKeyId: string,
  r2SecretAccessKey: string,
  cfAccountId: string,
): void {
  const RCLONE_CONF_PATH = "/root/.config/rclone/rclone.conf";
  const CONFIGURED_FLAG = "/tmp/.rclone-configured";

  // Check if already configured (idempotent)
  if (existsSync(CONFIGURED_FLAG)) {
    log("Rclone already configured (flag exists)");
    return;
  }

  const rcloneConfig = [
    "[r2]",
    "type = s3",
    "provider = Cloudflare",
    `access_key_id = ${r2AccessKeyId}`,
    `secret_access_key = ${r2SecretAccessKey}`,
    `endpoint = https://${cfAccountId}.r2.cloudflarestorage.com`,
    "acl = private",
    "no_check_bucket = true",
  ].join("\n");

  // Write rclone config files
  mkdirSync("/root/.config/rclone", { recursive: true });
  writeFileSync(RCLONE_CONF_PATH, rcloneConfig);
  writeFileSync(CONFIGURED_FLAG, "");

  log("Rclone configured for R2");
}

function isGatewayRunning(): boolean {
  log("Checking if gateway is already running...");

  // Primary: check if gateway port is actually listening (TCP connect)
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

  // Secondary: log pgrep results for debugging (informational only)
  try {
    const result = execSync("pgrep -af 'openclaw gateway'", {
      stdio: "pipe",
    })
      .toString()
      .trim();
    log("pgrep result:", { result: result || "(empty)" });
  } catch {
    log("pgrep: no matching processes");
  }

  // Only trust the port check — pgrep can have false positives
  return portInUse;
}

function tryUnlink(path: string): void {
  try {
    unlinkSync(path);
    log(`Removed stale file: ${path}`);
  } catch {
    // ignore — file didn't exist
  }
}

function rcloneConfigured(): boolean {
  const confPath = "/root/.config/rclone/rclone.conf";
  const exists = existsSync(confPath);
  log(`rclone config exists at ${confPath}: ${exists}`);
  if (exists) {
    try {
      const content = readFileSync(confPath, "utf8");
      log("rclone config size:", { bytes: content.length });
    } catch (err) {
      logError("Failed to read rclone config", err);
    }
  }
  return exists;
}

/**
 * Creates an OpenClaw configuration object from environment variables.
 *
 * @param env - Environment variables (typically from process.env)
 * @param options - Configuration options (workspace dir, port, existing config)
 * @returns A complete OpenClawConfig object
 */
export function createOpenClawConfig(
  env: OpenClawEnv,
  options: OpenClawConfigOptions,
): OpenClawConfig {
  const { workspaceDir, gatewayPort, existingConfig } = options;

  // Validate PRIMARY_MODEL_ID format
  if (!env.PRIMARY_MODEL_ID.includes("/")) {
    throw new Error(
      `PRIMARY_MODEL_ID must include a provider prefix (e.g., "anthropic/claude-opus-4-6"), got: ${env.PRIMARY_MODEL_ID}`,
    );
  }

  // Start with existing config or empty object
  const config: OpenClawConfig = existingConfig ?? {};

  // Ensure nested structure
  config.agents ??= {};
  config.agents.defaults ??= {};
  config.agents.defaults.model ??= {};
  config.agents.defaults.models ??= {};
  config.gateway ??= {};
  config.gateway.auth ??= {};
  config.models ??= {};
  config.models.providers ??= {};
  config.channels ??= {};
  config.env ??= {};
  config.env.vars ??= {};

  // Workspace
  config.agents.defaults.workspace = workspaceDir;

  // Gateway basics
  config.gateway.port = gatewayPort;
  config.gateway.mode = "local";
  config.gateway.trustedProxies = ["10.1.0.0"];
  config.gateway.auth.token = env.OPENCLAW_GATEWAY_TOKEN;

  // Set gateway token in env vars so OpenClaw can access it
  config.env.vars.OPENCLAW_GATEWAY_TOKEN = env.OPENCLAW_GATEWAY_TOKEN;

  // Control UI: disable device auth (dispatch worker handles authentication)
  config.gateway.controlUi = {
    ...((config.gateway.controlUi as object) ?? {}),
    dangerouslyDisableDeviceAuth: true,
  };

  // Control UI allowed origins
  const allowedOrigins = env.OPENCLAW_ALLOWED_ORIGINS.split(",")
    .map((o) => o.trim())
    .filter(Boolean);

  if (!allowedOrigins.includes(env.OPENCLAW_SITE_URL)) {
    allowedOrigins.push(env.OPENCLAW_SITE_URL);
  }

  config.gateway.controlUi = { allowedOrigins };

  // Anthropic provider configuration
  const baseUrl = env.ANTHROPIC_BASE_URL.replace(/\/+$/, "");

  config.models.providers.anthropic = {
    baseUrl,
    api: "anthropic-messages",
    apiKey: env.ANTHROPIC_API_KEY,
    models: [
      {
        id: "claude-opus-4-6",
        name: "Claude Opus 4.6",
        reasoning: true,
        input: ["text", "image"],
        cost: {
          input: 15.0,
          output: 75.0,
          cacheRead: 1.5,
          cacheWrite: 18.75,
        },
        contextWindow: 200000,
        maxTokens: 16384,
      },
      {
        id: "claude-opus-4-5",
        name: "Claude Opus 4.5",
        reasoning: true,
        input: ["text", "image"],
        cost: {
          input: 15.0,
          output: 75.0,
          cacheRead: 1.5,
          cacheWrite: 18.75,
        },
        contextWindow: 200000,
        maxTokens: 16384,
      },
      {
        id: "claude-sonnet-4-5",
        name: "Claude Sonnet 4.5",
        reasoning: true,
        input: ["text", "image"],
        cost: {
          input: 3.0,
          output: 15.0,
          cacheRead: 0.3,
          cacheWrite: 3.75,
        },
        contextWindow: 200000,
        maxTokens: 16384,
      },
      {
        id: "claude-haiku-4-5",
        name: "Claude Haiku 4.5",
        reasoning: false,
        input: ["text", "image"],
        cost: {
          input: 0.8,
          output: 4.0,
          cacheRead: 0.08,
          cacheWrite: 1.0,
        },
        contextWindow: 200000,
        maxTokens: 8192,
      },
    ],
  };

  config.agents.defaults.models["anthropic/claude-opus-4-6"] = {
    alias: "Opus 4.6",
  };
  config.agents.defaults.models["anthropic/claude-opus-4-5"] = {
    alias: "Opus 4.5",
  };
  config.agents.defaults.models["anthropic/claude-sonnet-4-5"] = {
    alias: "Sonnet 4.5",
  };
  config.agents.defaults.models["anthropic/claude-haiku-4-5"] = {
    alias: "Haiku 4.5",
  };
  config.agents.defaults.model.primary = env.PRIMARY_MODEL_ID;

  // Channel configurations (optional)
  if (env.TELEGRAM_BOT_TOKEN) {
    config.channels.telegram = {
      ...((config.channels.telegram as object) ?? {}),
      botToken: env.TELEGRAM_BOT_TOKEN,
      enabled: true,
    };
  }

  if (env.DISCORD_BOT_TOKEN) {
    config.channels.discord = {
      ...((config.channels.discord as object) ?? {}),
      token: env.DISCORD_BOT_TOKEN,
      enabled: true,
    };
  }

  if (env.SLACK_BOT_TOKEN && env.SLACK_APP_TOKEN) {
    config.channels.slack = {
      ...((config.channels.slack as object) ?? {}),
      botToken: env.SLACK_BOT_TOKEN,
      appToken: env.SLACK_APP_TOKEN,
      enabled: true,
    };
  }

  return config;
}

// ============================================================
// Main startup sequence
// ============================================================

log("=== OpenClaw startup script begin ===");

// ============================================================
// 0. Configure rclone for R2 (if credentials available)
// ============================================================

// Helper to validate required environment variables
// Returns the value if present, or adds the key to the missing array
function requireEnv(key: string, missing: string[]): string {
  const value = process.env[key];
  if (!value) {
    missing.push(key);
    return ""; // Return empty string as placeholder
  }
  return value;
}

// ============================================================
// 0. Validate all required environment variables
// ============================================================

log("Step 0: Validating environment variables");

// Collect all missing required environment variables
const missingVars: string[] = [];

// R2 credentials (needed for rclone config)
const r2AccessKeyId = requireEnv("R2_ACCESS_KEY_ID", missingVars);
const r2SecretAccessKey = requireEnv("R2_SECRET_ACCESS_KEY", missingVars);
const cfAccountId = requireEnv("CLOUDFLARE_ACCOUNT_ID", missingVars);

// Extract and validate required environment variables
const env: OpenClawEnv = {
  // Claw-specific configuration (required)
  R2_BUCKET_NAME: requireEnv("R2_BUCKET_NAME", missingVars),
  OPENCLAW_GATEWAY_TOKEN: requireEnv("OPENCLAW_GATEWAY_TOKEN", missingVars),
  OPENCLAW_SITE_URL: requireEnv("OPENCLAW_SITE_URL", missingVars),
  OPENCLAW_ALLOWED_ORIGINS: requireEnv("OPENCLAW_ALLOWED_ORIGINS", missingVars),
  CLOUDFLARE_ACCOUNT_ID: cfAccountId, // Already validated above
  // Anthropic configuration (required)
  ANTHROPIC_BASE_URL: requireEnv("ANTHROPIC_BASE_URL", missingVars),
  ANTHROPIC_API_KEY: requireEnv("ANTHROPIC_API_KEY", missingVars),
  PRIMARY_MODEL_ID: requireEnv("PRIMARY_MODEL_ID", missingVars),
  // Channel tokens (optional)
  DISCORD_BOT_TOKEN: process.env.DISCORD_BOT_TOKEN,
  TELEGRAM_BOT_TOKEN: process.env.TELEGRAM_BOT_TOKEN,
  SLACK_BOT_TOKEN: process.env.SLACK_BOT_TOKEN,
  SLACK_APP_TOKEN: process.env.SLACK_APP_TOKEN,
};

// If any required variables are missing, throw a single error with all of them
if (missingVars.length > 0) {
  const errorMessage = [
    `Missing ${missingVars.length} required environment variable${missingVars.length > 1 ? "s" : ""}:`,
    ...missingVars.map((v) => `  - ${v}`),
    "",
    "These variables must be set by the dispatch worker before starting the gateway.",
  ].join("\n");
  throw new Error(errorMessage);
}

log("Step 0 complete: All required environment variables validated");

// ============================================================
// 1. Configure rclone for R2
// ============================================================

log("Step 1: Configuring rclone for R2");

ensureRcloneConfig(r2AccessKeyId, r2SecretAccessKey, cfAccountId);

log("Step 1 complete: rclone configured");

// Log validated environment (claw-specific values in full, secrets redacted)
log("Environment configuration:", {
  // Claw-specific — safe to log in full
  R2_BUCKET_NAME: env.R2_BUCKET_NAME,
  OPENCLAW_GATEWAY_TOKEN: env.OPENCLAW_GATEWAY_TOKEN,
  OPENCLAW_SITE_URL: env.OPENCLAW_SITE_URL,
  OPENCLAW_ALLOWED_ORIGINS: env.OPENCLAW_ALLOWED_ORIGINS,
  CLOUDFLARE_ACCOUNT_ID: env.CLOUDFLARE_ACCOUNT_ID,
  ANTHROPIC_BASE_URL: env.ANTHROPIC_BASE_URL,
  PRIMARY_MODEL_ID: env.PRIMARY_MODEL_ID,
  // Runtime
  NODE_VERSION: process.version ?? "(unknown)",
  BUN_VERSION: process.versions?.bun ?? "(unknown)",
});

const bucket = env.R2_BUCKET_NAME;

// ============================================================
// 2. Bail if already running
// ============================================================

log("Step 2: Checking if gateway is already running");
if (isGatewayRunning()) {
  log("Gateway already running, exiting with code 0");
  process.exit(0);
}
log("Step 2 complete: gateway is NOT running, proceeding with startup");

// ============================================================
// 3. Create directories
// ============================================================

log("Step 3: Creating directories");
mkdirSync(CONFIG_DIR, { recursive: true });
log(`Created/verified: ${CONFIG_DIR}`);
mkdirSync(WORKSPACE_DIR, { recursive: true });
log(`Created/verified: ${WORKSPACE_DIR}`);
log("Step 3 complete");

// ============================================================
// 4. Restore from R2 via rclone (non-fatal on failure)
// ============================================================

log("Step 4: R2 restore");
if (rcloneConfigured()) {
  try {
    const cmd = `rclone sync r2:${bucket}/openclaw/ ${CONFIG_DIR}/ ${RCLONE_FLAGS}`;
    log("Running rclone restore:", { cmd });
    const output = execSync(cmd, {
      stdio: "pipe",
      timeout: 30000,
    })
      .toString()
      .trim();
    if (output) log("rclone restore output:", { output });
    log("Step 4 complete: config restored from R2");
  } catch (err) {
    logError("R2 restore failed (non-fatal, continuing)", err);
  }
} else {
  log("Step 4 skipped: rclone not configured");
}

// ============================================================
// 5. Build openclaw.json from environment variables
// ============================================================

log("Step 5: Building openclaw.json");

// Load existing config if present
let existingConfig: OpenClawConfig | undefined;
if (existsSync(CONFIG_FILE)) {
  log("Found existing config file, loading");
  try {
    const raw = readFileSync(CONFIG_FILE, "utf8");
    existingConfig = JSON.parse(raw);
    log("Loaded existing config successfully:", {
      configLength: raw.length,
      hasAgents: !!existingConfig?.agents,
      hasGateway: !!existingConfig?.gateway,
      hasModels: !!existingConfig?.models,
      hasChannels: !!existingConfig?.channels,
    });
  } catch (err) {
    logError("Failed to parse existing config, starting fresh", err);
  }
} else {
  log("No existing config found, creating new");
}

// Create config using the helper (env is already validated in Step 0)
const config = createOpenClawConfig(env, {
  workspaceDir: WORKSPACE_DIR,
  gatewayPort: GATEWAY_PORT,
  existingConfig,
});

// Write config
const configJson = JSON.stringify(config, null, 2);
writeFileSync(CONFIG_FILE, configJson);
log("Step 5 complete: config written to " + CONFIG_FILE, {
  configLength: configJson.length,
});

// ============================================================
// 6. Persist config to R2 via rclone (non-fatal on failure)
// ============================================================

log("Step 6: R2 persist");
if (rcloneConfigured()) {
  try {
    const cmd = `rclone sync ${CONFIG_DIR}/ r2:${bucket}/openclaw/ ${RCLONE_FLAGS} ${RCLONE_EXCLUDE}`;
    log("Running rclone persist:", { cmd });
    const output = execSync(cmd, {
      stdio: "pipe",
      timeout: 30000,
    })
      .toString()
      .trim();
    if (output) log("rclone persist output:", { output });
    log("Step 6 complete: config persisted to R2");
  } catch (err) {
    logError("R2 persist failed (non-fatal, continuing to start gateway)", err);
  }
} else {
  log("Step 6 skipped: rclone not configured");
}

// ============================================================
// 7. Start gateway
// ============================================================

log("Step 7: Starting OpenClaw Gateway");

// Clean up stale lock files
tryUnlink("/tmp/openclaw-gateway.lock");
tryUnlink(join(CONFIG_DIR, "gateway.lock"));

const args = [
  "gateway",
  "--port",
  String(GATEWAY_PORT),
  "--verbose",
  "--allow-unconfigured",
  "--bind",
  "lan",
];

log("Spawning gateway:", { command: `openclaw ${args.join(" ")}` });

// Check that openclaw binary exists
try {
  const which = execSync("which openclaw", { stdio: "pipe" }).toString().trim();
  log("openclaw binary found at:", { path: which });
} catch (err) {
  logError("Failed to find openclaw binary!", err);
  process.exit(1);
}

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

// Open local log file for persistent logging
const logFile = Bun.file(LOG_FILE);
const logWriter = logFile.writer();

// Write startup header
const startupHeader = [
  `\n${"=".repeat(60)}`,
  `Gateway startup: ${new Date().toISOString()}`,
  `Token present: ${!!config.gateway?.auth?.token}`,
  `Args: openclaw ${args.join(" ")}`,
  `${"=".repeat(60)}\n`,
].join("\n");
logWriter.write(startupHeader);
logWriter.flush();

log("Spawning gateway process now...");

// Start gateway with piped output so we can tee to log file
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

// Run both tees concurrently, wait for process exit
const [exitCode] = await Promise.all([
  proc.exited,
  tee(proc.stdout as ReadableStream<Uint8Array>, process.stdout),
  tee(proc.stderr as ReadableStream<Uint8Array>, process.stderr),
]);

log(`Gateway exited with code ${exitCode}`);
logWriter.write(`\nGateway exited with code ${exitCode}\n`);
logWriter.flush();
logWriter.end();

// Sync log to R2 (best effort)
if (rcloneConfigured()) {
  try {
    log("Syncing gateway log to R2...");
    execSync(`rclone copy ${LOG_FILE} r2:${bucket}/ ${RCLONE_FLAGS}`, {
      stdio: "pipe",
      timeout: 10000,
    });
    log("Gateway log synced to R2");
  } catch {
    log("Failed to sync gateway log to R2 (best effort, ignoring)");
  }
}

log(`=== OpenClaw startup script exiting with code ${exitCode} ===`);
process.exit(exitCode);
