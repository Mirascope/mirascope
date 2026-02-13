import type { Sandbox } from "@cloudflare/sandbox";

import { describe, it, expect, vi } from "vitest";

import { findGatewayProcess, buildEnvVars } from "./proxy";
import {
  createMockSandbox,
  createMockProcess,
  createMockConfig,
  createMockEnv,
} from "./test-helpers";

describe("buildEnvVars", () => {
  it("passes through all defined container env vars", () => {
    const config = createMockConfig({
      containerEnv: {
        ANTHROPIC_API_KEY: "sk-test",
        ANTHROPIC_BASE_URL: "https://router.example.com",
        OPENCLAW_GATEWAY_TOKEN: "gw-tok",
        MIRASCOPE_API_KEY: "mk-test",
      },
    });
    const env = createMockEnv();

    const result = buildEnvVars(config, env);
    expect(result).toEqual({
      ANTHROPIC_API_KEY: "sk-test",
      ANTHROPIC_BASE_URL: "https://router.example.com",
      OPENCLAW_GATEWAY_TOKEN: "gw-tok",
      MIRASCOPE_API_KEY: "mk-test",
      CLOUDFLARE_ACCOUNT_ID: "test-account-id",
      OPENCLAW_SITE_URL: "https://mirascope.com",
      OPENCLAW_ALLOWED_ORIGINS: "https://mirascope.com",
      R2_ACCESS_KEY_ID: "test-access-key",
      R2_SECRET_ACCESS_KEY: "test-secret-key",
      R2_BUCKET_NAME: "claw-claw-123",
    });
  });

  it("strips undefined values", () => {
    const config = createMockConfig({
      containerEnv: {
        ANTHROPIC_API_KEY: "sk-test",
        ANTHROPIC_BASE_URL: "https://router.example.com",
        OPENCLAW_GATEWAY_TOKEN: "gw-tok",
        MIRASCOPE_API_KEY: "mk-test",
        TELEGRAM_BOT_TOKEN: undefined,
        DISCORD_BOT_TOKEN: undefined,
      },
    });
    const env = createMockEnv();

    const result = buildEnvVars(config, env);
    expect(result).not.toHaveProperty("TELEGRAM_BOT_TOKEN");
    expect(result).not.toHaveProperty("DISCORD_BOT_TOKEN");
    expect(Object.keys(result)).toHaveLength(10);
  });

  it("includes R2 credentials even with empty containerEnv", () => {
    const config = createMockConfig({ containerEnv: {} });
    const env = createMockEnv();
    const result = buildEnvVars(config, env);
    expect(result).toEqual({
      CLOUDFLARE_ACCOUNT_ID: "test-account-id",
      OPENCLAW_SITE_URL: "https://mirascope.com",
      OPENCLAW_ALLOWED_ORIGINS: "https://mirascope.com",
      R2_ACCESS_KEY_ID: "test-access-key",
      R2_SECRET_ACCESS_KEY: "test-secret-key",
      R2_BUCKET_NAME: "claw-claw-123",
    });
  });

  it("includes CLOUDFLARE_ACCOUNT_ID from dispatch worker env", () => {
    const config = createMockConfig({ containerEnv: {} });
    const env = createMockEnv({ CLOUDFLARE_ACCOUNT_ID: "my-cf-account" });
    const result = buildEnvVars(config, env);
    expect(result).toHaveProperty("CLOUDFLARE_ACCOUNT_ID", "my-cf-account");
  });

  it("omits CLOUDFLARE_ACCOUNT_ID if not set in dispatch worker env", () => {
    const config = createMockConfig({ containerEnv: {} });
    const env = createMockEnv({ CLOUDFLARE_ACCOUNT_ID: undefined });
    const result = buildEnvVars(config, env);
    expect(result).not.toHaveProperty("CLOUDFLARE_ACCOUNT_ID");
  });

  it("includes OPENCLAW_SITE_URL and OPENCLAW_ALLOWED_ORIGINS from SITE_URL", () => {
    const config = createMockConfig({ containerEnv: {} });
    const env = createMockEnv({ SITE_URL: "https://example.com" });
    const result = buildEnvVars(config, env);
    expect(result).toHaveProperty("OPENCLAW_SITE_URL", "https://example.com");
    expect(result).toHaveProperty(
      "OPENCLAW_ALLOWED_ORIGINS",
      "https://example.com",
    );
  });
});

describe("findGatewayProcess", () => {
  it("returns null when no processes exist", async () => {
    const sandbox = createMockSandbox({
      listProcesses: vi.fn().mockResolvedValue([]),
    });
    const result = await findGatewayProcess(sandbox as unknown as Sandbox);
    expect(result).toBeNull();
  });

  it("finds a running gateway process by start-openclaw.ts command", async () => {
    const proc = createMockProcess({
      command: "bun /usr/local/bin/start-openclaw.ts",
      status: "running",
    });
    const sandbox = createMockSandbox({
      listProcesses: vi.fn().mockResolvedValue([proc]),
    });

    const result = await findGatewayProcess(sandbox as unknown as Sandbox);
    expect(result).toBe(proc);
  });

  it("finds a running gateway process by 'openclaw gateway' command", async () => {
    const proc = createMockProcess({
      command: "openclaw gateway --port 18789 --verbose",
      status: "running",
    });
    const sandbox = createMockSandbox({
      listProcesses: vi.fn().mockResolvedValue([proc]),
    });

    const result = await findGatewayProcess(sandbox as unknown as Sandbox);
    expect(result).toBe(proc);
  });

  it("returns starting process as well", async () => {
    const proc = createMockProcess({
      command: "openclaw gateway --port 18789",
      status: "starting",
    });
    const sandbox = createMockSandbox({
      listProcesses: vi.fn().mockResolvedValue([proc]),
    });

    const result = await findGatewayProcess(sandbox as unknown as Sandbox);
    expect(result).toBe(proc);
  });

  it("ignores CLI commands (openclaw devices, openclaw --version)", async () => {
    const procs = [
      createMockProcess({
        command: "openclaw devices list",
        status: "running",
      }),
      createMockProcess({ command: "openclaw --version", status: "running" }),
    ];
    const sandbox = createMockSandbox({
      listProcesses: vi.fn().mockResolvedValue(procs),
    });

    const result = await findGatewayProcess(sandbox as unknown as Sandbox);
    expect(result).toBeNull();
  });

  it("ignores completed/failed processes", async () => {
    const proc = createMockProcess({
      command: "openclaw gateway --port 18789",
      status: "completed",
      exitCode: 0,
    });
    const sandbox = createMockSandbox({
      listProcesses: vi.fn().mockResolvedValue([proc]),
    });

    const result = await findGatewayProcess(sandbox as unknown as Sandbox);
    expect(result).toBeNull();
  });

  it("returns null and logs when listProcesses throws", async () => {
    const sandbox = createMockSandbox({
      listProcesses: vi
        .fn()
        .mockRejectedValue(new Error("sandbox unavailable")),
    });

    const result = await findGatewayProcess(sandbox as unknown as Sandbox);
    expect(result).toBeNull();
  });

  it("picks the first matching gateway among multiple processes", async () => {
    const gateway = createMockProcess({
      id: "gateway-proc",
      command: "openclaw gateway --port 18789",
      status: "running",
    });
    const other = createMockProcess({
      id: "other-proc",
      command: "node some-script.js",
      status: "running",
    });
    const sandbox = createMockSandbox({
      listProcesses: vi.fn().mockResolvedValue([other, gateway]),
    });

    const result = await findGatewayProcess(sandbox as unknown as Sandbox);
    expect(result).toBe(gateway);
  });
});
