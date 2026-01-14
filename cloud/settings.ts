import { Context } from "effect";

export type Settings = {
  readonly env: string;
  readonly DATABASE_URL?: string;
  readonly GOOGLE_CLIENT_ID?: string;
  readonly GOOGLE_CLIENT_SECRET?: string;
  readonly GOOGLE_CALLBACK_URL?: string;
  readonly GITHUB_CLIENT_ID?: string;
  readonly GITHUB_CLIENT_SECRET?: string;
  readonly GITHUB_CALLBACK_URL?: string;
  readonly SITE_URL?: string;
  // ROUTER KEYS
  readonly ANTHROPIC_API_KEY?: string;
  readonly GEMINI_API_KEY?: string;
  readonly OPENAI_API_KEY?: string;
  // ClickHouse settings
  readonly CLICKHOUSE_URL?: string;
  readonly CLICKHOUSE_USER?: string;
  readonly CLICKHOUSE_PASSWORD?: string;
  readonly CLICKHOUSE_DATABASE?: string;
  // TLS settings (Node.js environment only)
  readonly CLICKHOUSE_TLS_ENABLED?: boolean;
  readonly CLICKHOUSE_TLS_CA?: string;
  readonly CLICKHOUSE_TLS_SKIP_VERIFY?: boolean;
  readonly CLICKHOUSE_TLS_HOSTNAME_VERIFY?: boolean;
  readonly CLICKHOUSE_TLS_MIN_VERSION?: string;
  // Analytics settings
  readonly GOOGLE_ANALYTICS_MEASUREMENT_ID?: string;
  readonly GOOGLE_ANALYTICS_API_SECRET?: string;
  readonly POSTHOG_API_KEY?: string;
  readonly POSTHOG_HOST?: string;
};

export class SettingsService extends Context.Tag("SettingsService")<
  SettingsService,
  Settings
>() {}

export function getSettings(): Settings {
  const clickhouseTlsHostnameVerifyEnv =
    process.env.CLICKHOUSE_TLS_HOSTNAME_VERIFY;

  const settings: Settings = {
    env: process.env.ENVIRONMENT || "local",
    DATABASE_URL: process.env.DATABASE_URL,
    GITHUB_CLIENT_ID: process.env.GITHUB_CLIENT_ID,
    GITHUB_CLIENT_SECRET: process.env.GITHUB_CLIENT_SECRET,
    GITHUB_CALLBACK_URL: process.env.GITHUB_CALLBACK_URL,
    GOOGLE_CLIENT_ID: process.env.GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET,
    GOOGLE_CALLBACK_URL: process.env.GOOGLE_CALLBACK_URL,
    SITE_URL: process.env.SITE_URL,
    // ROUTER KEYS
    ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY,
    GEMINI_API_KEY: process.env.GEMINI_API_KEY,
    OPENAI_API_KEY: process.env.OPENAI_API_KEY,
    // ClickHouse settings
    CLICKHOUSE_URL: process.env.CLICKHOUSE_URL || "http://localhost:8123",
    CLICKHOUSE_USER: process.env.CLICKHOUSE_USER || "default",
    CLICKHOUSE_PASSWORD: process.env.CLICKHOUSE_PASSWORD,
    CLICKHOUSE_DATABASE:
      process.env.CLICKHOUSE_DATABASE || "mirascope_analytics",
    // TLS settings
    CLICKHOUSE_TLS_ENABLED: process.env.CLICKHOUSE_TLS_ENABLED === "true",
    CLICKHOUSE_TLS_CA: process.env.CLICKHOUSE_TLS_CA,
    CLICKHOUSE_TLS_SKIP_VERIFY:
      process.env.CLICKHOUSE_TLS_SKIP_VERIFY === "true",
    CLICKHOUSE_TLS_HOSTNAME_VERIFY: clickhouseTlsHostnameVerifyEnv !== "false",
    CLICKHOUSE_TLS_MIN_VERSION:
      process.env.CLICKHOUSE_TLS_MIN_VERSION || "TLSv1.2",
    // Analytics settings
    GOOGLE_ANALYTICS_MEASUREMENT_ID:
      process.env.GOOGLE_ANALYTICS_MEASUREMENT_ID,
    GOOGLE_ANALYTICS_API_SECRET: process.env.GOOGLE_ANALYTICS_API_SECRET,
    POSTHOG_API_KEY: process.env.POSTHOG_API_KEY,
    POSTHOG_HOST: process.env.POSTHOG_HOST || "https://app.posthog.com",
  };

  // Production environment validation (Node.js environment)
  if (settings.env === "production") {
    if (!settings.CLICKHOUSE_TLS_ENABLED) {
      throw new Error("CLICKHOUSE_TLS_ENABLED=true is required in production");
    }
    if (settings.CLICKHOUSE_TLS_SKIP_VERIFY) {
      throw new Error(
        "CLICKHOUSE_TLS_SKIP_VERIFY=true is not allowed in production",
      );
    }
    if (!settings.CLICKHOUSE_TLS_HOSTNAME_VERIFY) {
      throw new Error(
        "CLICKHOUSE_TLS_HOSTNAME_VERIFY=true is required in production",
      );
    }
  }

  return settings;
}

/**
 * Cloudflare Workers environment type for settings extraction.
 * Extends as needed for additional bindings.
 */
export type CloudflareEnvironment = {
  ENVIRONMENT?: string;
  DATABASE_URL?: string;
  CLICKHOUSE_URL?: string;
  CLICKHOUSE_USER?: string;
  CLICKHOUSE_PASSWORD?: string;
  CLICKHOUSE_DATABASE?: string;
  CLICKHOUSE_TLS_ENABLED?: string;
  CLICKHOUSE_TLS_CA?: string;
  CLICKHOUSE_TLS_SKIP_VERIFY?: string;
  CLICKHOUSE_TLS_HOSTNAME_VERIFY?: string;
  // Add other bindings as needed
};

/**
 * Get settings from Cloudflare Workers environment bindings.
 * Used by Queue Consumer, Cron Trigger, etc.
 */
export function getSettingsFromEnvironment(
  env: CloudflareEnvironment,
): Settings {
  const settings: Settings = {
    env: env.ENVIRONMENT || "local",
    DATABASE_URL: env.DATABASE_URL,
    // ClickHouse settings
    CLICKHOUSE_URL: env.CLICKHOUSE_URL || "http://localhost:8123",
    CLICKHOUSE_USER: env.CLICKHOUSE_USER || "default",
    CLICKHOUSE_PASSWORD: env.CLICKHOUSE_PASSWORD,
    CLICKHOUSE_DATABASE: env.CLICKHOUSE_DATABASE || "mirascope_analytics",
    // TLS settings (Workers environment has limited TLS control)
    CLICKHOUSE_TLS_ENABLED: env.CLICKHOUSE_TLS_ENABLED === "true",
    CLICKHOUSE_TLS_CA: env.CLICKHOUSE_TLS_CA,
    CLICKHOUSE_TLS_SKIP_VERIFY: env.CLICKHOUSE_TLS_SKIP_VERIFY === "true",
    CLICKHOUSE_TLS_HOSTNAME_VERIFY:
      env.CLICKHOUSE_TLS_HOSTNAME_VERIFY !== "false",
  };

  return settings;
}
