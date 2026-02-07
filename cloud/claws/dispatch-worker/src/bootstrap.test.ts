import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

import type { DispatchEnv } from "./types";

import {
  fetchBootstrapConfig,
  resolveClawId,
  reportClawStatus,
} from "./bootstrap";
import { createMockConfig } from "./test-helpers";

/** Mock service binding — just an object with a vi.fn() `fetch` method. */
type MockBinding = { fetch: ReturnType<typeof vi.fn> };

function createMockBinding(): MockBinding {
  return { fetch: vi.fn() };
}

/** The binding used by the current test — set fresh in makeEnv(). */
let binding: MockBinding;

function makeEnv(overrides: Partial<DispatchEnv> = {}): DispatchEnv {
  binding = createMockBinding();
  return {
    Sandbox: {} as any,
    MIRASCOPE_CLOUD: binding as any,
    CF_ACCOUNT_ID: "test-account",
    ...overrides,
  };
}

beforeEach(() => {
  vi.clearAllMocks();
});

afterEach(() => {
  vi.restoreAllMocks();
});

// =========================================================================
// fetchBootstrapConfig
// =========================================================================

describe("fetchBootstrapConfig", () => {
  it("fetches config via service binding with correct URL", async () => {
    const config = createMockConfig();
    const env = makeEnv();
    binding.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(config),
    });

    const result = await fetchBootstrapConfig("claw-123", env);

    expect(binding.fetch).toHaveBeenCalledOnce();
    const [url, opts] = binding.fetch.mock.calls[0];
    expect(url).toBe("https://internal/api/internal/claws/claw-123/bootstrap");
    expect(opts.method).toBe("GET");
    expect(result).toEqual(config);
  });

  it("does not send bearer token", async () => {
    const config = createMockConfig();
    const env = makeEnv();
    binding.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(config),
    });

    await fetchBootstrapConfig("claw-123", env);

    const [, opts] = binding.fetch.mock.calls[0];
    const headers = new Headers(opts.headers);
    expect(headers.get("Authorization")).toBeNull();
  });

  it("throws on non-OK response with status and body", async () => {
    const env = makeEnv();
    binding.fetch.mockResolvedValue({
      ok: false,
      status: 404,
      statusText: "Not Found",
      text: () => Promise.resolve("claw not found"),
    });

    await expect(fetchBootstrapConfig("claw-123", env)).rejects.toThrow(
      "Bootstrap config fetch failed for claw claw-123: 404 Not Found — claw not found",
    );
  });
});

// =========================================================================
// resolveClawId
// =========================================================================

describe("resolveClawId", () => {
  it("resolves slugs to clawId via correct URL", async () => {
    const payload = { clawId: "claw-123", organizationId: "org-456" };
    const env = makeEnv();
    binding.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(payload),
    });

    const result = await resolveClawId("test-org", "test-claw", env);

    expect(binding.fetch).toHaveBeenCalledOnce();
    const [url] = binding.fetch.mock.calls[0];
    expect(url).toBe(
      "https://internal/api/internal/claws/resolve/test-org/test-claw",
    );
    expect(result).toEqual(payload);
  });

  it("throws on non-OK response", async () => {
    const env = makeEnv();
    binding.fetch.mockResolvedValue({
      ok: false,
      status: 404,
      statusText: "Not Found",
      text: () => Promise.resolve("not found"),
    });

    await expect(resolveClawId("test-org", "test-claw", env)).rejects.toThrow(
      "Claw resolution failed for test-claw.test-org: 404 Not Found",
    );
  });
});

// =========================================================================
// reportClawStatus
// =========================================================================

describe("reportClawStatus", () => {
  it("posts status to correct URL", async () => {
    const env = makeEnv();
    binding.fetch.mockResolvedValue({ ok: true });

    await reportClawStatus(
      "claw-123",
      { status: "active", startedAt: "2025-01-01T00:00:00Z" },
      env,
    );

    expect(binding.fetch).toHaveBeenCalledOnce();
    const [url, opts] = binding.fetch.mock.calls[0];
    expect(url).toBe("https://internal/api/internal/claws/claw-123/status");
    expect(opts.method).toBe("POST");
    expect(JSON.parse(opts.body)).toEqual({
      status: "active",
      startedAt: "2025-01-01T00:00:00Z",
    });
  });

  it("does not throw on non-OK response", async () => {
    const env = makeEnv();
    binding.fetch.mockResolvedValue({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
    });

    await expect(
      reportClawStatus(
        "claw-123",
        { status: "error", errorMessage: "boom" },
        env,
      ),
    ).resolves.toBeUndefined();
  });

  it("does not throw on fetch error", async () => {
    const env = makeEnv();
    binding.fetch.mockRejectedValue(new Error("binding error"));

    await expect(
      reportClawStatus("claw-123", { status: "error" }, env),
    ).resolves.toBeUndefined();
  });

  it("reports error status with errorMessage", async () => {
    const env = makeEnv();
    binding.fetch.mockResolvedValue({ ok: true });

    await reportClawStatus(
      "claw-123",
      { status: "error", errorMessage: "Gateway crashed" },
      env,
    );

    const [, opts] = binding.fetch.mock.calls[0];
    expect(JSON.parse(opts.body)).toEqual({
      status: "error",
      errorMessage: "Gateway crashed",
    });
  });
});
