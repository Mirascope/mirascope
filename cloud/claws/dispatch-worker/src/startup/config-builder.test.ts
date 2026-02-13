import { describe, it, expect } from "vitest";

import {
  buildConfig,
  buildAllowedOrigins,
  redactConfig,
  type StartupEnv,
  type OpenClawStartupConfig,
} from "./config-builder";

describe("buildConfig", () => {
  const minimalEnv: StartupEnv = {};

  it("produces valid config from empty env", () => {
    const config = buildConfig(minimalEnv);

    expect(config.agents?.defaults?.workspace).toBe(
      "/root/.openclaw/workspace",
    );
    expect(config.gateway?.port).toBe(18789);
    expect(config.gateway?.mode).toBe("local");
    expect(config.gateway?.trustedProxies).toEqual(["10.1.0.0"]);
  });

  it("sets gateway auth token when provided", () => {
    const config = buildConfig({ OPENCLAW_GATEWAY_TOKEN: "test-token-123" });

    expect(config.gateway?.auth?.token).toBe("test-token-123");
  });

  it("does not set gateway auth when no token", () => {
    const config = buildConfig(minimalEnv);

    expect(config.gateway?.auth).toBeUndefined();
  });

  it("configures Anthropic provider with base URL and API key", () => {
    const config = buildConfig({
      ANTHROPIC_BASE_URL: "https://example.com/router/v2/anthropic",
      ANTHROPIC_API_KEY: "sk-test-key",
    });

    const provider = config.models?.providers?.anthropic as Record<
      string,
      unknown
    >;
    expect(provider).toBeDefined();
    expect(provider.baseUrl).toBe("https://example.com/router/v2/anthropic");
    expect(provider.apiKey).toBe("sk-test-key");
    expect(provider.api).toBe("anthropic-messages");

    // Should have models
    const models = provider.models as Array<{ id: string }>;
    expect(models).toHaveLength(3);
    expect(models[0].id).toBe("claude-opus-4-5-20251101");

    // Should set primary model
    expect(config.agents?.defaults?.model?.primary).toBe(
      "anthropic/claude-opus-4-5-20251101",
    );

    // Should set model aliases
    expect(
      config.agents?.defaults?.models?.["anthropic/claude-opus-4-5-20251101"],
    ).toEqual({
      alias: "Opus 4.5",
    });
  });

  it("strips trailing slashes from base URL", () => {
    const config = buildConfig({
      ANTHROPIC_BASE_URL: "https://example.com/router///",
      ANTHROPIC_API_KEY: "sk-test",
    });

    const provider = config.models?.providers?.anthropic as Record<
      string,
      unknown
    >;
    expect(provider.baseUrl).toBe("https://example.com/router");
  });

  it("configures Anthropic without base URL (direct API key)", () => {
    const config = buildConfig({ ANTHROPIC_API_KEY: "sk-direct" });

    // No custom provider — uses default
    expect(config.models?.providers?.anthropic).toBeUndefined();
    expect(config.agents?.defaults?.model?.primary).toBe(
      "anthropic/claude-opus-4-5",
    );
  });

  it("configures Telegram channel", () => {
    const config = buildConfig({ TELEGRAM_BOT_TOKEN: "tg-token-123" });

    const telegram = config.channels?.telegram as Record<string, unknown>;
    expect(telegram.botToken).toBe("tg-token-123");
    expect(telegram.enabled).toBe(true);
  });

  it("configures Discord channel", () => {
    const config = buildConfig({ DISCORD_BOT_TOKEN: "dc-token-123" });

    const discord = config.channels?.discord as Record<string, unknown>;
    expect(discord.token).toBe("dc-token-123");
    expect(discord.enabled).toBe(true);
  });

  it("configures Slack channel only when both tokens present", () => {
    // Missing app token — should not configure
    const config1 = buildConfig({ SLACK_BOT_TOKEN: "bot-token" });
    expect(config1.channels?.slack).toBeUndefined();

    // Both tokens — should configure
    const config2 = buildConfig({
      SLACK_BOT_TOKEN: "bot-token",
      SLACK_APP_TOKEN: "app-token",
    });
    const slack = config2.channels?.slack as Record<string, unknown>;
    expect(slack.botToken).toBe("bot-token");
    expect(slack.appToken).toBe("app-token");
    expect(slack.enabled).toBe(true);
  });

  it("merges with existing config", () => {
    const existing: OpenClawStartupConfig = {
      channels: {
        discord: {
          token: "old-token",
          guilds: { "123": { allow: true } },
        },
      },
    };

    const config = buildConfig({ DISCORD_BOT_TOKEN: "new-token" }, existing);

    const discord = config.channels?.discord as Record<string, unknown>;
    expect(discord.token).toBe("new-token");
    expect(discord.enabled).toBe(true);
    // Existing guild config should be preserved via spread
    expect(discord.guilds).toEqual({ "123": { allow: true } });
  });

  it("does not mutate the existing config", () => {
    const existing: OpenClawStartupConfig = {
      gateway: { port: 9999 },
    };

    buildConfig(minimalEnv, existing);

    // Original should be unchanged
    expect(existing.gateway?.port).toBe(9999);
  });
});

describe("buildAllowedOrigins", () => {
  it("returns undefined when no origins", () => {
    expect(buildAllowedOrigins({})).toBeUndefined();
  });

  it("parses comma-separated OPENCLAW_ALLOWED_ORIGINS", () => {
    const result = buildAllowedOrigins({
      OPENCLAW_ALLOWED_ORIGINS: "https://a.com, https://b.com",
    });

    expect(result?.allowedOrigins).toEqual(["https://a.com", "https://b.com"]);
  });

  it("adds OPENCLAW_SITE_URL if not already in origins", () => {
    const result = buildAllowedOrigins({
      OPENCLAW_SITE_URL: "https://staging.mirascope.com",
    });

    expect(result?.allowedOrigins).toEqual(["https://staging.mirascope.com"]);
  });

  it("deduplicates SITE_URL when already in ALLOWED_ORIGINS", () => {
    const result = buildAllowedOrigins({
      OPENCLAW_ALLOWED_ORIGINS: "https://staging.mirascope.com",
      OPENCLAW_SITE_URL: "https://staging.mirascope.com",
    });

    expect(result?.allowedOrigins).toEqual(["https://staging.mirascope.com"]);
  });

  it("filters empty entries from comma-separated list", () => {
    const result = buildAllowedOrigins({
      OPENCLAW_ALLOWED_ORIGINS: "https://a.com,,, ,https://b.com,",
    });

    expect(result?.allowedOrigins).toEqual(["https://a.com", "https://b.com"]);
  });
});

describe("redactConfig", () => {
  it("redacts provider API keys", () => {
    const config: OpenClawStartupConfig = {
      models: {
        providers: {
          anthropic: {
            apiKey: "sk-secret-123",
            baseUrl: "https://example.com",
          },
        },
      },
    };

    const redacted = redactConfig(config);

    const provider = redacted.models?.providers?.anthropic as Record<
      string,
      unknown
    >;
    expect(provider.apiKey).toBe("(redacted)");
    expect(provider.baseUrl).toBe("https://example.com");
  });

  it("redacts channel tokens", () => {
    const config: OpenClawStartupConfig = {
      channels: {
        discord: { token: "dc-secret", enabled: true },
        telegram: { botToken: "tg-secret", enabled: true },
        slack: { botToken: "slack-bot", appToken: "slack-app", enabled: true },
      },
    };

    const redacted = redactConfig(config);

    const discord = redacted.channels?.discord as Record<string, unknown>;
    const telegram = redacted.channels?.telegram as Record<string, unknown>;
    const slack = redacted.channels?.slack as Record<string, unknown>;

    expect(discord.token).toBe("(redacted)");
    expect(telegram.botToken).toBe("(redacted)");
    expect(slack.botToken).toBe("(redacted)");
    expect(slack.appToken).toBe("(redacted)");
  });

  it("redacts gateway auth token", () => {
    const config: OpenClawStartupConfig = {
      gateway: { auth: { token: "gw-secret" } },
    };

    const redacted = redactConfig(config);
    expect(redacted.gateway?.auth?.token).toBe("(redacted)");
  });

  it("does not mutate original config", () => {
    const config: OpenClawStartupConfig = {
      models: {
        providers: {
          anthropic: { apiKey: "sk-secret" },
        },
      },
    };

    redactConfig(config);

    const provider = config.models?.providers?.anthropic as Record<
      string,
      unknown
    >;
    expect(provider.apiKey).toBe("sk-secret");
  });
});
