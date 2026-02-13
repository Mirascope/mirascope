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

import { execSync } from "child_process";
import {
  existsSync,
  readFileSync,
  writeFileSync,
  mkdirSync,
  unlinkSync,
} from "fs";
import { join } from "path";

// ============================================================
// Constants
// ============================================================

const CONFIG_DIR = "/root/.openclaw";
const CONFIG_FILE = join(CONFIG_DIR, "openclaw.json");
const WORKSPACE_DIR = join(CONFIG_DIR, "workspace");
const GATEWAY_PORT = 18789;
const LOG_FILE = "/tmp/gateway.log";

const bucket = process.env.R2_BUCKET_NAME;
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

// ============================================================
// Main startup sequence
// ============================================================

log("=== OpenClaw startup script begin ===");

// Log claw-specific values in full, redact shared secrets
log("Environment snapshot:", {
  // Claw-specific — safe to log in full
  R2_BUCKET_NAME: process.env.R2_BUCKET_NAME ?? "(not set)",
  OPENCLAW_GATEWAY_TOKEN: process.env.OPENCLAW_GATEWAY_TOKEN ?? "(not set)",
  OPENCLAW_PRIMARY_MODEL: process.env.OPENCLAW_PRIMARY_MODEL ?? "(not set)",
  OPENCLAW_SITE_URL: process.env.OPENCLAW_SITE_URL ?? "(not set)",
  OPENCLAW_ALLOWED_ORIGINS: process.env.OPENCLAW_ALLOWED_ORIGINS ?? "(not set)",
  CF_ACCOUNT_ID: process.env.CF_ACCOUNT_ID ?? "(not set)",
  ANTHROPIC_BASE_URL: process.env.ANTHROPIC_BASE_URL ?? "(not set)",
  // Shared secrets — presence only
  ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY ? "(set)" : "(not set)",
  R2_ACCESS_KEY_ID: process.env.R2_ACCESS_KEY_ID ? "(set)" : "(not set)",
  R2_SECRET_ACCESS_KEY: process.env.R2_SECRET_ACCESS_KEY
    ? "(set)"
    : "(not set)",
  DISCORD_BOT_TOKEN: process.env.DISCORD_BOT_TOKEN ? "(set)" : "(not set)",
  TELEGRAM_BOT_TOKEN: process.env.TELEGRAM_BOT_TOKEN ? "(set)" : "(not set)",
  SLACK_BOT_TOKEN: process.env.SLACK_BOT_TOKEN ? "(set)" : "(not set)",
  SLACK_APP_TOKEN: process.env.SLACK_APP_TOKEN ? "(set)" : "(not set)",
  // Runtime
  NODE_VERSION: process.version ?? "(unknown)",
  BUN_VERSION: process.versions?.bun ?? "(unknown)",
});

// ============================================================
// 1. Bail if already running
// ============================================================

log("Step 1: Checking if gateway is already running");
if (isGatewayRunning()) {
  log("Gateway already running, exiting with code 0");
  process.exit(0);
}
log("Step 1 complete: gateway is NOT running, proceeding with startup");

// ============================================================
// 2. Create directories
// ============================================================

log("Step 2: Creating directories");
mkdirSync(CONFIG_DIR, { recursive: true });
log(`Created/verified: ${CONFIG_DIR}`);
mkdirSync(WORKSPACE_DIR, { recursive: true });
log(`Created/verified: ${WORKSPACE_DIR}`);
log("Step 2 complete");

// ============================================================
// 3. Restore from R2 via rclone (non-fatal on failure)
// ============================================================

log("Step 3: R2 restore");
if (bucket && rcloneConfigured()) {
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
    log("Step 3 complete: config restored from R2");
  } catch (err) {
    logError("R2 restore failed (non-fatal, continuing)", err);
  }
} else if (!bucket) {
  log("Step 3 skipped: R2_BUCKET_NAME not set");
} else {
  log("Step 3 skipped: rclone not configured");
}

// ============================================================
// 4. Build openclaw.json from environment variables
// ============================================================

log("Step 4: Building openclaw.json");

interface OpenClawConfig {
  agents?: {
    defaults?: {
      workspace?: string;
      model?: { primary?: string };
      models?: Record<string, { alias: string }>;
    };
  };
  gateway?: {
    port?: number;
    mode?: string;
    trustedProxies?: string[];
    auth?: { token?: string };
    controlUi?: { allowedOrigins?: string[] };
  };
  models?: {
    providers?: Record<string, unknown>;
  };
  channels?: Record<string, unknown>;
}

let config: OpenClawConfig = {};

if (existsSync(CONFIG_FILE)) {
  log("Found existing config file, loading");
  try {
    const raw = readFileSync(CONFIG_FILE, "utf8");
    config = JSON.parse(raw);
    log("Loaded existing config successfully:", {
      configLength: raw.length,
      hasAgents: !!config.agents,
      hasGateway: !!config.gateway,
      hasModels: !!config.models,
      hasChannels: !!config.channels,
    });
  } catch (err) {
    logError("Failed to parse existing config, starting fresh", err);
  }
} else {
  log("No existing config found, creating new");
}

// Ensure nested structure
config.agents ??= {};
config.agents.defaults ??= {};
config.agents.defaults.model ??= {};
config.gateway ??= {};

// Workspace
config.agents.defaults.workspace = WORKSPACE_DIR;
log("Workspace set to:", { workspace: WORKSPACE_DIR });

// Gateway
config.gateway.port = GATEWAY_PORT;
config.gateway.mode = "local";
config.gateway.trustedProxies = ["10.1.0.0"];
log("Gateway basics configured:", {
  port: GATEWAY_PORT,
  mode: "local",
  trustedProxies: ["10.1.0.0"],
});

// Gateway token (always required for claws)
const gatewayToken = process.env.OPENCLAW_GATEWAY_TOKEN;
if (gatewayToken) {
  config.gateway.auth ??= {};
  config.gateway.auth.token = gatewayToken;
  log("Gateway token configured");
} else {
  log("WARNING: No OPENCLAW_GATEWAY_TOKEN set");
}

// Control UI allowed origins (for WebSocket connections from browser)
const allowedOrigins: string[] = [];
const envOrigins = process.env.OPENCLAW_ALLOWED_ORIGINS;
if (envOrigins) {
  allowedOrigins.push(
    ...envOrigins
      .split(",")
      .map((o) => o.trim())
      .filter(Boolean),
  );
}
const siteUrl = process.env.OPENCLAW_SITE_URL;
if (siteUrl && !allowedOrigins.includes(siteUrl)) {
  allowedOrigins.push(siteUrl);
}
if (allowedOrigins.length > 0) {
  config.gateway.controlUi = { allowedOrigins };
  log("Control UI allowed origins:", { allowedOrigins });
} else {
  log("No allowed origins configured for Control UI");
}

// Anthropic provider configuration via Mirascope router
const baseUrl = (process.env.ANTHROPIC_BASE_URL ?? "").replace(/\/+$/, "");
if (baseUrl) {
  log("Configuring Anthropic provider:", { baseUrl });
  config.models ??= {};
  config.models.providers ??= {};

  const providerConfig: Record<string, unknown> = {
    baseUrl,
    api: "anthropic-messages",
    models: [
      {
        id: "claude-opus-4-6",
        name: "Claude Opus 4.6",
        contextWindow: 200000,
      },
      {
        id: "claude-opus-4-5",
        name: "Claude Opus 4.5",
        contextWindow: 200000,
      },
      {
        id: "claude-sonnet-4-5",
        name: "Claude Sonnet 4.5",
        contextWindow: 200000,
      },
      {
        id: "claude-haiku-4-5",
        name: "Claude Haiku 4.5",
        contextWindow: 200000,
      },
    ],
  };

  if (process.env.ANTHROPIC_API_KEY) {
    providerConfig.apiKey = process.env.ANTHROPIC_API_KEY;
    log("Anthropic API key set");
  } else {
    log("WARNING: No ANTHROPIC_API_KEY set");
  }

  config.models.providers.anthropic = providerConfig;

  config.agents.defaults.models ??= {};
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

  // Use the model selected at claw creation (passed via OPENCLAW_PRIMARY_MODEL)
  // or default to haiku (free tier default)
  const primaryModel = process.env.OPENCLAW_PRIMARY_MODEL;
  config.agents.defaults.model.primary = primaryModel
    ? `anthropic/${primaryModel}`
    : "anthropic/claude-haiku-4-5";
  log("Anthropic provider configured", {
    primaryModel: config.agents.defaults.model.primary,
  });
} else if (process.env.ANTHROPIC_API_KEY) {
  const primaryModel = process.env.OPENCLAW_PRIMARY_MODEL;
  config.agents.defaults.model.primary = primaryModel
    ? `anthropic/${primaryModel}`
    : "anthropic/claude-haiku-4-5";
  log("Using default Anthropic provider (no base URL)");
} else {
  log("WARNING: No Anthropic configuration at all");
}

// Channel configurations
config.channels ??= {};
log("Checking channel configurations...");

if (process.env.TELEGRAM_BOT_TOKEN) {
  config.channels.telegram = {
    ...((config.channels.telegram as object) ?? {}),
    botToken: process.env.TELEGRAM_BOT_TOKEN,
    enabled: true,
  };
  log("Telegram channel configured");
} else {
  log("Telegram: no token set");
}

if (process.env.DISCORD_BOT_TOKEN) {
  config.channels.discord = {
    ...((config.channels.discord as object) ?? {}),
    token: process.env.DISCORD_BOT_TOKEN,
    enabled: true,
  };
  log("Discord channel configured");
} else {
  log("Discord: no token set");
}

if (process.env.SLACK_BOT_TOKEN && process.env.SLACK_APP_TOKEN) {
  config.channels.slack = {
    ...((config.channels.slack as object) ?? {}),
    botToken: process.env.SLACK_BOT_TOKEN,
    appToken: process.env.SLACK_APP_TOKEN,
    enabled: true,
  };
  log("Slack channel configured");
} else {
  log("Slack: missing bot token and/or app token");
}

// Write config
const configJson = JSON.stringify(config, null, 2);
writeFileSync(CONFIG_FILE, configJson);
log("Step 4 complete: config written to " + CONFIG_FILE, {
  configLength: configJson.length,
});
// Log full config for staging debugging
// Log config structure (redact provider apiKey values)
try {
  const redacted = JSON.parse(configJson);
  if (redacted.models?.providers) {
    for (const p of Object.values(redacted.models.providers) as Record<
      string,
      unknown
    >[]) {
      if (p.apiKey) p.apiKey = "(redacted)";
    }
  }
  if (redacted.channels) {
    for (const ch of Object.values(redacted.channels) as Record<
      string,
      unknown
    >[]) {
      if (ch.token) ch.token = "(redacted)";
      if (ch.botToken) ch.botToken = "(redacted)";
      if (ch.appToken) ch.appToken = "(redacted)";
    }
  }
  log("Full config (secrets redacted):", { config: JSON.stringify(redacted) });
} catch {
  log("Config written but failed to log redacted version");
}

// ============================================================
// 5. Persist config to R2 via rclone (non-fatal on failure)
// ============================================================

log("Step 5: R2 persist");
if (bucket && rcloneConfigured()) {
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
    log("Step 5 complete: config persisted to R2");
  } catch (err) {
    logError("R2 persist failed (non-fatal, continuing to start gateway)", err);
  }
} else if (!bucket) {
  log("Step 5 skipped: R2_BUCKET_NAME not set");
} else {
  log("Step 5 skipped: rclone not configured");
}

// ============================================================
// 6. Start gateway
// ============================================================

log("Step 6: Starting OpenClaw Gateway");

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

if (gatewayToken) {
  args.push("--token", gatewayToken);
  log("Gateway args: token auth enabled");
} else {
  log("Gateway args: no token auth");
}

// Log the full command (redact token)
const safeArgs = args.map((a) => (a === gatewayToken ? "***REDACTED***" : a));
log("Spawning gateway:", { command: `openclaw ${safeArgs.join(" ")}` });

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
  `Token present: ${!!gatewayToken}`,
  `Args: openclaw ${safeArgs.join(" ")}`,
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
if (bucket && rcloneConfigured()) {
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
