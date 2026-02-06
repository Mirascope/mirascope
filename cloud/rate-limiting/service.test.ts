/**
 * @fileoverview Tests for the RateLimiter service.
 */

import { Effect, Layer } from "effect";

import { RateLimitError, ServiceUnavailableError } from "@/errors";
import { Payments } from "@/payments";
import { RateLimiter } from "@/rate-limiting/service";
import { TestDrizzleORM } from "@/tests/db";
import { describe, it, expect, assert } from "@/tests/payments";
import { MockRateLimiter } from "@/tests/rate-limiting";

describe("RateLimiter", () => {
  const TEST_ORG_ID = "550e8400-e29b-41d4-a716-446655440000";
  const TEST_ORG_ID_2 = "660e8400-e29b-41d4-a716-446655440001";

  /**
   * Helper to create a mock Payments layer that doesn't require database lookups.
   * Returns free plan for TEST_ORG_ID, can be overridden for specific tests.
   */
  function createMockPaymentsLayer(planTier: "free" | "pro" | "team" = "free") {
    return Layer.succeed(Payments, {
      customers: {
        subscriptions: {
          getPlan: () => Effect.succeed(planTier),
          getPlanLimits: (tier: "free" | "pro" | "team") =>
            Effect.succeed({
              seats: tier === "free" ? 1 : tier === "pro" ? 5 : Infinity,
              projects: tier === "free" ? 1 : tier === "pro" ? 5 : Infinity,
              spansPerMonth: tier === "free" ? 1_000_000 : Infinity,
              apiRequestsPerMinute:
                tier === "free" ? 100 : tier === "pro" ? 1000 : 10000,
              dataRetentionDays:
                tier === "free" ? 30 : tier === "pro" ? 90 : 180,
            }),
        },
      } as never,
      products: {} as never,
      paymentIntents: {} as never,
      paymentMethods: {} as never,
    });
  }

  /**
   * Helper to create a test layer with MockRateLimiters and Payments
   */
  function createTestLayer(planTier: "free" | "pro" | "team" = "free") {
    const mockLimiters = {
      free: new MockRateLimiter(100),
      pro: new MockRateLimiter(1000),
      team: new MockRateLimiter(10000),
    };

    return Layer.mergeAll(
      RateLimiter.Live(mockLimiters),
      createMockPaymentsLayer(planTier),
      TestDrizzleORM,
    );
  }

  describe("Basic Rate Limiting", () => {
    it.effect("allows first request for organization", () =>
      Effect.gen(function* () {
        const rateLimiter = yield* RateLimiter;

        const result = yield* rateLimiter.checkRateLimit({
          organizationId: TEST_ORG_ID,
        });

        expect(result.allowed).toBe(true);
        expect(result.limit).toBe(100); // Free plan limit
        expect(result.resetAt).toBeInstanceOf(Date);
      }).pipe(Effect.provide(createTestLayer())),
    );

    it.effect("allows requests within limit", () =>
      Effect.gen(function* () {
        const rateLimiter = yield* RateLimiter;

        // Make 5 requests
        for (let i = 0; i < 5; i++) {
          const result = yield* rateLimiter.checkRateLimit({
            organizationId: TEST_ORG_ID,
          });

          expect(result.allowed).toBe(true);
        }
      }).pipe(Effect.provide(createTestLayer())),
    );

    it.effect("denies request when at limit", () =>
      Effect.gen(function* () {
        const rateLimiter = yield* RateLimiter;

        // Free plan: 100 requests/minute
        // Make 100 requests to hit the limit
        for (let i = 0; i < 100; i++) {
          yield* rateLimiter.checkRateLimit({
            organizationId: TEST_ORG_ID,
          });
        }

        // 101st request should fail
        const result = yield* rateLimiter
          .checkRateLimit({
            organizationId: TEST_ORG_ID,
          })
          .pipe(Effect.flip);

        assert(result instanceof RateLimitError);
        expect(result.organizationId).toBe(TEST_ORG_ID);
        expect(result.limit).toBe(100);
        expect(result.retryAfter).toBeGreaterThan(0);
      }).pipe(Effect.provide(createTestLayer())),
    );
  });

  describe("Sliding Window Behavior", () => {
    it.effect("calculates reset time correctly", () =>
      Effect.gen(function* () {
        const rateLimiter = yield* RateLimiter;
        const now = Date.now();

        // Make a new request
        const result = yield* rateLimiter.checkRateLimit({
          organizationId: TEST_ORG_ID,
        });

        expect(result.allowed).toBe(true);
        // Reset time should be ~60 seconds from now
        const resetDelta = result.resetAt.getTime() - now;
        expect(resetDelta).toBeGreaterThan(59000); // ~60s (allow 1s buffer)
        expect(resetDelta).toBeLessThan(61000);
      }).pipe(Effect.provide(createTestLayer())),
    );

    it.effect("calculates reset time correctly when rate limit exceeded", () =>
      Effect.gen(function* () {
        const rateLimiter = yield* RateLimiter;
        const now = Date.now();

        // Fill up to exactly the limit (100 total requests)
        for (let i = 0; i < 100; i++) {
          yield* rateLimiter.checkRateLimit({
            organizationId: TEST_ORG_ID,
          });
        }

        // The 101st request should be rate limited
        const result = yield* rateLimiter
          .checkRateLimit({
            organizationId: TEST_ORG_ID,
          })
          .pipe(Effect.flip);

        assert(result instanceof RateLimitError);
        expect(result.retryAfter).toBeGreaterThan(0);
        expect(result.retryAfter).toBeLessThanOrEqual(60);

        // Verify reset time is reasonable
        const resetDelta = Date.now() + result.retryAfter * 1000 - now;
        expect(resetDelta).toBeGreaterThan(0);
        expect(resetDelta).toBeLessThanOrEqual(61000);
      }).pipe(Effect.provide(createTestLayer())),
    );
  });

  describe("Plan Tier Differences", () => {
    it.effect("enforces free plan limit (100/min)", () =>
      Effect.gen(function* () {
        const rateLimiter = yield* RateLimiter;

        // Make 100 requests
        for (let i = 0; i < 100; i++) {
          yield* rateLimiter.checkRateLimit({
            organizationId: TEST_ORG_ID,
          });
        }

        // 101st should fail
        const result = yield* rateLimiter
          .checkRateLimit({
            organizationId: TEST_ORG_ID,
          })
          .pipe(Effect.flip);

        assert(result instanceof RateLimitError);
      }).pipe(Effect.provide(createTestLayer())),
    );
  });

  describe("Multi-Organization Isolation", () => {
    it.effect("different organizations have independent limits", () =>
      Effect.gen(function* () {
        const rateLimiter = yield* RateLimiter;

        // Exhaust org 1's limit
        for (let i = 0; i < 100; i++) {
          yield* rateLimiter.checkRateLimit({
            organizationId: TEST_ORG_ID,
          });
        }

        // Org 1 should be rate limited
        const org1Result = yield* rateLimiter
          .checkRateLimit({
            organizationId: TEST_ORG_ID,
          })
          .pipe(Effect.flip);
        assert(org1Result instanceof RateLimitError);

        // Org 2 should still be allowed
        const org2Result = yield* rateLimiter.checkRateLimit({
          organizationId: TEST_ORG_ID_2,
        });
        expect(org2Result.allowed).toBe(true);
      }).pipe(Effect.provide(createTestLayer())),
    );
  });

  describe("Edge Cases", () => {
    it.effect("returns correct retry-after when rate limited", () =>
      Effect.gen(function* () {
        const rateLimiter = yield* RateLimiter;

        // Fill up the limit
        for (let i = 0; i < 100; i++) {
          yield* rateLimiter.checkRateLimit({
            organizationId: TEST_ORG_ID,
          });
        }

        // Next request should fail with retry-after
        const result = yield* rateLimiter
          .checkRateLimit({
            organizationId: TEST_ORG_ID,
          })
          .pipe(Effect.flip);

        assert(result instanceof RateLimitError);
        expect(result.retryAfter).toBeGreaterThan(0);
        expect(result.retryAfter).toBeLessThanOrEqual(60);
        expect(result.message).toContain("100 requests per minute");
      }).pipe(Effect.provide(createTestLayer())),
    );
  });

  describe("Concurrent Requests", () => {
    it.effect("handles multiple sequential requests correctly", () =>
      Effect.gen(function* () {
        const rateLimiter = yield* RateLimiter;

        // Make 10 sequential requests
        for (let i = 0; i < 10; i++) {
          const result = yield* rateLimiter.checkRateLimit({
            organizationId: TEST_ORG_ID,
          });
          expect(result.allowed).toBe(true);
        }
      }).pipe(Effect.provide(createTestLayer())),
    );
  });

  describe("addRateLimitHeaders", () => {
    it.effect("adds rate limit headers to response", () =>
      Effect.gen(function* () {
        const rateLimiter = yield* RateLimiter;

        // Make a request to get a valid result
        const result = yield* rateLimiter.checkRateLimit({
          organizationId: TEST_ORG_ID,
        });

        // Create a response and add headers
        const response = new Response("test", { status: 200 });
        const responseWithHeaders = rateLimiter.addRateLimitHeaders({
          response,
          result,
        });

        // Verify headers are added
        expect(responseWithHeaders.headers.get("X-RateLimit-Limit")).toBe(
          "100",
        );
        expect(
          responseWithHeaders.headers.get("X-RateLimit-Reset"),
        ).toBeTruthy();

        // Verify reset time is a valid Unix timestamp
        const resetTime = Number(
          responseWithHeaders.headers.get("X-RateLimit-Reset"),
        );
        expect(resetTime).toBeGreaterThan(Date.now() / 1000);
      }).pipe(Effect.provide(createTestLayer())),
    );

    it.effect("skips adding headers when limit is 0", () =>
      Effect.gen(function* () {
        const rateLimiter = yield* RateLimiter;

        // Create a result with limit 0 (no rate limiting)
        const result = {
          allowed: true,
          limit: 0,
          resetAt: new Date(),
        };

        // Create a response and try to add headers
        const response = new Response("test", { status: 200 });
        const responseWithHeaders = rateLimiter.addRateLimitHeaders({
          response,
          result,
        });

        // Verify headers are NOT added
        expect(responseWithHeaders.headers.get("X-RateLimit-Limit")).toBeNull();
        expect(responseWithHeaders.headers.get("X-RateLimit-Reset")).toBeNull();
      }).pipe(Effect.provide(createTestLayer())),
    );

    it.effect("preserves existing response properties", () =>
      Effect.gen(function* () {
        const rateLimiter = yield* RateLimiter;

        const result = yield* rateLimiter.checkRateLimit({
          organizationId: TEST_ORG_ID,
        });

        // Create a response with custom headers and status
        const originalResponse = new Response("test body", {
          status: 201,
          statusText: "Created",
          headers: {
            "Content-Type": "application/json",
            "X-Custom-Header": "custom-value",
          },
        });

        const responseWithHeaders = rateLimiter.addRateLimitHeaders({
          response: originalResponse,
          result,
        });

        // Verify original properties are preserved
        expect(responseWithHeaders.status).toBe(201);
        expect(responseWithHeaders.statusText).toBe("Created");
        expect(responseWithHeaders.headers.get("Content-Type")).toBe(
          "application/json",
        );
        expect(responseWithHeaders.headers.get("X-Custom-Header")).toBe(
          "custom-value",
        );

        // Verify rate limit headers are added
        expect(responseWithHeaders.headers.get("X-RateLimit-Limit")).toBe(
          "100",
        );
      }).pipe(Effect.provide(createTestLayer())),
    );
  });

  describe("createRateLimitErrorResponse", () => {
    it.effect("creates 429 response with correct structure", () =>
      Effect.gen(function* () {
        const rateLimiter = yield* RateLimiter;

        // Create a rate limit error
        const error = new RateLimitError({
          message: "Rate limit exceeded",
          organizationId: TEST_ORG_ID,
          limit: 100,
          retryAfter: 45,
          planTier: "free",
        });

        const response = rateLimiter.createRateLimitErrorResponse({ error });

        // Verify status code
        expect(response.status).toBe(429);
        expect(response.statusText).toBe("Too Many Requests");

        // Verify headers
        expect(response.headers.get("Content-Type")).toBe("application/json");
        expect(response.headers.get("X-RateLimit-Limit")).toBe("100");
        expect(response.headers.get("Retry-After")).toBe("45");
        expect(response.headers.get("X-RateLimit-Reset")).toBeTruthy();

        // Verify body structure
        const body = JSON.parse(
          yield* Effect.promise(() => response.text()),
        ) as {
          tag: string;
          message: string;
          organizationId: string;
          limit: number;
          retryAfter: number;
          planTier: string;
        };
        expect(body.tag).toBe("RateLimitError");
        expect(body.message).toBe("Rate limit exceeded");
        expect(body.organizationId).toBe(TEST_ORG_ID);
        expect(body.limit).toBe(100);
        expect(body.retryAfter).toBe(45);
        expect(body.planTier).toBe("free");
      }).pipe(Effect.provide(createTestLayer())),
    );

    it.effect("calculates X-RateLimit-Reset correctly", () =>
      Effect.gen(function* () {
        const rateLimiter = yield* RateLimiter;

        const now = Date.now();
        const retryAfter = 30; // 30 seconds

        const error = new RateLimitError({
          message: "Rate limit exceeded",
          organizationId: TEST_ORG_ID,
          limit: 100,
          retryAfter,
          planTier: "free",
        });

        const response = rateLimiter.createRateLimitErrorResponse({ error });

        // Verify reset time is approximately retryAfter seconds from now
        const resetTime =
          Number(response.headers.get("X-RateLimit-Reset")) * 1000;
        const expectedResetTime = now + retryAfter * 1000;

        // Allow 2 second buffer for test execution time
        expect(resetTime).toBeGreaterThan(expectedResetTime - 2000);
        expect(resetTime).toBeLessThan(expectedResetTime + 2000);
      }).pipe(Effect.provide(createTestLayer())),
    );
  });

  describe("Zero Rate Limit", () => {
    it.effect("handles zero rate limit correctly", () => {
      // Create custom Payments layer with zero rate limit
      const ZeroLimitPaymentsLayer = Layer.succeed(Payments, {
        customers: {
          subscriptions: {
            getPlan: () => Effect.succeed("free" as const),
            getPlanLimits: () =>
              Effect.succeed({
                seats: 1,
                projects: 1,
                apiRequestsPerMinute: 0,
                spansPerMonth: 0,
                dataRetentionDays: 30,
              }),
          },
        } as never,
        products: {} as never,
        paymentIntents: {} as never,
        paymentMethods: {} as never,
      });

      const mockLimiters = {
        free: new MockRateLimiter(0),
        pro: new MockRateLimiter(1000),
        team: new MockRateLimiter(10000),
      };

      const testLayer = Layer.mergeAll(
        RateLimiter.Live(mockLimiters),
        ZeroLimitPaymentsLayer,
        TestDrizzleORM,
      );

      return Effect.gen(function* () {
        const rateLimiter = yield* RateLimiter;
        const now = Date.now();

        // First request should be rate limited immediately with 0 limit
        const result = yield* rateLimiter
          .checkRateLimit({
            organizationId: TEST_ORG_ID,
          })
          .pipe(Effect.flip);

        assert(result instanceof RateLimitError);
        expect(result.limit).toBe(0);
        expect(result.retryAfter).toBeGreaterThan(0);
        expect(result.retryAfter).toBeLessThanOrEqual(60);

        // Verify reset time is calculated correctly
        const expectedResetTime = now + 60000;
        const actualResetTime = Date.now() + result.retryAfter * 1000;
        expect(actualResetTime).toBeGreaterThan(expectedResetTime - 2000);
        expect(actualResetTime).toBeLessThan(expectedResetTime + 2000);
      }).pipe(Effect.provide(testLayer));
    });
  });

  describe("Fail-Closed Behavior", () => {
    it.effect("fails closed when payments service throws non-Error", () => {
      // Create a Payments layer that throws a non-Error value (string)
      const FailingPaymentsLayer = Layer.succeed(Payments, {
        customers: {
          subscriptions: {
            getPlan: () => Effect.fail("Payments down"), // Non-Error value
            getPlanLimits: (tier: "free" | "pro" | "team") =>
              Effect.succeed({
                seats: tier === "free" ? 1 : tier === "pro" ? 5 : Infinity,
                projects: tier === "free" ? 1 : tier === "pro" ? 5 : Infinity,
                spansPerMonth: tier === "free" ? 1_000_000 : Infinity,
                apiRequestsPerMinute:
                  tier === "free" ? 100 : tier === "pro" ? 1000 : 10000,
                dataRetentionDays:
                  tier === "free" ? 30 : tier === "pro" ? 90 : 180,
              }),
          },
        } as never,
        products: {} as never,
        paymentIntents: {} as never,
        paymentMethods: {} as never,
      });

      const mockLimiters = {
        free: new MockRateLimiter(100),
        pro: new MockRateLimiter(1000),
        team: new MockRateLimiter(10000),
      };

      const testLayer = Layer.mergeAll(
        RateLimiter.Live(mockLimiters),
        FailingPaymentsLayer,
        TestDrizzleORM,
      );

      return Effect.gen(function* () {
        const rateLimiter = yield* RateLimiter;

        // Should fail-closed with ServiceUnavailableError
        const result = yield* rateLimiter
          .checkRateLimit({
            organizationId: TEST_ORG_ID,
          })
          .pipe(Effect.flip);

        // Should get a ServiceUnavailableError with String(error)
        assert(result instanceof ServiceUnavailableError);
        expect(result.message).toContain("Unable to determine plan tier");
        expect(result.message).toContain("Payments down");
        expect(result.service).toBe("payments");
      }).pipe(Effect.provide(testLayer));
    });

    it.effect("fails closed when payments service throws error", () => {
      // Create a Payments layer that throws errors
      const FailingPaymentsLayer = Layer.succeed(Payments, {
        customers: {
          subscriptions: {
            getPlan: () =>
              Effect.fail(new Error("Payments service unavailable")),
            getPlanLimits: (tier: "free" | "pro" | "team") =>
              Effect.succeed({
                seats: tier === "free" ? 1 : tier === "pro" ? 5 : Infinity,
                projects: tier === "free" ? 1 : tier === "pro" ? 5 : Infinity,
                spansPerMonth: tier === "free" ? 1_000_000 : Infinity,
                apiRequestsPerMinute:
                  tier === "free" ? 100 : tier === "pro" ? 1000 : 10000,
                dataRetentionDays:
                  tier === "free" ? 30 : tier === "pro" ? 90 : 180,
              }),
          },
        } as never,
        products: {} as never,
        paymentIntents: {} as never,
        paymentMethods: {} as never,
      });

      const mockLimiters = {
        free: new MockRateLimiter(100),
        pro: new MockRateLimiter(1000),
        team: new MockRateLimiter(10000),
      };

      const testLayer = Layer.mergeAll(
        RateLimiter.Live(mockLimiters),
        FailingPaymentsLayer,
        TestDrizzleORM,
      );

      return Effect.gen(function* () {
        const rateLimiter = yield* RateLimiter;

        // Should fail-closed with ServiceUnavailableError
        const result = yield* rateLimiter
          .checkRateLimit({
            organizationId: TEST_ORG_ID,
          })
          .pipe(Effect.flip);

        // Should get a ServiceUnavailableError (503) wrapping the payments error
        assert(result instanceof ServiceUnavailableError);
        expect(result.message).toContain("Unable to determine plan tier");
        expect(result.service).toBe("payments");
        expect(ServiceUnavailableError.status).toBe(503);
      }).pipe(Effect.provide(testLayer));
    });

    it.effect("fails closed when rate limiter throws error", () => {
      // Create a mock limiter that throws errors
      const mockLimiters = {
        free: {
          limit: () => Promise.reject(new Error("Rate limiter error")),
        } as never,
        pro: new MockRateLimiter(1000),
        team: new MockRateLimiter(10000),
      };

      const testLayer = Layer.mergeAll(
        RateLimiter.Live(mockLimiters),
        createMockPaymentsLayer("free"),
        TestDrizzleORM,
      );

      return Effect.gen(function* () {
        const rateLimiter = yield* RateLimiter;

        // Should fail-closed and reject the request with ServiceUnavailableError
        const result = yield* rateLimiter
          .checkRateLimit({
            organizationId: TEST_ORG_ID,
          })
          .pipe(Effect.flip);

        // Should get a ServiceUnavailableError (503) wrapping the rate limiter error
        assert(result instanceof ServiceUnavailableError);
        expect(result.message).toContain("Rate limiter service unavailable");
        expect(ServiceUnavailableError.status).toBe(503);
      }).pipe(Effect.provide(testLayer));
    });
  });
});
