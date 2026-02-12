import type { Sandbox, Process } from "@cloudflare/sandbox";

import { Effect } from "effect";
import { Hono } from "hono";
import { describe, it, expect, vi, beforeEach } from "vitest";

import type { AppEnv } from "./types";

import {
  createMockSandbox,
  createMockProcess,
  createMockConfig,
} from "./test-helpers";

// We test the internal routes by importing the sub-router and mounting it on
// a test Hono app that pre-populates the sandbox and clawId context vars
// (simulating what the main middleware does).

let mockSandbox = createMockSandbox();

// Mock the proxy module so findGatewayProcess uses our mock sandbox
vi.mock("./proxy", () => ({
  ensureGateway: vi.fn(),
  findGatewayProcess: vi.fn(),
}));

vi.mock("./bootstrap", () => ({
  fetchBootstrapConfig: vi.fn(),
  reportClawStatus: vi.fn(),
}));

vi.mock("./cache", () => ({
  getCachedConfig: vi.fn(),
  setCachedConfig: vi.fn(),
}));

import { fetchBootstrapConfig, reportClawStatus } from "./bootstrap";
import { getCachedConfig, setCachedConfig } from "./cache";
import { internal } from "./internal";
import { ensureGateway, findGatewayProcess } from "./proxy";

const mockFindGateway = vi.mocked(findGatewayProcess);
const mockEnsureGateway = vi.mocked(ensureGateway);
const mockFetchBootstrapConfig = vi.mocked(fetchBootstrapConfig);
const mockReportClawStatus = vi.mocked(reportClawStatus);
const mockGetCachedConfig = vi.mocked(getCachedConfig);
const mockSetCachedConfig = vi.mocked(setCachedConfig);

function createTestApp() {
  const app = new Hono<AppEnv>();
  // Simulate the main middleware that sets sandbox + clawId + env
  app.use("*", async (c, next) => {
    c.set("sandbox", mockSandbox as unknown as Sandbox);
    c.set("clawId", "test-claw-id");
    await next();
  });
  app.route("/_internal", internal);
  return app;
}

beforeEach(() => {
  mockSandbox = createMockSandbox();
  mockFindGateway.mockReset();
  mockEnsureGateway.mockReset();
  mockFetchBootstrapConfig.mockReset();
  mockReportClawStatus.mockReset();
  mockReportClawStatus.mockReturnValue(
    Effect.void as unknown as ReturnType<typeof reportClawStatus>,
  );
  mockGetCachedConfig.mockReset();
  mockSetCachedConfig.mockReset();
});

describe("POST /_internal/recreate", () => {
  it("kills gateway process and destroys container", async () => {
    const proc = createMockProcess();
    mockFindGateway.mockResolvedValue(proc as unknown as Process);

    const app = createTestApp();
    const res = await app.request("/_internal/recreate", { method: "POST" });
    const body = (await res.json()) as Record<string, unknown>;

    expect(res.status).toBe(200);
    expect(body).toEqual({ ok: true });
    expect(proc.kill).toHaveBeenCalledOnce();
    expect(mockSandbox.destroy).toHaveBeenCalledOnce();
  });

  it("destroys container even if no gateway process found", async () => {
    mockFindGateway.mockResolvedValue(null);

    const app = createTestApp();
    const res = await app.request("/_internal/recreate", { method: "POST" });
    const body = (await res.json()) as Record<string, unknown>;

    expect(res.status).toBe(200);
    expect(body).toEqual({ ok: true });
    expect(mockSandbox.destroy).toHaveBeenCalledOnce();
  });

  it("returns 500 if destroy fails", async () => {
    mockFindGateway.mockResolvedValue(null);
    mockSandbox.destroy.mockRejectedValue(new Error("destroy failed"));

    const app = createTestApp();
    const res = await app.request("/_internal/recreate", { method: "POST" });
    const body = (await res.json()) as Record<string, unknown>;

    expect(res.status).toBe(500);
    expect(body.ok).toBe(false);
    expect(body.error).toBe("destroy failed");
  });

  it("still destroys container even if kill fails", async () => {
    const proc = createMockProcess();
    proc.kill.mockRejectedValue(new Error("kill failed"));
    mockFindGateway.mockResolvedValue(proc as unknown as Process);

    const app = createTestApp();
    const res = await app.request("/_internal/recreate", { method: "POST" });
    const body = (await res.json()) as Record<string, unknown>;

    expect(res.status).toBe(200);
    expect(body).toEqual({ ok: true });
    expect(mockSandbox.destroy).toHaveBeenCalledOnce();
  });
});

describe("POST /_internal/restart-gateway", () => {
  it("kills the gateway process", async () => {
    const proc = createMockProcess();
    mockFindGateway.mockResolvedValue(proc as unknown as Process);

    const app = createTestApp();
    const res = await app.request("/_internal/restart-gateway", {
      method: "POST",
    });
    const body = (await res.json()) as Record<string, unknown>;

    expect(res.status).toBe(200);
    expect(body).toEqual({ ok: true });
    expect(proc.kill).toHaveBeenCalledOnce();
  });

  it("returns ok when no process exists", async () => {
    mockFindGateway.mockResolvedValue(null);

    const app = createTestApp();
    const res = await app.request("/_internal/restart-gateway", {
      method: "POST",
    });
    const body = (await res.json()) as Record<string, unknown>;

    expect(res.status).toBe(200);
    expect(body).toEqual({ ok: true });
  });

  it("returns 500 if kill fails", async () => {
    const proc = createMockProcess();
    proc.kill.mockRejectedValue(new Error("kill failed"));
    mockFindGateway.mockResolvedValue(proc as unknown as Process);

    const app = createTestApp();
    const res = await app.request("/_internal/restart-gateway", {
      method: "POST",
    });
    const body = (await res.json()) as Record<string, unknown>;

    expect(res.status).toBe(500);
    expect(body.ok).toBe(false);
    expect(body.error).toBe("kill failed");
  });
});

describe("POST /_internal/destroy", () => {
  it("destroys the container", async () => {
    const app = createTestApp();
    const res = await app.request("/_internal/destroy", { method: "POST" });
    const body = (await res.json()) as Record<string, unknown>;

    expect(res.status).toBe(200);
    expect(body).toEqual({ ok: true });
    expect(mockSandbox.destroy).toHaveBeenCalledOnce();
  });

  it("returns 500 if destroy fails", async () => {
    mockSandbox.destroy.mockRejectedValue(new Error("nope"));

    const app = createTestApp();
    const res = await app.request("/_internal/destroy", { method: "POST" });
    const body = (await res.json()) as Record<string, unknown>;

    expect(res.status).toBe(500);
    expect(body.ok).toBe(false);
    expect(body.error).toBe("nope");
  });
});

describe("GET /_internal/state", () => {
  it("returns running state when gateway is running", async () => {
    const proc = createMockProcess({ status: "running" });
    mockFindGateway.mockResolvedValue(proc as unknown as Process);

    const app = createTestApp();
    const res = await app.request("/_internal/state");
    const body = (await res.json()) as Record<string, unknown>;

    expect(res.status).toBe(200);
    expect(body.status).toBe("running");
    expect(body.lastChange).toBeTypeOf("number");
  });

  it("returns running state when gateway is starting", async () => {
    const proc = createMockProcess({ status: "starting" });
    mockFindGateway.mockResolvedValue(proc as unknown as Process);

    const app = createTestApp();
    const res = await app.request("/_internal/state");
    const body = (await res.json()) as Record<string, unknown>;

    expect(body.status).toBe("running");
  });

  it("returns stopped with exit code when process completed", async () => {
    const proc = createMockProcess({ status: "completed", exitCode: 1 });
    mockFindGateway.mockResolvedValue(proc as unknown as Process);

    const app = createTestApp();
    const res = await app.request("/_internal/state");
    const body = (await res.json()) as Record<string, unknown>;

    expect(body.status).toBe("stopped");
    expect(body.exitCode).toBe(1);
  });

  it("returns stopped when no process found", async () => {
    mockFindGateway.mockResolvedValue(null);

    const app = createTestApp();
    const res = await app.request("/_internal/state");
    const body = (await res.json()) as Record<string, unknown>;

    expect(body.status).toBe("stopped");
    expect(body.exitCode).toBeUndefined();
  });
});

describe("POST /_internal/warm-up", () => {
  it("uses cached config and calls ensureGateway", async () => {
    const config = createMockConfig();
    mockGetCachedConfig.mockReturnValue(config);
    mockEnsureGateway.mockResolvedValue(undefined);

    const app = createTestApp();
    const res = await app.request("/_internal/warm-up", { method: "POST" });
    const body = (await res.json()) as Record<string, unknown>;

    expect(res.status).toBe(200);
    expect(body).toEqual({ ok: true });
    expect(mockGetCachedConfig).toHaveBeenCalledWith("test-claw-id");
    expect(mockEnsureGateway).toHaveBeenCalledOnce();
    expect(mockFetchBootstrapConfig).not.toHaveBeenCalled();
  });

  it("fetches config when not cached", async () => {
    const config = createMockConfig();
    mockGetCachedConfig.mockReturnValue(null);
    mockFetchBootstrapConfig.mockReturnValue(
      Effect.succeed(config) as unknown as ReturnType<
        typeof fetchBootstrapConfig
      >,
    );
    mockEnsureGateway.mockResolvedValue(undefined);

    const app = createTestApp();
    const res = await app.request("/_internal/warm-up", { method: "POST" });
    const body = (await res.json()) as Record<string, unknown>;

    expect(res.status).toBe(200);
    expect(body).toEqual({ ok: true });
    expect(mockSetCachedConfig).toHaveBeenCalledWith("test-claw-id", config);
  });

  it("returns 500 if ensureGateway fails", async () => {
    const config = createMockConfig();
    mockGetCachedConfig.mockReturnValue(config);
    mockEnsureGateway.mockRejectedValue(new Error("gateway start failed"));

    const app = createTestApp();
    const res = await app.request("/_internal/warm-up", { method: "POST" });
    const body = (await res.json()) as Record<string, unknown>;

    expect(res.status).toBe(500);
    expect(body.ok).toBe(false);
    expect(body.error).toBe("gateway start failed");
  });

  it("reports active status after successful warm-up", async () => {
    const config = createMockConfig();
    mockGetCachedConfig.mockReturnValue(config);
    mockEnsureGateway.mockResolvedValue(undefined);

    const app = createTestApp();
    await app.request("/_internal/warm-up", { method: "POST" });

    expect(mockReportClawStatus).toHaveBeenCalledWith(
      "test-claw-id",
      expect.objectContaining({
        status: "active",
        startedAt: expect.any(String),
      }),
      undefined,
    );
  });

  it("reports error status when warm-up fails", async () => {
    const config = createMockConfig();
    mockGetCachedConfig.mockReturnValue(config);
    mockEnsureGateway.mockRejectedValue(new Error("gateway start failed"));

    const app = createTestApp();
    await app.request("/_internal/warm-up", { method: "POST" });

    expect(mockReportClawStatus).toHaveBeenCalledWith(
      "test-claw-id",
      expect.objectContaining({
        status: "error",
        errorMessage: "gateway start failed",
      }),
      undefined,
    );
  });
});
