import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

import type { DispatchEnv } from "./types";

import {
  fetchBootstrapConfig,
  resolveClawId,
  reportClawStatus,
} from "./bootstrap";
import { createMockConfig } from "./test-helpers";

// Mock global fetch
const mockFetch = vi.fn();
vi.stubGlobal("fetch", mockFetch);

function makeEnv(overrides: Partial<DispatchEnv> = {}): DispatchEnv {
  return {
    Sandbox: {} as any,
    MIRASCOPE_API_BASE_URL: "https://api.mirascope.com",
    MIRASCOPE_API_BEARER_TOKEN: "test-token",
    CF_ACCOUNT_ID: "test-account",
    ...overrides,
  };
}

beforeEach(() => {
  mockFetch.mockReset();
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("fetchBootstrapConfig", () => {
  it("fetches config from correct URL with auth header", async () => {
    const config = createMockConfig();
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(config),
    });

    const result = await fetchBootstrapConfig("claw-123", makeEnv());

    expect(mockFetch).toHaveBeenCalledOnce();
    const [url, opts] = mockFetch.mock.calls[0];
    expect(url).toBe(
      "https://api.mirascope.com/api/internal/claws/claw-123/bootstrap",
    );
    expect(opts.method).toBe("GET");
    expect(opts.headers.Authorization).toBe("Bearer test-token");
    expect(result).toEqual(config);
  });

  it("throws when MIRASCOPE_API_BASE_URL is not set", async () => {
    await expect(
      fetchBootstrapConfig(
        "claw-123",
        makeEnv({ MIRASCOPE_API_BASE_URL: undefined }),
      ),
    ).rejects.toThrow("MIRASCOPE_API_BASE_URL is not set");
  });

  it("throws on non-OK response with status and body", async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 404,
      statusText: "Not Found",
      text: () => Promise.resolve("claw not found"),
    });

    await expect(fetchBootstrapConfig("claw-123", makeEnv())).rejects.toThrow(
      "Bootstrap config fetch failed for claw claw-123: 404 Not Found — claw not found",
    );
  });

  it("omits auth header when token is not set", async () => {
    const config = createMockConfig();
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(config),
    });

    await fetchBootstrapConfig(
      "claw-123",
      makeEnv({ MIRASCOPE_API_BEARER_TOKEN: undefined }),
    );

    const [, opts] = mockFetch.mock.calls[0];
    expect(opts.headers.Authorization).toBeUndefined();
  });
});

describe("resolveClawId", () => {
  it("resolves slugs to clawId via correct URL", async () => {
    const payload = { clawId: "claw-123", organizationId: "org-456" };
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(payload),
    });

    const result = await resolveClawId("test-org", "test-claw", makeEnv());

    expect(mockFetch).toHaveBeenCalledOnce();
    const [url] = mockFetch.mock.calls[0];
    expect(url).toBe(
      "https://api.mirascope.com/api/internal/claws/resolve/test-org/test-claw",
    );
    expect(result).toEqual(payload);
  });

  it("throws when MIRASCOPE_API_BASE_URL is not set", async () => {
    await expect(
      resolveClawId(
        "org",
        "claw",
        makeEnv({ MIRASCOPE_API_BASE_URL: undefined }),
      ),
    ).rejects.toThrow("MIRASCOPE_API_BASE_URL is not set");
  });

  it("throws on non-OK response", async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 404,
      statusText: "Not Found",
      text: () => Promise.resolve("not found"),
    });

    await expect(
      resolveClawId("test-org", "test-claw", makeEnv()),
    ).rejects.toThrow(
      "Claw resolution failed for test-claw.test-org: 404 Not Found",
    );
  });
});

describe("reportClawStatus", () => {
  it("posts status to correct URL", async () => {
    mockFetch.mockResolvedValue({ ok: true });

    await reportClawStatus(
      "claw-123",
      { status: "active", startedAt: "2025-01-01T00:00:00Z" },
      makeEnv(),
    );

    expect(mockFetch).toHaveBeenCalledOnce();
    const [url, opts] = mockFetch.mock.calls[0];
    expect(url).toBe(
      "https://api.mirascope.com/api/internal/claws/claw-123/status",
    );
    expect(opts.method).toBe("POST");
    expect(JSON.parse(opts.body)).toEqual({
      status: "active",
      startedAt: "2025-01-01T00:00:00Z",
    });
  });

  it("silently returns when MIRASCOPE_API_BASE_URL is not set", async () => {
    // reportClawStatus logs an error but doesn't throw
    await expect(
      reportClawStatus(
        "claw-123",
        { status: "active" },
        makeEnv({ MIRASCOPE_API_BASE_URL: undefined }),
      ),
    ).resolves.toBeUndefined();

    expect(mockFetch).not.toHaveBeenCalled();
  });

  it("does not throw on non-OK response", async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
    });

    // Should not throw
    await expect(
      reportClawStatus(
        "claw-123",
        { status: "error", errorMessage: "boom" },
        makeEnv(),
      ),
    ).resolves.toBeUndefined();
  });

  it("does not throw on fetch error", async () => {
    mockFetch.mockRejectedValue(new Error("network error"));

    await expect(
      reportClawStatus("claw-123", { status: "error" }, makeEnv()),
    ).resolves.toBeUndefined();
  });

  it("reports error status with errorMessage", async () => {
    mockFetch.mockResolvedValue({ ok: true });

    await reportClawStatus(
      "claw-123",
      { status: "error", errorMessage: "Gateway crashed" },
      makeEnv(),
    );

    const [, opts] = mockFetch.mock.calls[0];
    expect(JSON.parse(opts.body)).toEqual({
      status: "error",
      errorMessage: "Gateway crashed",
    });
  });
});
