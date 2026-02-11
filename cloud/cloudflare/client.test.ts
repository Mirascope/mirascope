/**
 * @fileoverview Tests for the Cloudflare HTTP client.
 *
 * Verifies the client correctly:
 * - Constructs authenticated requests
 * - Unwraps the Cloudflare API v4 response envelope
 * - Converts errors to CloudflareApiError
 */

import { describe, it, expect } from "@effect/vitest";
import { Effect, Layer } from "effect";
import { vi, beforeEach } from "vitest";

import { CloudflareHttp } from "@/cloudflare/client";
import { CloudflareApiError } from "@/errors";

const TEST_TOKEN = "test-api-token-abc123";

const TestLayer = CloudflareHttp.Live(TEST_TOKEN);

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
    it.effect("unwraps successful response envelope", () => {
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

      return Effect.gen(function* () {
        const client = yield* CloudflareHttp;
        const result = yield* client.request<{ id: string; name: string }>({
          method: "GET",
          path: "/accounts/abc/r2/buckets/test-bucket",
        });

        expect(result).toEqual({ id: "bucket-123", name: "test-bucket" });
      }).pipe(Effect.provide(TestLayer));
    });

    it.effect("sends correct authorization header", () => {
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

      return Effect.gen(function* () {
        const client = yield* CloudflareHttp;
        yield* client.request({
          method: "GET",
          path: "/test",
        });

        const [url, init] = fetchSpy.mock.calls[0] as [string, RequestInit];
        expect(url).toBe("https://api.cloudflare.com/client/v4/test");
        expect((init.headers as Record<string, string>).Authorization).toBe(
          `Bearer ${TEST_TOKEN}`,
        );
      }).pipe(Effect.provide(TestLayer));
    });

    it.effect("sends JSON body for POST requests", () => {
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

      return Effect.gen(function* () {
        const client = yield* CloudflareHttp;
        yield* client.request({
          method: "POST",
          path: "/test",
          body: { name: "my-bucket" },
        });

        const [, init] = fetchSpy.mock.calls[0] as [string, RequestInit];
        expect(init.method).toBe("POST");
        expect(init.body).toBe(JSON.stringify({ name: "my-bucket" }));
      }).pipe(Effect.provide(TestLayer));
    });

    it.effect("fails with CloudflareApiError on API error response", () => {
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

      return Effect.gen(function* () {
        const client = yield* CloudflareHttp;
        const error = yield* client
          .request({
            method: "GET",
            path: "/test",
          })
          .pipe(Effect.flip);

        expect(error).toBeInstanceOf(CloudflareApiError);
        const apiError = error as CloudflareApiError;
        expect(apiError.message).toContain("Bucket not found");
        expect(apiError.message).toContain("Access denied");
        expect(apiError.message).toContain("[10006]");
        expect(apiError.message).toContain("[10007]");
      }).pipe(Effect.provide(TestLayer));
    });

    it.effect("fails with CloudflareApiError on network error", () => {
      vi.spyOn(globalThis, "fetch").mockRejectedValue(
        new Error("Network timeout"),
      );

      return Effect.gen(function* () {
        const client = yield* CloudflareHttp;
        const error = yield* client
          .request({
            method: "GET",
            path: "/test",
          })
          .pipe(Effect.flip);

        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain(
          "request failed",
        );
      }).pipe(Effect.provide(TestLayer));
    });

    it.effect("fails with CloudflareApiError on invalid JSON response", () => {
      vi.spyOn(globalThis, "fetch").mockResolvedValue(
        new Response("not json", {
          status: 200,
          headers: { "Content-Type": "text/plain" },
        }),
      );

      return Effect.gen(function* () {
        const client = yield* CloudflareHttp;
        const error = yield* client
          .request({
            method: "GET",
            path: "/test",
          })
          .pipe(Effect.flip);

        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain(
          "Failed to parse",
        );
      }).pipe(Effect.provide(TestLayer));
    });

    it.effect("does not send body for GET requests", () => {
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

      return Effect.gen(function* () {
        const client = yield* CloudflareHttp;
        yield* client.request({
          method: "GET",
          path: "/test",
        });

        const [, init] = fetchSpy.mock.calls[0] as [string, RequestInit];
        expect(init.body).toBeUndefined();
      }).pipe(Effect.provide(TestLayer));
    });

    it.effect("merges custom headers with defaults", () => {
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

      return Effect.gen(function* () {
        const client = yield* CloudflareHttp;
        yield* client.request({
          method: "POST",
          path: "/test",
          headers: { "cf-r2-jurisdiction": "eu" },
        });

        const [, init] = fetchSpy.mock.calls[0] as [string, RequestInit];
        const headers = init.headers as Record<string, string>;
        expect(headers["cf-r2-jurisdiction"]).toBe("eu");
        expect(headers.Authorization).toBe(`Bearer ${TEST_TOKEN}`);
      }).pipe(Effect.provide(TestLayer));
    });

    it.effect("handles empty errors array in failure response", () => {
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

      return Effect.gen(function* () {
        const client = yield* CloudflareHttp;
        const error = yield* client
          .request({
            method: "GET",
            path: "/test",
          })
          .pipe(Effect.flip);

        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain(
          "Unknown error",
        );
      }).pipe(Effect.provide(TestLayer));
    });
  });
});
