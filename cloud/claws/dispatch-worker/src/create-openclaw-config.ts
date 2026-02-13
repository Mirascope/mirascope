/**
 * Pure function to create OpenClaw configuration from environment variables.
 *
 * This function takes all necessary environment values as parameters and returns
 * an OpenClawConfig object. It has no side effects and can be easily tested.
 */

import type { OpenClawConfig } from "openclaw/plugin-sdk";

export interface OpenClawEnv {
  // Claw-specific configuration (required)
  R2_BUCKET_NAME: string;
  OPENCLAW_GATEWAY_TOKEN: string;
  OPENCLAW_SITE_URL: string;
  OPENCLAW_ALLOWED_ORIGINS: string;
  CF_ACCOUNT_ID: string;

  // Anthropic configuration (required)
  ANTHROPIC_BASE_URL: string;
  ANTHROPIC_API_KEY: string;
  PRIMARY_MODEL_ID: string;

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

/**
 * Initializes the nested structure of the config object, ensuring all required
 * sub-objects exist with nullish coalescing assignment.
 */
export function initializeConfigStructure(config: OpenClawConfig): void {
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
}

/**
 * Configures the gateway settings: port, mode, trusted proxies, auth token,
 * and control UI allowed origins.
 */
export function configureGateway(
  config: OpenClawConfig,
  env: OpenClawEnv,
  options: OpenClawConfigOptions,
): void {
  config.gateway!.port = options.gatewayPort;
  config.gateway!.mode = "local";
  config.gateway!.trustedProxies = ["10.1.0.0"];
  config.gateway!.auth!.token = env.OPENCLAW_GATEWAY_TOKEN;

  const allowedOrigins = env.OPENCLAW_ALLOWED_ORIGINS.split(",")
    .map((o) => o.trim())
    .filter(Boolean);

  if (!allowedOrigins.includes(env.OPENCLAW_SITE_URL)) {
    allowedOrigins.push(env.OPENCLAW_SITE_URL);
  }

  config.gateway!.controlUi = { allowedOrigins };
}

/**
 * Configures the Anthropic provider with base URL, API key, and model cards
 * for all supported Claude models.
 */
export function configureAnthropicProvider(
  config: OpenClawConfig,
  env: OpenClawEnv,
): void {
  const baseUrl = env.ANTHROPIC_BASE_URL.replace(/\/+$/, "");

  config.models!.providers!.anthropic = {
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
}

/**
 * Configures model aliases and the primary model selection.
 * Validates that PRIMARY_MODEL_ID includes a provider prefix (e.g. "anthropic/claude-opus-4-6").
 */
export function configureModelDefaults(
  config: OpenClawConfig,
  env: OpenClawEnv,
): void {
  if (!env.PRIMARY_MODEL_ID.includes("/")) {
    throw new Error(
      `PRIMARY_MODEL_ID must include a provider prefix (e.g., "anthropic/claude-opus-4-6"), got: ${env.PRIMARY_MODEL_ID}`,
    );
  }

  config.agents!.defaults!.models!["anthropic/claude-opus-4-6"] = {
    alias: "Opus 4.6",
  };
  config.agents!.defaults!.models!["anthropic/claude-opus-4-5"] = {
    alias: "Opus 4.5",
  };
  config.agents!.defaults!.models!["anthropic/claude-sonnet-4-5"] = {
    alias: "Sonnet 4.5",
  };
  config.agents!.defaults!.models!["anthropic/claude-haiku-4-5"] = {
    alias: "Haiku 4.5",
  };
  config.agents!.defaults!.model!.primary = env.PRIMARY_MODEL_ID;
}

/**
 * Configures optional channel integrations (Telegram, Discord, Slack).
 * Only configures channels whose tokens are present in the environment.
 */
export function configureChannels(
  config: OpenClawConfig,
  env: OpenClawEnv,
): void {
  if (env.TELEGRAM_BOT_TOKEN) {
    config.channels!.telegram = {
      ...((config.channels!.telegram as object) ?? {}),
      botToken: env.TELEGRAM_BOT_TOKEN,
      enabled: true,
    };
  }

  if (env.DISCORD_BOT_TOKEN) {
    config.channels!.discord = {
      ...((config.channels!.discord as object) ?? {}),
      token: env.DISCORD_BOT_TOKEN,
      enabled: true,
    };
  }

  if (env.SLACK_BOT_TOKEN && env.SLACK_APP_TOKEN) {
    config.channels!.slack = {
      ...((config.channels!.slack as object) ?? {}),
      botToken: env.SLACK_BOT_TOKEN,
      appToken: env.SLACK_APP_TOKEN,
      enabled: true,
    };
  }
}

/**
 * Configures the default workspace directory for agents.
 */
export function configureWorkspace(
  config: OpenClawConfig,
  options: OpenClawConfigOptions,
): void {
  config.agents!.defaults!.workspace = options.workspaceDir;
}

/**
 * Configures environment variables that OpenClaw needs at runtime,
 * such as the gateway token.
 */
export function configureEnvVars(
  config: OpenClawConfig,
  env: OpenClawEnv,
): void {
  config.env!.vars!.OPENCLAW_GATEWAY_TOKEN = env.OPENCLAW_GATEWAY_TOKEN;
}

/**
 * Creates an OpenClaw configuration object from environment variables.
 *
 * Orchestrates the configuration by delegating to focused sub-functions,
 * each responsible for a logical grouping of settings.
 *
 * @param env - Environment variables (typically from process.env)
 * @param options - Configuration options (workspace dir, port, existing config)
 * @returns A complete OpenClawConfig object
 */
export function createOpenClawConfig(
  env: OpenClawEnv,
  options: OpenClawConfigOptions,
): OpenClawConfig {
  const config: OpenClawConfig = options.existingConfig ?? {};

  initializeConfigStructure(config);
  configureWorkspace(config, options);
  configureGateway(config, env, options);
  configureEnvVars(config, env);
  configureAnthropicProvider(config, env);
  configureModelDefaults(config, env);
  configureChannels(config, env);

  return config;
}
