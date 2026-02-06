/**
 * Startup script for OpenClaw in Cloudflare Sandbox (Claws dispatch worker).
 *
 * Run via: bun /usr/local/bin/start-openclaw.ts
 *
 * 1. Checks if gateway is already running
 * 2. Restores config from R2 backup if available and newer
 * 3. Builds openclaw.json from environment variables
 * 4. Starts the gateway
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
  cpSync,
  unlinkSync,
  statSync,
} from "fs";
import { join } from "path";

// ============================================================
// Constants
// ============================================================

const CONFIG_DIR = "/root/.openclaw";
const CONFIG_FILE = join(CONFIG_DIR, "openclaw.json");
const BACKUP_DIR = "/data/claw";
const WORKSPACE_DIR = join(CONFIG_DIR, "workspace");
const GATEWAY_PORT = 18789;

// ============================================================
// Helpers
// ============================================================

function isGatewayRunning(): boolean {
  try {
    execSync("pgrep -f 'openclaw gateway'", { stdio: "ignore" });
    return true;
  } catch {
    return false;
  }
}

function shouldRestoreFromR2(): boolean {
  const r2SyncFile = join(BACKUP_DIR, ".last-sync");
  const localSyncFile = join(CONFIG_DIR, ".last-sync");

  if (!existsSync(r2SyncFile)) {
    console.log("No R2 sync timestamp found, skipping restore");
    return false;
  }

  if (!existsSync(localSyncFile)) {
    console.log("No local sync timestamp, will restore from R2");
    return true;
  }

  const r2Time = readFileSync(r2SyncFile, "utf8").trim();
  const localTime = readFileSync(localSyncFile, "utf8").trim();

  console.log("R2 last sync:", r2Time);
  console.log("Local last sync:", localTime);

  const r2Epoch = new Date(r2Time).getTime() || 0;
  const localEpoch = new Date(localTime).getTime() || 0;

  if (r2Epoch > localEpoch) {
    console.log("R2 backup is newer, will restore");
    return true;
  }

  console.log("Local data is newer or same, skipping restore");
  return false;
}

function tryUnlink(path: string): void {
  try {
    unlinkSync(path);
  } catch {
    // ignore
  }
}

// ============================================================
// 1. Bail if already running
// ============================================================

if (isGatewayRunning()) {
  console.log("OpenClaw gateway is already running, exiting.");
  process.exit(0);
}

// ============================================================
// 2. Create directories
// ============================================================

mkdirSync(CONFIG_DIR, { recursive: true });
mkdirSync(WORKSPACE_DIR, { recursive: true });

console.log("Config directory:", CONFIG_DIR);
console.log("Backup directory:", BACKUP_DIR);

// ============================================================
// 3. Restore from R2 backup
// ============================================================

const backupConfigPath = join(BACKUP_DIR, "openclaw", "openclaw.json");

if (existsSync(backupConfigPath)) {
  if (shouldRestoreFromR2()) {
    console.log("Restoring from R2 backup at", join(BACKUP_DIR, "openclaw"));
    cpSync(join(BACKUP_DIR, "openclaw"), CONFIG_DIR, { recursive: true });
    const syncFile = join(BACKUP_DIR, ".last-sync");
    if (existsSync(syncFile)) {
      cpSync(syncFile, join(CONFIG_DIR, ".last-sync"));
    }
    console.log("Restored config from R2 backup");
  }
} else if (existsSync(BACKUP_DIR) && statSync(BACKUP_DIR).isDirectory()) {
  console.log("R2 mounted at", BACKUP_DIR, "but no backup data found yet");
} else {
  console.log("R2 not mounted, starting fresh");
}

// ============================================================
// 4. Build openclaw.json from environment variables
// ============================================================

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
  };
  models?: {
    providers?: Record<string, unknown>;
  };
  channels?: Record<string, unknown>;
}

let config: OpenClawConfig = {};

if (existsSync(CONFIG_FILE)) {
  console.log("Using existing config");
  try {
    config = JSON.parse(readFileSync(CONFIG_FILE, "utf8"));
  } catch {
    console.log("Failed to parse existing config, starting fresh");
  }
} else {
  console.log("No existing config found, creating new");
}

// Ensure nested structure
config.agents ??= {};
config.agents.defaults ??= {};
config.agents.defaults.model ??= {};
config.gateway ??= {};

// Workspace
config.agents.defaults.workspace = WORKSPACE_DIR;

// Gateway
config.gateway.port = GATEWAY_PORT;
config.gateway.mode = "local";
config.gateway.trustedProxies = ["10.1.0.0"];

// Gateway token (always required for claws)
const gatewayToken = process.env.OPENCLAW_GATEWAY_TOKEN;
if (gatewayToken) {
  config.gateway.auth ??= {};
  config.gateway.auth.token = gatewayToken;
}

// Anthropic provider configuration via Mirascope router
const baseUrl = (process.env.ANTHROPIC_BASE_URL ?? "").replace(/\/+$/, "");
if (baseUrl) {
  console.log("Configuring Anthropic provider with base URL:", baseUrl);
  config.models ??= {};
  config.models.providers ??= {};

  const providerConfig: Record<string, unknown> = {
    baseUrl,
    api: "anthropic-messages",
    models: [
      {
        id: "claude-opus-4-5-20251101",
        name: "Claude Opus 4.5",
        contextWindow: 200000,
      },
      {
        id: "claude-sonnet-4-5-20250929",
        name: "Claude Sonnet 4.5",
        contextWindow: 200000,
      },
      {
        id: "claude-haiku-4-5-20251001",
        name: "Claude Haiku 4.5",
        contextWindow: 200000,
      },
    ],
  };

  if (process.env.ANTHROPIC_API_KEY) {
    providerConfig.apiKey = process.env.ANTHROPIC_API_KEY;
  }

  config.models.providers.anthropic = providerConfig;

  config.agents.defaults.models ??= {};
  config.agents.defaults.models["anthropic/claude-opus-4-5-20251101"] = {
    alias: "Opus 4.5",
  };
  config.agents.defaults.models["anthropic/claude-sonnet-4-5-20250929"] = {
    alias: "Sonnet 4.5",
  };
  config.agents.defaults.models["anthropic/claude-haiku-4-5-20251001"] = {
    alias: "Haiku 4.5",
  };
  config.agents.defaults.model.primary = "anthropic/claude-opus-4-5-20251101";
} else if (process.env.ANTHROPIC_API_KEY) {
  config.agents.defaults.model.primary = "anthropic/claude-opus-4-5";
}

// Channel configurations
config.channels ??= {};

if (process.env.TELEGRAM_BOT_TOKEN) {
  config.channels.telegram = {
    ...((config.channels.telegram as object) ?? {}),
    botToken: process.env.TELEGRAM_BOT_TOKEN,
    enabled: true,
  };
}

if (process.env.DISCORD_BOT_TOKEN) {
  config.channels.discord = {
    ...((config.channels.discord as object) ?? {}),
    token: process.env.DISCORD_BOT_TOKEN,
    enabled: true,
  };
}

if (process.env.SLACK_BOT_TOKEN && process.env.SLACK_APP_TOKEN) {
  config.channels.slack = {
    ...((config.channels.slack as object) ?? {}),
    botToken: process.env.SLACK_BOT_TOKEN,
    appToken: process.env.SLACK_APP_TOKEN,
    enabled: true,
  };
}

// Write config
writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
console.log("Configuration written to", CONFIG_FILE);

// ============================================================
// 5. Start gateway
// ============================================================

console.log("Starting OpenClaw Gateway on port", GATEWAY_PORT);

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
  console.log("Starting gateway with token auth...");
  args.push("--token", gatewayToken);
} else {
  console.log("Starting gateway (no token)...");
}

// Replace the current process with the gateway
// Using Bun.spawn with stdio: "inherit" and unref: false to act like exec
const proc = Bun.spawn(["openclaw", ...args], {
  stdio: ["inherit", "inherit", "inherit"],
  env: process.env,
});

// Wait for the gateway process to exit and propagate its exit code
const exitCode = await proc.exited;
process.exit(exitCode);
