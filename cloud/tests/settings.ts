/**
 * @fileoverview Mock Settings helpers for testing.
 *
 * This module provides utilities for creating mock SettingsConfig instances
 * and Settings layers for use in tests.
 */

import { Layer } from "effect";

import { Settings, type SettingsConfig } from "@/settings";

/**
 * Creates a complete mock SettingsConfig for testing.
 * All values are valid test defaults.
 *
 * @param overrides - Partial overrides to customize the mock settings
 * @returns A complete SettingsConfig with test values
 *
 * @example
 * ```ts
 * // Use defaults
 * const settings = createMockSettings();
 *
 * // Override specific values
 * const settings = createMockSettings({
 *   env: "production",
 *   stripe: { ...createMockSettings().stripe, secretKey: "sk_live_xxx" }
 * });
 * ```
 */
export function createMockSettings(
  overrides: Partial<SettingsConfig> = {},
): SettingsConfig {
  const defaults: SettingsConfig = {
    env: "test",
    databaseUrl: "postgres://test:test@localhost:5432/test",
    siteUrl: "http://localhost:3000",
    mockDeployment: false,

    github: {
      clientId: "test-github-client-id",
      clientSecret: "test-github-client-secret",
      callbackUrl: "http://localhost:3000/auth/github/callback",
    },

    google: {
      clientId: "test-google-client-id",
      clientSecret: "test-google-client-secret",
      callbackUrl: "http://localhost:3000/auth/google/callback",
    },

    stripe: {
      secretKey: "sk_test_xxx",
      webhookSecret: "whsec_xxx",
      routerPriceId: "price_router_xxx",
      routerMeterId: "mtr_router_xxx",
      cloudFreePriceId: "price_free_xxx",
      cloudProPriceId: "price_pro_xxx",
      cloudTeamPriceId: "price_team_xxx",
      cloudSpansPriceId: "price_spans_xxx",
      cloudSpansMeterId: "mtr_spans_xxx",
    },

    resend: {
      apiKey: "re_test_xxx",
      audienceSegmentId: "aud_xxx",
    },

    router: {
      openaiApiKey: "sk-test-openai",
      anthropicApiKey: "sk-ant-test",
      geminiApiKey: "test-gemini-key",
    },

    clickhouse: {
      url: "http://localhost:8123",
      user: "default",
      password: "test-password",
      database: "test_db",
      tls: {
        enabled: false,
        ca: "", // Not supported by @clickhouse/client-web
        skipVerify: false,
        hostnameVerify: true,
        minVersion: "1.2",
      },
    },

    posthog: {
      apiKey: "phc_test",
      host: "https://app.posthog.com",
    },

    googleAnalytics: {
      measurementId: "G-TEST",
      apiSecret: "ga-secret",
    },

    frontend: {
      stripePublishableKey: "pk_test_xxx",
      posthogApiKey: "phc_test",
      posthogHost: "https://app.posthog.com",
      googleAnalyticsMeasurementId: "G-TEST",
    },

    cloudflare: {
      accountId: "test-cf-account-id",
      apiToken: "test-cf-api-token",
      r2BucketItemReadPermissionGroupId: "test-r2-read-perm",
      r2BucketItemWritePermissionGroupId: "test-r2-write-perm",
      durableObjectNamespaceId: "test-do-namespace-id",
      dispatchWorkerBaseUrl: "https://dispatch.test.workers.dev",
    },

    encryptionKeys: {
      CLAW_SECRETS_ENCRYPTION_KEY_V1:
        "S0YrcgEScoOL1ALp/w+xI90P9O8h4s3OzEXtzlhBbHQ=",
    },
    activeEncryptionKeyId: "CLAW_SECRETS_ENCRYPTION_KEY_V1",

    deploymentTarget: "cloudflare",
  };

  return {
    ...defaults,
    ...overrides,
    // Deep merge nested objects if provided
    github: { ...defaults.github, ...overrides.github },
    google: { ...defaults.google, ...overrides.google },
    stripe: { ...defaults.stripe, ...overrides.stripe },
    resend: { ...defaults.resend, ...overrides.resend },
    router: { ...defaults.router, ...overrides.router },
    clickhouse: {
      ...defaults.clickhouse,
      ...overrides.clickhouse,
      tls: {
        ...defaults.clickhouse.tls,
        ...overrides.clickhouse?.tls,
      },
    },
    posthog: { ...defaults.posthog, ...overrides.posthog },
    googleAnalytics: {
      ...defaults.googleAnalytics,
      ...overrides.googleAnalytics,
    },
    frontend: { ...defaults.frontend, ...overrides.frontend },
    cloudflare: { ...defaults.cloudflare, ...overrides.cloudflare },
    encryptionKeys: {
      ...defaults.encryptionKeys,
      ...overrides.encryptionKeys,
    },
  };
}

/**
 * Creates a Settings layer with mock values for testing.
 *
 * @param overrides - Partial overrides to customize the mock settings
 * @returns A Layer providing Settings with test values
 *
 * @example
 * ```ts
 * const program = Effect.gen(function* () {
 *   const settings = yield* Settings;
 *   // settings has test values
 * });
 *
 * program.pipe(Effect.provide(MockSettingsLayer()));
 * ```
 */
export const MockSettingsLayer = (overrides: Partial<SettingsConfig> = {}) =>
  Layer.succeed(Settings, createMockSettings(overrides));

/**
 * Creates a complete mock environment variable object for testing Settings validation.
 * All values are valid test defaults matching the expected environment variable names.
 *
 * @param overrides - Partial overrides to customize specific env vars
 * @returns A complete environment object suitable for testing
 */
export function createMockEnv(
  overrides: Record<string, string | undefined> = {},
): Record<string, string> {
  const defaults: Record<string, string> = {
    ENVIRONMENT: "test",
    DATABASE_URL: "postgres://test:test@localhost:5432/test",
    SITE_URL: "http://localhost:3000",
    GITHUB_CLIENT_ID: "test-github-client-id",
    GITHUB_CLIENT_SECRET: "test-github-client-secret",
    GITHUB_CALLBACK_URL: "http://localhost:3000/auth/github/callback",
    GOOGLE_CLIENT_ID: "test-google-client-id",
    GOOGLE_CLIENT_SECRET: "test-google-client-secret",
    GOOGLE_CALLBACK_URL: "http://localhost:3000/auth/google/callback",
    STRIPE_SECRET_KEY: "sk_test_xxx",
    STRIPE_WEBHOOK_SECRET: "whsec_xxx",
    STRIPE_ROUTER_PRICE_ID: "price_router_xxx",
    STRIPE_ROUTER_METER_ID: "mtr_router_xxx",
    STRIPE_CLOUD_FREE_PRICE_ID: "price_free_xxx",
    STRIPE_CLOUD_PRO_PRICE_ID: "price_pro_xxx",
    STRIPE_CLOUD_TEAM_PRICE_ID: "price_team_xxx",
    STRIPE_CLOUD_SPANS_PRICE_ID: "price_spans_xxx",
    STRIPE_CLOUD_SPANS_METER_ID: "mtr_spans_xxx",
    RESEND_API_KEY: "re_test_xxx",
    RESEND_AUDIENCE_SEGMENT_ID: "aud_xxx",
    OPENAI_API_KEY: "sk-test-openai",
    ANTHROPIC_API_KEY: "sk-ant-test",
    GEMINI_API_KEY: "test-gemini-key",
    CLICKHOUSE_URL: "http://localhost:8123",
    CLICKHOUSE_USER: "default",
    CLICKHOUSE_PASSWORD: "test-password",
    CLICKHOUSE_DATABASE: "test_db",
    CLICKHOUSE_TLS_ENABLED: "false",
    CLICKHOUSE_TLS_CA: "", // Not supported by @clickhouse/client-web
    CLICKHOUSE_TLS_SKIP_VERIFY: "false",
    CLICKHOUSE_TLS_HOSTNAME_VERIFY: "true",
    CLICKHOUSE_TLS_MIN_VERSION: "1.2",
    POSTHOG_API_KEY: "phc_test",
    POSTHOG_HOST: "https://app.posthog.com",
    GOOGLE_ANALYTICS_MEASUREMENT_ID: "G-TEST",
    GOOGLE_ANALYTICS_API_SECRET: "ga-secret",
    VITE_STRIPE_PUBLISHABLE_KEY: "pk_test_xxx",
    VITE_POSTHOG_API_KEY: "phc_test",
    VITE_POSTHOG_HOST: "https://app.posthog.com",
    VITE_GOOGLE_ANALYTICS_MEASUREMENT_ID: "G-TEST",
    CLOUDFLARE_ACCOUNT_ID: "test-cf-account-id",
    CLOUDFLARE_API_TOKEN: "test-cf-api-token",
    CF_R2_READ_PERMISSION_GROUP_ID: "test-r2-read-perm",
    CF_R2_WRITE_PERMISSION_GROUP_ID: "test-r2-write-perm",
    CF_DO_NAMESPACE_ID: "test-do-namespace-id",
    CF_DISPATCH_WORKER_BASE_URL: "https://dispatch.test.workers.dev",
    CLAW_SECRETS_ENCRYPTION_KEY_V1:
      "S0YrcgEScoOL1ALp/w+xI90P9O8h4s3OzEXtzlhBbHQ=",
  };

  // Filter out undefined values from overrides
  const filtered = Object.fromEntries(
    Object.entries({ ...defaults, ...overrides }).filter(
      ([, v]) => v !== undefined,
    ),
  ) as Record<string, string>;

  return filtered;
}
