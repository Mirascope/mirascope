/**
 * @fileoverview Tests for the Cloudflare HTTP client.
 *
 * Verifies the client correctly:
 * - Constructs authenticated requests
 * - Unwraps the Cloudflare API v4 response envelope
 * - Converts errors to CloudflareApiError
 */

import { Effect, Layer } from "effect";
import { describe, it, expect, vi, beforeEach } from "vitest";

import { CloudflareHttp } from "@/cloudflare/client";
import { CloudflareApiError } from "@/errors";

const TEST_TOKEN = "test-api-token-abc123";

const run = <A, E>(effect: Effect.Effect<A, E, CloudflareHttp>) =>
  Effect.runPromise(
    effect.pipe(Effect.provide(CloudflareHttp.Live(TEST_TOKEN))),
  );

const runFail = <A, E>(effect: Effect.Effect<A, E, CloudflareHttp>) =>
  Effect.runPromise(
    effect.pipe(Effect.flip, Effect.provide(CloudflareHttp.Live(TEST_TOKEN))),
  );

describe("CloudflareHttp", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  describe("Live layer", () => {
    it("creates a valid layer", () => {
      const layer = CloudflareHttp.Live(TEST_TOKEN);
      expect(Layer.isLayer(layer)).toBe(true);
    });
  });

  describe("request", () => {
    it("unwraps successful response envelope", async () => {
      vi.spyOn(globalThis, "fetch").mockResolvedValue(
        new Response(
          JSON.stringify({
            success: true,
            errors: [],
            messages: [],
            result: { id: "bucket-123", name: "test-bucket" },
          }),
        ),
      );

      const result = await run(
        Effect.gen(function* () {
          const client = yield* CloudflareHttp;
          return yield* client.request<{ id: string; name: string }>({
            method: "GET",
            path: "/accounts/abc/r2/buckets/test-bucket",
          });
        }),
      );

      expect(result).toEqual({ id: "bucket-123", name: "test-bucket" });
    });

    it("sends correct authorization header", async () => {
      const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
        new Response(
          JSON.stringify({
            success: true,
            errors: [],
            messages: [],
            result: {},
          }),
        ),
      );

      await run(
        Effect.gen(function* () {
          const client = yield* CloudflareHttp;
          return yield* client.request({
            method: "GET",
            path: "/test",
          });
        }),
      );

      const [url, init] = fetchSpy.mock.calls[0] as [string, RequestInit];
      expect(url).toBe("https://api.cloudflare.com/client/v4/test");
      expect((init.headers as Record<string, string>).Authorization).toBe(
        `Bearer ${TEST_TOKEN}`,
      );
    });

    it("sends JSON body for POST requests", async () => {
      const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
        new Response(
          JSON.stringify({
            success: true,
            errors: [],
            messages: [],
            result: {},
          }),
        ),
      );

      await run(
        Effect.gen(function* () {
          const client = yield* CloudflareHttp;
          return yield* client.request({
            method: "POST",
            path: "/test",
            body: { name: "my-bucket" },
          });
        }),
      );

      const [, init] = fetchSpy.mock.calls[0] as [string, RequestInit];
      expect(init.method).toBe("POST");
      expect(init.body).toBe(JSON.stringify({ name: "my-bucket" }));
    });

    it("fails with CloudflareApiError on API error response", async () => {
      vi.spyOn(globalThis, "fetch").mockResolvedValue(
        new Response(
          JSON.stringify({
            success: false,
            errors: [
              { code: 10006, message: "Bucket not found" },
              { code: 10007, message: "Access denied" },
            ],
            messages: [],
            result: null,
          }),
        ),
      );

      const error = await runFail(
        Effect.gen(function* () {
          const client = yield* CloudflareHttp;
          return yield* client.request({
            method: "GET",
            path: "/test",
          });
        }),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
      const apiError = error as CloudflareApiError;
      expect(apiError.message).toContain("Bucket not found");
      expect(apiError.message).toContain("Access denied");
      expect(apiError.message).toContain("[10006]");
      expect(apiError.message).toContain("[10007]");
    });

    it("fails with CloudflareApiError on network error", async () => {
      vi.spyOn(globalThis, "fetch").mockRejectedValue(
        new Error("Network timeout"),
      );

      const error = await runFail(
        Effect.gen(function* () {
          const client = yield* CloudflareHttp;
          return yield* client.request({
            method: "GET",
            path: "/test",
          });
        }),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
      expect((error as CloudflareApiError).message).toContain("request failed");
    });

    it("fails with CloudflareApiError on invalid JSON response", async () => {
      vi.spyOn(globalThis, "fetch").mockResolvedValue(
        new Response("not json", {
          status: 200,
          headers: { "Content-Type": "text/plain" },
        }),
      );

      const error = await runFail(
        Effect.gen(function* () {
          const client = yield* CloudflareHttp;
          return yield* client.request({
            method: "GET",
            path: "/test",
          });
        }),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
      expect((error as CloudflareApiError).message).toContain(
        "Failed to parse",
      );
    });

    it("does not send body for GET requests", async () => {
      const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
        new Response(
          JSON.stringify({
            success: true,
            errors: [],
            messages: [],
            result: {},
          }),
        ),
      );

      await run(
        Effect.gen(function* () {
          const client = yield* CloudflareHttp;
          return yield* client.request({
            method: "GET",
            path: "/test",
          });
        }),
      );

      const [, init] = fetchSpy.mock.calls[0] as [string, RequestInit];
      expect(init.body).toBeUndefined();
    });

    it("merges custom headers with defaults", async () => {
      const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
        new Response(
          JSON.stringify({
            success: true,
            errors: [],
            messages: [],
            result: {},
          }),
        ),
      );

      await run(
        Effect.gen(function* () {
          const client = yield* CloudflareHttp;
          return yield* client.request({
            method: "POST",
            path: "/test",
            headers: { "cf-r2-jurisdiction": "eu" },
          });
        }),
      );

      const [, init] = fetchSpy.mock.calls[0] as [string, RequestInit];
      const headers = init.headers as Record<string, string>;
      expect(headers["cf-r2-jurisdiction"]).toBe("eu");
      expect(headers.Authorization).toBe(`Bearer ${TEST_TOKEN}`);
    });

    it("handles empty errors array in failure response", async () => {
      vi.spyOn(globalThis, "fetch").mockResolvedValue(
        new Response(
          JSON.stringify({
            success: false,
            errors: [],
            messages: [],
            result: null,
          }),
        ),
      );

      const error = await runFail(
        Effect.gen(function* () {
          const client = yield* CloudflareHttp;
          return yield* client.request({
            method: "GET",
            path: "/test",
          });
        }),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
      expect((error as CloudflareApiError).message).toContain("Unknown error");
    });
  });
});
