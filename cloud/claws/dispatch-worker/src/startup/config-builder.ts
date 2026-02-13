/**
 * Pure function: builds an OpenClaw config from environment variables.
 *
 * This is the core logic of start-openclaw.ts, extracted for testability.
 * Given a set of env vars and an optional existing config, produces the
 * final openclaw.json content.
 */

import { log } from "./logger";

// ============================================================
// Types
// ============================================================

export interface StartupEnv {
  OPENCLAW_GATEWAY_TOKEN?: string;
  OPENCLAW_SITE_URL?: string;
  OPENCLAW_ALLOWED_ORIGINS?: string;
  ANTHROPIC_API_KEY?: string;
  ANTHROPIC_BASE_URL?: string;
  TELEGRAM_BOT_TOKEN?: string;
  DISCORD_BOT_TOKEN?: string;
  SLACK_BOT_TOKEN?: string;
  SLACK_APP_TOKEN?: string;
  R2_BUCKET_NAME?: string;
  R2_ACCESS_KEY_ID?: string;
  R2_SECRET_ACCESS_KEY?: string;
  CF_ACCOUNT_ID?: string;
}

export interface OpenClawStartupConfig {
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

// ============================================================
// Constants
// ============================================================

const GATEWAY_PORT = 18789;
const WORKSPACE_DIR = "/root/.openclaw/workspace";

const ANTHROPIC_MODELS = [
  {
    id: "claude-opus-4-5-20251101",
    name: "Claude Opus 4.5",
    contextWindow: 200000,
    alias: "Opus 4.5",
  },
  {
    id: "claude-sonnet-4-5-20250929",
    name: "Claude Sonnet 4.5",
    contextWindow: 200000,
    alias: "Sonnet 4.5",
  },
  {
    id: "claude-haiku-4-5-20251001",
    name: "Claude Haiku 4.5",
    contextWindow: 200000,
    alias: "Haiku 4.5",
  },
] as const;

// ============================================================
// Config builder
// ============================================================

/**
 * Build an OpenClaw config from environment variables, optionally merging
 * with an existing config (e.g. restored from R2).
 *
 * This function is pure — no filesystem or network access.
 */
export function buildConfig(
  env: StartupEnv,
  existingConfig?: OpenClawStartupConfig,
): OpenClawStartupConfig {
  const config: OpenClawStartupConfig = existingConfig
    ? structuredClone(existingConfig)
    : {};

  // Ensure nested structure
  config.agents ??= {};
  config.agents.defaults ??= {};
  config.agents.defaults.model ??= {};
  config.gateway ??= {};

  // Workspace
  config.agents.defaults.workspace = WORKSPACE_DIR;

  // Gateway basics
  config.gateway.port = GATEWAY_PORT;
  config.gateway.mode = "local";
  config.gateway.trustedProxies = ["10.1.0.0"];

  // Gateway auth token
  if (env.OPENCLAW_GATEWAY_TOKEN) {
    config.gateway.auth ??= {};
    config.gateway.auth.token = env.OPENCLAW_GATEWAY_TOKEN;
  }

  // Control UI allowed origins
  config.gateway.controlUi = buildAllowedOrigins(env);

  // Anthropic provider
  configureAnthropic(config, env);

  // Channel configurations
  configureChannels(config, env);

  return config;
}

/**
 * Build the allowed origins list from env vars.
 */
export function buildAllowedOrigins(
  env: Pick<StartupEnv, "OPENCLAW_ALLOWED_ORIGINS" | "OPENCLAW_SITE_URL">,
): { allowedOrigins: string[] } | undefined {
  const origins: string[] = [];

  if (env.OPENCLAW_ALLOWED_ORIGINS) {
    origins.push(
      ...env.OPENCLAW_ALLOWED_ORIGINS.split(",")
        .map((o) => o.trim())
        .filter(Boolean),
    );
  }

  if (env.OPENCLAW_SITE_URL && !origins.includes(env.OPENCLAW_SITE_URL)) {
    origins.push(env.OPENCLAW_SITE_URL);
  }

  return origins.length > 0 ? { allowedOrigins: origins } : undefined;
}

/**
 * Configure the Anthropic provider on the config object.
 */
function configureAnthropic(
  config: OpenClawStartupConfig,
  env: Pick<StartupEnv, "ANTHROPIC_API_KEY" | "ANTHROPIC_BASE_URL">,
): void {
  const baseUrl = (env.ANTHROPIC_BASE_URL ?? "").replace(/\/+$/, "");

  if (baseUrl) {
    config.models ??= {};
    config.models.providers ??= {};

    const providerConfig: Record<string, unknown> = {
      baseUrl,
      api: "anthropic-messages",
      models: ANTHROPIC_MODELS.map(({ id, name, contextWindow }) => ({
        id,
        name,
        contextWindow,
      })),
    };

    if (env.ANTHROPIC_API_KEY) {
      providerConfig.apiKey = env.ANTHROPIC_API_KEY;
    }

    config.models.providers.anthropic = providerConfig;

    config.agents!.defaults!.models ??= {};
    for (const model of ANTHROPIC_MODELS) {
      config.agents!.defaults!.models[`anthropic/${model.id}`] = {
        alias: model.alias,
      };
    }
    config.agents!.defaults!.model!.primary = `anthropic/${ANTHROPIC_MODELS[0].id}`;
  } else if (env.ANTHROPIC_API_KEY) {
    config.agents!.defaults!.model!.primary = "anthropic/claude-opus-4-5";
  }
}

/**
 * Configure messaging channels on the config object.
 */
function configureChannels(
  config: OpenClawStartupConfig,
  env: Pick<
    StartupEnv,
    | "TELEGRAM_BOT_TOKEN"
    | "DISCORD_BOT_TOKEN"
    | "SLACK_BOT_TOKEN"
    | "SLACK_APP_TOKEN"
  >,
): void {
  config.channels ??= {};

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
}

/**
 * Log the environment snapshot (redacts shared secrets).
 */
export function logEnvironment(env: StartupEnv): void {
  log("Environment snapshot:", {
    // Claw-specific — safe to log in full
    R2_BUCKET_NAME: env.R2_BUCKET_NAME ?? "(not set)",
    OPENCLAW_GATEWAY_TOKEN: env.OPENCLAW_GATEWAY_TOKEN ?? "(not set)",
    OPENCLAW_SITE_URL: env.OPENCLAW_SITE_URL ?? "(not set)",
    OPENCLAW_ALLOWED_ORIGINS: env.OPENCLAW_ALLOWED_ORIGINS ?? "(not set)",
    CF_ACCOUNT_ID: env.CF_ACCOUNT_ID ?? "(not set)",
    ANTHROPIC_BASE_URL: env.ANTHROPIC_BASE_URL ?? "(not set)",
    // Shared secrets — presence only
    ANTHROPIC_API_KEY: env.ANTHROPIC_API_KEY ? "(set)" : "(not set)",
    R2_ACCESS_KEY_ID: env.R2_ACCESS_KEY_ID ? "(set)" : "(not set)",
    R2_SECRET_ACCESS_KEY: env.R2_SECRET_ACCESS_KEY ? "(set)" : "(not set)",
    DISCORD_BOT_TOKEN: env.DISCORD_BOT_TOKEN ? "(set)" : "(not set)",
    TELEGRAM_BOT_TOKEN: env.TELEGRAM_BOT_TOKEN ? "(set)" : "(not set)",
    SLACK_BOT_TOKEN: env.SLACK_BOT_TOKEN ? "(set)" : "(not set)",
    SLACK_APP_TOKEN: env.SLACK_APP_TOKEN ? "(set)" : "(not set)",
  });
}

/**
 * Produce a redacted version of the config for logging.
 */
export function redactConfig(
  config: OpenClawStartupConfig,
): OpenClawStartupConfig {
  const redacted = structuredClone(config);

  // Redact provider API keys
  if (redacted.models?.providers) {
    for (const p of Object.values(redacted.models.providers) as Record<
      string,
      unknown
    >[]) {
      if (p.apiKey) p.apiKey = "(redacted)";
    }
  }

  // Redact channel tokens
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

  // Redact gateway auth token
  if (redacted.gateway?.auth?.token) {
    redacted.gateway.auth.token = "(redacted)";
  }

  return redacted;
}
