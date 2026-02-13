import { describe, expect, it } from "vitest";

import type {
  OpenClawEnv,
  OpenClawConfigOptions,
} from "./create-openclaw-config";

import {
  configureAnthropicProvider,
  configureChannels,
  configureEnvVars,
  configureGateway,
  configureModelDefaults,
  configureWorkspace,
  createOpenClawConfig,
  initializeConfigStructure,
} from "./create-openclaw-config";

function makeEnv(overrides: Partial<OpenClawEnv> = {}): OpenClawEnv {
  return {
    R2_BUCKET_NAME: "test-bucket",
    OPENCLAW_GATEWAY_TOKEN: "gw-token-123",
    OPENCLAW_SITE_URL: "https://site.example.com",
    OPENCLAW_ALLOWED_ORIGINS: "https://a.example.com,https://b.example.com",
    CF_ACCOUNT_ID: "cf-123",
    ANTHROPIC_BASE_URL: "https://api.anthropic.com/",
    ANTHROPIC_API_KEY: "sk-test-key",
    PRIMARY_MODEL_ID: "anthropic/claude-opus-4-6",
    ...overrides,
  };
}

function makeOptions(
  overrides: Partial<OpenClawConfigOptions> = {},
): OpenClawConfigOptions {
  return {
    workspaceDir: "/tmp/workspace",
    gatewayPort: 8080,
    ...overrides,
  };
}

function makeInitializedConfig(): any {
  const config: any = {};
  initializeConfigStructure(config);
  return config;
}

describe("initializeConfigStructure", () => {
  it("creates all nested structures on empty object", () => {
    const config: any = {};
    initializeConfigStructure(config);
    expect(config.agents.defaults.model).toBeDefined();
    expect(config.agents.defaults.models).toBeDefined();
    expect(config.gateway.auth).toBeDefined();
    expect(config.models.providers).toBeDefined();
    expect(config.channels).toBeDefined();
    expect(config.env.vars).toBeDefined();
  });

  it("preserves existing values", () => {
    const config: any = { agents: { defaults: { workspace: "/existing" } } };
    initializeConfigStructure(config);
    expect(config.agents.defaults.workspace).toBe("/existing");
    expect(config.agents.defaults.model).toBeDefined();
  });
});

describe("configureGateway", () => {
  it("sets port, mode, trustedProxies, auth, and allowedOrigins", () => {
    const config = makeInitializedConfig();
    const env = makeEnv();
    configureGateway(config, env, makeOptions({ gatewayPort: 9090 }));

    expect(config.gateway.port).toBe(9090);
    expect(config.gateway.mode).toBe("local");
    expect(config.gateway.trustedProxies).toEqual(["10.1.0.0"]);
    expect(config.gateway.auth.token).toBe("gw-token-123");
    expect(config.gateway.controlUi.allowedOrigins).toContain(
      "https://a.example.com",
    );
    expect(config.gateway.controlUi.allowedOrigins).toContain(
      "https://b.example.com",
    );
  });

  it("adds site URL to allowedOrigins if not already present", () => {
    const config = makeInitializedConfig();
    const env = makeEnv({ OPENCLAW_ALLOWED_ORIGINS: "https://other.com" });
    configureGateway(config, env, makeOptions());

    expect(config.gateway.controlUi.allowedOrigins).toContain(
      "https://site.example.com",
    );
  });

  it("does not duplicate site URL in allowedOrigins", () => {
    const config = makeInitializedConfig();
    const env = makeEnv({
      OPENCLAW_ALLOWED_ORIGINS: "https://site.example.com,https://other.com",
    });
    configureGateway(config, env, makeOptions());

    const origins = config.gateway.controlUi.allowedOrigins;
    expect(
      origins.filter((o: string) => o === "https://site.example.com"),
    ).toHaveLength(1);
  });
});

describe("configureAnthropicProvider", () => {
  it("sets up anthropic provider with model cards", () => {
    const config = makeInitializedConfig();
    configureAnthropicProvider(config, makeEnv());

    const provider = config.models.providers.anthropic;
    expect(provider.baseUrl).toBe("https://api.anthropic.com");
    expect(provider.api).toBe("anthropic-messages");
    expect(provider.apiKey).toBe("sk-test-key");
    expect(provider.models).toHaveLength(4);
  });

  it("strips trailing slashes from base URL", () => {
    const config = makeInitializedConfig();
    configureAnthropicProvider(
      config,
      makeEnv({ ANTHROPIC_BASE_URL: "https://api.example.com///" }),
    );

    expect(config.models.providers.anthropic.baseUrl).toBe(
      "https://api.example.com",
    );
  });
});

describe("configureModelDefaults", () => {
  it("sets model aliases and primary model", () => {
    const config = makeInitializedConfig();
    configureModelDefaults(config, makeEnv());

    expect(
      config.agents.defaults.models["anthropic/claude-opus-4-6"].alias,
    ).toBe("Opus 4.6");
    expect(config.agents.defaults.model.primary).toBe(
      "anthropic/claude-opus-4-6",
    );
  });

  it("throws on invalid PRIMARY_MODEL_ID format", () => {
    const config = makeInitializedConfig();
    expect(() =>
      configureModelDefaults(
        config,
        makeEnv({ PRIMARY_MODEL_ID: "claude-opus-4-6" }),
      ),
    ).toThrow("PRIMARY_MODEL_ID must include a provider prefix");
  });
});

describe("configureChannels", () => {
  it("configures telegram when token present", () => {
    const config = makeInitializedConfig();
    configureChannels(config, makeEnv({ TELEGRAM_BOT_TOKEN: "tg-token" }));

    expect((config.channels.telegram as any).botToken).toBe("tg-token");
    expect((config.channels.telegram as any).enabled).toBe(true);
  });

  it("configures discord when token present", () => {
    const config = makeInitializedConfig();
    configureChannels(config, makeEnv({ DISCORD_BOT_TOKEN: "dc-token" }));

    expect((config.channels.discord as any).token).toBe("dc-token");
    expect((config.channels.discord as any).enabled).toBe(true);
  });

  it("configures slack only when both tokens present", () => {
    const config = makeInitializedConfig();
    configureChannels(
      config,
      makeEnv({ SLACK_BOT_TOKEN: "sl-bot", SLACK_APP_TOKEN: "sl-app" }),
    );

    expect((config.channels.slack as any).botToken).toBe("sl-bot");
    expect((config.channels.slack as any).appToken).toBe("sl-app");
  });

  it("does not configure slack with only bot token", () => {
    const config = makeInitializedConfig();
    configureChannels(config, makeEnv({ SLACK_BOT_TOKEN: "sl-bot" }));

    expect(config.channels.slack).toBeUndefined();
  });

  it("skips all channels when no tokens provided", () => {
    const config = makeInitializedConfig();
    configureChannels(config, makeEnv());

    expect(config.channels.telegram).toBeUndefined();
    expect(config.channels.discord).toBeUndefined();
    expect(config.channels.slack).toBeUndefined();
  });
});

describe("configureWorkspace", () => {
  it("sets workspace directory", () => {
    const config = makeInitializedConfig();
    configureWorkspace(config, makeOptions({ workspaceDir: "/my/dir" }));

    expect(config.agents.defaults.workspace).toBe("/my/dir");
  });
});

describe("configureEnvVars", () => {
  it("sets gateway token in env vars", () => {
    const config = makeInitializedConfig();
    configureEnvVars(config, makeEnv());

    expect(config.env.vars.OPENCLAW_GATEWAY_TOKEN).toBe("gw-token-123");
  });
});

describe("createOpenClawConfig", () => {
  it("returns a complete config with all sections", () => {
    const env = makeEnv({
      DISCORD_BOT_TOKEN: "dc-token",
      TELEGRAM_BOT_TOKEN: "tg-token",
    });
    const config = createOpenClawConfig(env, makeOptions());

    expect(config.gateway!.port).toBe(8080);
    expect(config.models!.providers!.anthropic).toBeDefined();
    expect(config.agents!.defaults!.model!.primary).toBe(
      "anthropic/claude-opus-4-6",
    );
    expect(config.agents!.defaults!.workspace).toBe("/tmp/workspace");
    expect((config.channels!.discord as any).token).toBe("dc-token");
    expect((config.channels!.telegram as any).botToken).toBe("tg-token");
    expect(config.env!.vars!.OPENCLAW_GATEWAY_TOKEN).toBe("gw-token-123");
  });

  it("uses existing config as base", () => {
    const existing: any = { custom: "value" };
    const config = createOpenClawConfig(
      makeEnv(),
      makeOptions({ existingConfig: existing }),
    );

    expect((config as any).custom).toBe("value");
    expect(config.gateway!.port).toBe(8080);
  });

  it("throws on invalid PRIMARY_MODEL_ID", () => {
    expect(() =>
      createOpenClawConfig(
        makeEnv({ PRIMARY_MODEL_ID: "no-slash" }),
        makeOptions(),
      ),
    ).toThrow("PRIMARY_MODEL_ID must include a provider prefix");
  });
});
