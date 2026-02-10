import { describe, expect, it } from "@effect/vitest";
import { Effect } from "effect";
import assert from "node:assert";
import { afterEach, beforeEach, vi } from "vitest";

import type { DispatchEnv } from "./types";

import {
  BootstrapDecodeError,
  BootstrapFetchError,
  type ClawResolutionError,
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
    Sandbox: {} as unknown as DispatchEnv["Sandbox"],
    MIRASCOPE_CLOUD: binding as unknown as DispatchEnv["MIRASCOPE_CLOUD"],
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
  it.effect("fetches config via service binding with correct URL", () =>
    Effect.gen(function* () {
      const config = createMockConfig();
      const env = makeEnv();
      binding.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(config),
      });

      const result = yield* fetchBootstrapConfig("claw-123", env);

      expect(binding.fetch).toHaveBeenCalledOnce();
      const [url, opts] = binding.fetch.mock.calls[0];
      expect(url).toBe(
        "https://internal/api/internal/claws/claw-123/bootstrap",
      );
      expect(opts.method).toBe("GET");
      expect(result).toEqual(config);
    }),
  );

  it.effect("does not send bearer token", () =>
    Effect.gen(function* () {
      const config = createMockConfig();
      const env = makeEnv();
      binding.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(config),
      });

      yield* fetchBootstrapConfig("claw-123", env);

      const [, opts] = binding.fetch.mock.calls[0];
      const headers = new Headers(opts.headers);
      expect(headers.get("Authorization")).toBeNull();
    }),
  );

  it.effect("fails with BootstrapFetchError on non-OK response", () =>
    Effect.gen(function* () {
      const env = makeEnv();
      binding.fetch.mockResolvedValue({
        ok: false,
        status: 404,
        statusText: "Not Found",
        text: () => Promise.resolve("claw not found"),
      });

      const result = yield* fetchBootstrapConfig("claw-123", env).pipe(
        Effect.flip,
      );
      assert(result instanceof BootstrapFetchError);
      expect(result.message).toContain("404");
      expect(result.message).toContain("claw not found");
    }),
  );

  it.effect("fails with BootstrapDecodeError when json() fails", () =>
    Effect.gen(function* () {
      const env = makeEnv();
      binding.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.reject(new Error("invalid json")),
      });

      const result = yield* fetchBootstrapConfig("claw-123", env).pipe(
        Effect.flip,
      );
      assert(result instanceof BootstrapDecodeError);
    }),
  );
});

// =========================================================================
// resolveClawId
// =========================================================================

describe("resolveClawId", () => {
  it.effect("resolves slugs to clawId via correct URL", () =>
    Effect.gen(function* () {
      const payload = { clawId: "claw-123", organizationId: "org-456" };
      const env = makeEnv();
      binding.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(payload),
      });

      const result = yield* resolveClawId("test-org", "test-claw", env);

      expect(binding.fetch).toHaveBeenCalledOnce();
      const [url] = binding.fetch.mock.calls[0];
      expect(url).toBe(
        "https://internal/api/internal/claws/resolve/test-org/test-claw",
      );
      expect(result).toEqual(payload);
    }),
  );

  it.effect("fails with ClawResolutionError on non-OK response", () =>
    Effect.gen(function* () {
      const env = makeEnv();
      binding.fetch.mockResolvedValue({
        ok: false,
        status: 404,
        statusText: "Not Found",
        text: () => Promise.resolve("not found"),
      });

      const result = yield* resolveClawId("test-org", "test-claw", env).pipe(
        Effect.flip,
      );
      expect(result._tag).toBe("ClawResolutionError");
      const err = result as ClawResolutionError;
      expect(err.orgSlug).toBe("test-org");
      expect(err.clawSlug).toBe("test-claw");
      expect(err.statusCode).toBe(404);
    }),
  );
});

// =========================================================================
// reportClawStatus
// =========================================================================

describe("reportClawStatus", () => {
  it.effect("posts status to correct URL", () =>
    Effect.gen(function* () {
      const env = makeEnv();
      binding.fetch.mockResolvedValue({ ok: true });

      yield* reportClawStatus(
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
    }),
  );

  it.effect("does not throw on non-OK response", () =>
    Effect.gen(function* () {
      const env = makeEnv();
      binding.fetch.mockResolvedValue({
        ok: false,
        status: 500,
        statusText: "Internal Server Error",
      });

      const result = yield* reportClawStatus(
        "claw-123",
        { status: "error", errorMessage: "boom" },
        env,
      );
      expect(result).toBeUndefined();
    }),
  );

  it.effect("does not throw on fetch error", () =>
    Effect.gen(function* () {
      const env = makeEnv();
      binding.fetch.mockRejectedValue(new Error("binding error"));

      const result = yield* reportClawStatus(
        "claw-123",
        { status: "error" },
        env,
      );
      expect(result).toBeUndefined();
    }),
  );

  it.effect("reports error status with errorMessage", () =>
    Effect.gen(function* () {
      const env = makeEnv();
      binding.fetch.mockResolvedValue({ ok: true });

      yield* reportClawStatus(
        "claw-123",
        { status: "error", errorMessage: "Gateway crashed" },
        env,
      );

      const [, opts] = binding.fetch.mock.calls[0];
      expect(JSON.parse(opts.body)).toEqual({
        status: "error",
        errorMessage: "Gateway crashed",
      });
    }),
  );
});
