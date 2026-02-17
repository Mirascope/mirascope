/**
 * @fileoverview Centralized application settings and environment variable validation.
 *
 * This module provides the `Settings` service which validates and provides access to
 * all required environment variables. Settings is the ONLY place in the codebase that
 * should access `process.env` directly.
 *
 * ## Architecture
 *
 * ```
 * process.env (unknown strings)
 *     ↓
 * Settings.Live layer (validates ALL env vars)
 *     ↓ fails with SettingsValidationError if any missing
 * SettingsConfig (all fields guaranteed non-empty strings)
 *     ↓
 * Stripe.layer(settings.stripe)     ← Can't fail, types guarantee values
 * Resend.layer(settings.resend)     ← Can't fail, types guarantee values
 * Database.layer(settings.database) ← Can't fail, types guarantee values
 * ```
 *
 * ## Usage
 *
 * ```ts
 * import { Settings } from "@/settings";
 *
 * const program = Effect.gen(function* () {
 *   const settings = yield* Settings;
 *   const dbUrl = settings.databaseUrl; // Guaranteed non-empty string
 * });
 * ```
 */

import { Context, Effect, Layer } from "effect";

import type { CloudflareConfig } from "@/cloudflare/config";
import type { PlanTier } from "@/payments/plans";

import { SettingsValidationError } from "@/errors";

// =============================================================================
// Config Types
// =============================================================================

/**
 * GitHub OAuth configuration.
 */
export type GitHubConfig = {
  readonly clientId: string;
  readonly clientSecret: string;
  readonly callbackUrl: string;
};

/**
 * Google OAuth configuration.
 */
export type GoogleConfig = {
  readonly clientId: string;
  readonly clientSecret: string;
  readonly callbackUrl: string;
};

/**
 * Stripe payments configuration.
 * Used by Settings and Stripe.layer().
 */
export type StripeConfig = {
  readonly secretKey: string;
  readonly webhookSecret: string;
  readonly routerPriceId: string;
  readonly routerMeterId: string;
  readonly cloudFreePriceId: string;
  readonly cloudProPriceId: string;
  readonly cloudTeamPriceId: string;
  readonly cloudSpansPriceId: string;
  readonly cloudSpansMeterId: string;
};

/**
 * Resend email configuration.
 * Used by Settings and Emails.layer().
 */
export type ResendConfig = {
  readonly apiKey: string;
  readonly audienceSegmentId: string;
};

/**
 * Router provider API keys configuration.
 */
export type RouterConfig = {
  readonly openaiApiKey: string;
  readonly anthropicApiKey: string;
  readonly geminiApiKey: string;
};

/**
 * ClickHouse TLS configuration.
 */
export type ClickHouseTlsConfig = {
  readonly enabled: boolean;
  readonly ca: string;
  readonly skipVerify: boolean;
  readonly hostnameVerify: boolean;
  readonly minVersion: string;
};

/**
 * ClickHouse database configuration.
 */
export type ClickHouseConfig = {
  readonly url: string;
  readonly user: string;
  readonly password: string;
  readonly database: string;
  readonly tls: ClickHouseTlsConfig;
};

/**
 * PostHog analytics configuration.
 * Used by Settings and PostHog.layer().
 */
export type PostHogConfig = {
  readonly apiKey: string;
  readonly host: string;
};

/**
 * Google Analytics configuration.
 */
export type GoogleAnalyticsConfig = {
  readonly measurementId: string;
  readonly apiSecret: string;
};

/**
 * Frontend (Vite) configuration.
 * These are validated at startup to ensure deployment is complete,
 * but accessed via import.meta.env on the client side.
 */
export type FrontendConfig = {
  readonly stripePublishableKey: string;
  readonly posthogApiKey: string;
  readonly posthogHost: string;
  readonly googleAnalyticsMeasurementId: string;
};

/**
 * Encryption key configuration for claw secrets.
 *
 * Keys are versioned so that rotation is possible without re-encrypting
 * all rows at once. The `secretsKeyId` column in the DB records which
 * env-var name was used to encrypt a given row, and on decrypt we look
 * up that name in this map.
 */
export type EncryptionKeysConfig = {
  readonly [keyId: string]: string; // keyId → base64-encoded 256-bit key
};

/**
 * Complete application settings configuration.
 * All fields are required and guaranteed to be non-empty strings.
 */
export type SettingsConfig = {
  // Core
  readonly env: string;
  readonly databaseUrl: string;
  readonly siteUrl: string;

  // Development — false when disabled, or the plan tier to simulate ("free"|"pro"|"team")
  readonly mockDeployment: false | PlanTier;

  // Auth
  readonly github: GitHubConfig;
  readonly google: GoogleConfig;

  // Payments
  readonly stripe: StripeConfig;

  // Email
  readonly resend: ResendConfig;

  // Router
  readonly router: RouterConfig;

  // ClickHouse
  readonly clickhouse: ClickHouseConfig;

  // Analytics
  readonly posthog: PostHogConfig;
  readonly googleAnalytics: GoogleAnalyticsConfig;

  // Frontend (validated but not accessed server-side)
  readonly frontend: FrontendConfig;

  // Cloudflare infrastructure
  readonly cloudflare: CloudflareConfig;

  // Encryption
  readonly encryptionKeys: EncryptionKeysConfig;
  readonly activeEncryptionKeyId: string;

  // OpenClaw gateway (optional — for dev/local WS proxy)
  readonly openclawGatewayWsUrl?: string;

  // Deployment target: "cloudflare" (default) or "mac-deployment"
  readonly deploymentTarget: "cloudflare" | "mac-deployment";
};

// =============================================================================
// Environment Source Abstraction
// =============================================================================

/**
 * Abstraction over environment variable sources.
 * Allows the same validation logic for process.env and Cloudflare Workers env.
 */
export type EnvSource = {
  get: (name: string) => string | undefined;
};

/**
 * EnvSource that reads from process.env.
 */
export const processEnvSource: EnvSource = {
  get: (name) => process.env[name],
};

/**
 * Hyperdrive binding type for Cloudflare Workers.
 */
export type HyperdriveBinding = {
  connectionString: string;
};

/**
 * Cloudflare Workers environment type for settings extraction.
 * Extends as needed for additional bindings.
 */
export type CloudflareEnvironment = {
  MOCK_DEPLOYMENT?: string;
  ENVIRONMENT?: string;
  HYPERDRIVE?: HyperdriveBinding;
  SITE_URL?: string;
  GITHUB_CLIENT_ID?: string;
  GITHUB_CLIENT_SECRET?: string;
  GITHUB_CALLBACK_URL?: string;
  GOOGLE_CLIENT_ID?: string;
  GOOGLE_CLIENT_SECRET?: string;
  GOOGLE_CALLBACK_URL?: string;
  STRIPE_SECRET_KEY?: string;
  STRIPE_WEBHOOK_SECRET?: string;
  STRIPE_ROUTER_PRICE_ID?: string;
  STRIPE_ROUTER_METER_ID?: string;
  STRIPE_CLOUD_FREE_PRICE_ID?: string;
  STRIPE_CLOUD_PRO_PRICE_ID?: string;
  STRIPE_CLOUD_TEAM_PRICE_ID?: string;
  STRIPE_CLOUD_SPANS_PRICE_ID?: string;
  STRIPE_CLOUD_SPANS_METER_ID?: string;
  RESEND_API_KEY?: string;
  RESEND_AUDIENCE_SEGMENT_ID?: string;
  OPENAI_API_KEY?: string;
  ANTHROPIC_API_KEY?: string;
  GEMINI_API_KEY?: string;
  CLICKHOUSE_URL?: string;
  CLICKHOUSE_USER?: string;
  CLICKHOUSE_PASSWORD?: string;
  CLICKHOUSE_DATABASE?: string;
  CLICKHOUSE_TLS_ENABLED?: string;
  CLICKHOUSE_TLS_CA?: string;
  CLICKHOUSE_TLS_SKIP_VERIFY?: string;
  CLICKHOUSE_TLS_HOSTNAME_VERIFY?: string;
  CLICKHOUSE_TLS_MIN_VERSION?: string;
  POSTHOG_API_KEY?: string;
  POSTHOG_HOST?: string;
  GOOGLE_ANALYTICS_MEASUREMENT_ID?: string;
  GOOGLE_ANALYTICS_API_SECRET?: string;
  VITE_STRIPE_PUBLISHABLE_KEY?: string;
  VITE_POSTHOG_API_KEY?: string;
  VITE_POSTHOG_HOST?: string;
  VITE_GOOGLE_ANALYTICS_MEASUREMENT_ID?: string;
  // Cloudflare infrastructure (for claw deployment)
  CLOUDFLARE_ACCOUNT_ID?: string;
  CLOUDFLARE_API_TOKEN?: string;
  CF_R2_READ_PERMISSION_GROUP_ID?: string;
  CF_R2_WRITE_PERMISSION_GROUP_ID?: string;
  CF_DO_NAMESPACE_ID?: string;
  CF_DISPATCH_WORKER_BASE_URL?: string;
  // Encryption keys for claw secrets (versioned)
  CLAW_SECRETS_ENCRYPTION_KEY_V1?: string;
  // OpenClaw gateway (dev/local only)
  OPENCLAW_GATEWAY_WS_URL?: string;
  OPENCLAW_GATEWAY_TOKEN?: string;
  DEPLOYMENT_TARGET?: string;
};

/**
 * Creates an EnvSource from Cloudflare Workers environment bindings.
 * Only returns string values, excludes bindings like HYPERDRIVE.
 */
export const cloudflareEnvSource = (env: CloudflareEnvironment): EnvSource => ({
  get: (name) => {
    const value = env[name as keyof CloudflareEnvironment];
    return typeof value === "string" ? value : undefined;
  },
});

// =============================================================================
// Validation
// =============================================================================

/**
 * Validates environment variables from any source and returns SettingsConfig.
 */
function validateSettingsFromSource(
  source: EnvSource,
): Effect.Effect<SettingsConfig, SettingsValidationError> {
  return Effect.gen(function* () {
    const missing: string[] = [];
    const mockDeploymentRaw = source.get("MOCK_DEPLOYMENT")?.trim();
    const VALID_MOCK_TIERS = ["free", "pro", "team"] as const;
    const mockDeployment: false | PlanTier =
      mockDeploymentRaw === "true"
        ? "free"
        : VALID_MOCK_TIERS.includes(mockDeploymentRaw as PlanTier)
          ? (mockDeploymentRaw as PlanTier)
          : false;

    // Helper: validate required env var, collect missing ones
    const required = (name: string): string => {
      const value = source.get(name)?.trim();
      if (!value) {
        missing.push(name);
        return ""; // Placeholder - we'll fail before this is used
      }
      return value;
    };

    const optional = (name: string): string => {
      return source.get(name)?.trim() ?? "";
    };

    // Helper: parse boolean env var (required)
    const requiredBool = (name: string): boolean => {
      const value = source.get(name)?.trim();
      if (!value) {
        missing.push(name);
        return false;
      }
      return value === "true";
    };

    const settings: SettingsConfig = {
      env: required("ENVIRONMENT"),
      databaseUrl: required("DATABASE_URL"),
      siteUrl: required("SITE_URL"),
      mockDeployment,

      github: {
        clientId: required("GITHUB_CLIENT_ID"),
        clientSecret: required("GITHUB_CLIENT_SECRET"),
        callbackUrl: required("GITHUB_CALLBACK_URL"),
      },

      google: {
        clientId: required("GOOGLE_CLIENT_ID"),
        clientSecret: required("GOOGLE_CLIENT_SECRET"),
        callbackUrl: required("GOOGLE_CALLBACK_URL"),
      },

      stripe: {
        secretKey: required("STRIPE_SECRET_KEY"),
        webhookSecret: required("STRIPE_WEBHOOK_SECRET"),
        routerPriceId: required("STRIPE_ROUTER_PRICE_ID"),
        routerMeterId: required("STRIPE_ROUTER_METER_ID"),
        cloudFreePriceId: required("STRIPE_CLOUD_FREE_PRICE_ID"),
        cloudProPriceId: required("STRIPE_CLOUD_PRO_PRICE_ID"),
        cloudTeamPriceId: required("STRIPE_CLOUD_TEAM_PRICE_ID"),
        cloudSpansPriceId: required("STRIPE_CLOUD_SPANS_PRICE_ID"),
        cloudSpansMeterId: required("STRIPE_CLOUD_SPANS_METER_ID"),
      },

      resend: {
        apiKey: required("RESEND_API_KEY"),
        audienceSegmentId: required("RESEND_AUDIENCE_SEGMENT_ID"),
      },

      router: {
        openaiApiKey: required("OPENAI_API_KEY"),
        anthropicApiKey: required("ANTHROPIC_API_KEY"),
        geminiApiKey: required("GEMINI_API_KEY"),
      },

      clickhouse: {
        url: required("CLICKHOUSE_URL"),
        user: required("CLICKHOUSE_USER"),
        password: required("CLICKHOUSE_PASSWORD"),
        database: required("CLICKHOUSE_DATABASE"),
        tls: {
          enabled: requiredBool("CLICKHOUSE_TLS_ENABLED"),
          ca: optional("CLICKHOUSE_TLS_CA"), // Not supported by @clickhouse/client-web
          skipVerify: requiredBool("CLICKHOUSE_TLS_SKIP_VERIFY"),
          hostnameVerify: requiredBool("CLICKHOUSE_TLS_HOSTNAME_VERIFY"),
          minVersion: required("CLICKHOUSE_TLS_MIN_VERSION"),
        },
      },

      posthog: {
        apiKey: required("POSTHOG_API_KEY"),
        host: required("POSTHOG_HOST"),
      },

      googleAnalytics: {
        measurementId: required("GOOGLE_ANALYTICS_MEASUREMENT_ID"),
        apiSecret: required("GOOGLE_ANALYTICS_API_SECRET"),
      },

      frontend: {
        stripePublishableKey: required("VITE_STRIPE_PUBLISHABLE_KEY"),
        posthogApiKey: required("VITE_POSTHOG_API_KEY"),
        posthogHost: required("VITE_POSTHOG_HOST"),
        googleAnalyticsMeasurementId: required(
          "VITE_GOOGLE_ANALYTICS_MEASUREMENT_ID",
        ),
      },

      cloudflare: {
        accountId: mockDeployment
          ? optional("CLOUDFLARE_ACCOUNT_ID")
          : required("CLOUDFLARE_ACCOUNT_ID"),
        apiToken: mockDeployment
          ? optional("CLOUDFLARE_API_TOKEN")
          : required("CLOUDFLARE_API_TOKEN"),
        r2BucketItemReadPermissionGroupId: mockDeployment
          ? optional("CF_R2_READ_PERMISSION_GROUP_ID")
          : required("CF_R2_READ_PERMISSION_GROUP_ID"),
        r2BucketItemWritePermissionGroupId: mockDeployment
          ? optional("CF_R2_WRITE_PERMISSION_GROUP_ID")
          : required("CF_R2_WRITE_PERMISSION_GROUP_ID"),
        durableObjectNamespaceId: mockDeployment
          ? optional("CF_DO_NAMESPACE_ID")
          : required("CF_DO_NAMESPACE_ID"),
        dispatchWorkerBaseUrl: mockDeployment
          ? optional("CF_DISPATCH_WORKER_BASE_URL")
          : required("CF_DISPATCH_WORKER_BASE_URL"),
      },

      encryptionKeys: {
        CLAW_SECRETS_ENCRYPTION_KEY_V1: mockDeployment
          ? optional("CLAW_SECRETS_ENCRYPTION_KEY_V1") ||
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
          : required("CLAW_SECRETS_ENCRYPTION_KEY_V1"),
      },
      activeEncryptionKeyId: "CLAW_SECRETS_ENCRYPTION_KEY_V1",

      openclawGatewayWsUrl: optional("OPENCLAW_GATEWAY_WS_URL") || undefined,

      deploymentTarget:
        (optional("DEPLOYMENT_TARGET") as "cloudflare" | "mac-deployment") ||
        "cloudflare",
    };

    // Fail if any variables are missing
    if (missing.length > 0) {
      return yield* Effect.fail(
        new SettingsValidationError({
          message: `Missing required environment variables:\n  - ${missing.join("\n  - ")}`,
          missingVariables: missing,
        }),
      );
    }

    // ClickHouse TLS validation for @clickhouse/client-web compatibility
    // These limitations apply to ALL environments since we use the web client
    const tlsErrors: string[] = [];
    if (settings.clickhouse.tls.enabled) {
      if (settings.clickhouse.tls.skipVerify) {
        tlsErrors.push(
          "CLICKHOUSE_TLS_SKIP_VERIFY=true is not supported by @clickhouse/client-web",
        );
      }
      if (!settings.clickhouse.tls.hostnameVerify) {
        tlsErrors.push(
          "CLICKHOUSE_TLS_HOSTNAME_VERIFY=false is not supported by @clickhouse/client-web",
        );
      }
      if (settings.clickhouse.tls.ca) {
        tlsErrors.push(
          "CLICKHOUSE_TLS_CA is not supported by @clickhouse/client-web (uses system CA)",
        );
      }
      if (
        settings.clickhouse.tls.minVersion &&
        settings.clickhouse.tls.minVersion !== "1.2"
      ) {
        tlsErrors.push(
          `CLICKHOUSE_TLS_MIN_VERSION=${settings.clickhouse.tls.minVersion} is not supported by @clickhouse/client-web`,
        );
      }
    }

    // Production-specific validation
    if (settings.env === "production") {
      if (!settings.clickhouse.tls.enabled) {
        tlsErrors.push("CLICKHOUSE_TLS_ENABLED=true is required in production");
      }
      if (!settings.clickhouse.url.startsWith("https://")) {
        tlsErrors.push("CLICKHOUSE_URL must use https:// in production");
      }
    }

    if (tlsErrors.length > 0) {
      return yield* Effect.fail(
        new SettingsValidationError({
          message: `ClickHouse TLS configuration errors:\n  - ${tlsErrors.join("\n  - ")}`,
          missingVariables: [],
        }),
      );
    }

    return settings;
  });
}

/**
 * Validates settings from process.env.
 */
export function validateSettings(): Effect.Effect<
  SettingsConfig,
  SettingsValidationError
> {
  return validateSettingsFromSource(processEnvSource);
}

/**
 * Validates settings from Cloudflare Workers environment bindings.
 * Uses HYPERDRIVE.connectionString for databaseUrl.
 */
export function validateSettingsFromEnvironment(
  env: CloudflareEnvironment,
): Effect.Effect<SettingsConfig, SettingsValidationError> {
  // Check HYPERDRIVE binding first with clear error message
  if (!env.HYPERDRIVE?.connectionString) {
    return Effect.fail(
      new SettingsValidationError({
        message:
          "HYPERDRIVE binding not configured. Ensure HYPERDRIVE is set up in wrangler.jsonc.",
        missingVariables: ["HYPERDRIVE"],
      }),
    );
  }

  // Create an env source that gets DATABASE_URL from HYPERDRIVE binding
  const envSource: EnvSource = {
    get: (name) => {
      if (name === "DATABASE_URL") {
        return env.HYPERDRIVE?.connectionString;
      }
      return env[name as keyof CloudflareEnvironment] as string | undefined;
    },
  };
  return validateSettingsFromSource(envSource);
}

// =============================================================================
// Settings Service
// =============================================================================

/**
 * Settings service providing validated application configuration.
 *
 * This is the ONLY place in the codebase that should access process.env.
 * All other code should depend on the Settings service to get configuration.
 *
 * @example
 * ```ts
 * const program = Effect.gen(function* () {
 *   const settings = yield* Settings;
 *   const dbUrl = settings.databaseUrl; // Guaranteed non-empty string
 * });
 * ```
 */
export class Settings extends Context.Tag("Settings")<
  Settings,
  SettingsConfig
>() {
  /**
   * Live layer that validates and provides Settings from process.env.
   * Fails with SettingsValidationError if any required env vars are missing.
   */
  static Live = Layer.effect(Settings, validateSettings());

  /**
   * Creates a Live layer from Cloudflare Workers environment bindings.
   */
  static LiveFromEnvironment = (env: CloudflareEnvironment) =>
    Layer.effect(Settings, validateSettingsFromEnvironment(env));
}
