/**
 * @fileoverview Rate limiting service using Cloudflare's native rate limiting API.
 *
 * Provides per-organization rate limiting based on subscription plan tiers.
 * Uses Cloudflare's atomic rate limiting API for accurate enforcement.
 *
 * ## Architecture
 *
 * - **Algorithm**: Token bucket (handled by Cloudflare)
 * - **Storage**: Cloudflare rate limiter bindings (atomic operations)
 * - **Scope**: Per-organization (all API keys share the same limit)
 * - **Error Handling**: Fail-closed (rate limits are tied to billing)
 *
 * ## Usage
 *
 * ```ts
 * import { RateLimiter } from "@/rate-limiting";
 *
 * const program = Effect.gen(function* () {
 *   const rateLimiter = yield* RateLimiter;
 *
 *   const result = yield* rateLimiter.checkRateLimit({
 *     organizationId: "org_123",
 *   });
 *
 *   if (!result.allowed) {
 *     return rateLimiter.createRateLimitErrorResponse(result.error);
 *   }
 *
 *   const response = new Response("Success");
 *   return rateLimiter.addRateLimitHeaders({ response, result });
 * });
 * ```
 */

import { Context, Effect, Layer } from "effect";
import { RateLimitError, ServiceUnavailableError } from "@/errors";
import { Payments } from "@/payments";
import type { PlanTier } from "@/payments/subscriptions/types";
import type { RateLimiterBinding } from "@/workers/config";

/**
 * Result of a rate limit check.
 *
 * Contains information about whether the request is allowed and current
 * rate limit status for including in response headers.
 */
export interface RateLimitResult {
  /** Whether the request is allowed */
  allowed: boolean;
  /** Maximum requests per minute for this plan */
  limit: number;
  /** When the rate limit will reset */
  resetAt: Date;
}

/**
 * Constants for rate limiting configuration.
 */
const RATE_LIMIT_CONFIG = {
  /** Rate limit window duration in milliseconds (60 seconds) */
  WINDOW_MS: 60000,
} as const;

/**
 * Rate limiter client interface.
 *
 * Provides all rate limiting operations including checking limits,
 * adding headers to responses, and creating error responses.
 */
export interface RateLimiterClient {
  /**
   * Check if a request is allowed under the rate limit.
   *
   * @param params - Organization ID to check rate limit for
   * @returns Rate limit result with current status
   * @throws RateLimitError if limit exceeded
   * @throws ServiceUnavailableError if rate limiter service is unavailable
   * @throws Errors from Payments service (DatabaseError, NotFoundError, StripeError, etc.)
   */
  checkRateLimit: (params: {
    organizationId: string;
  }) => Effect.Effect<
    RateLimitResult,
    RateLimitError | ServiceUnavailableError,
    Payments
  >;

  /**
   * Add rate limit headers to a response.
   *
   * Adds standard X-RateLimit-* headers to inform clients about their
   * current rate limit status.
   *
   * @param params - Response to modify and rate limit result
   * @returns Modified response with rate limit headers
   */
  addRateLimitHeaders: (params: {
    response: Response;
    result: RateLimitResult;
  }) => Response;

  /**
   * Create a 429 response for rate limit errors.
   *
   * @param params - The rate limit error
   * @returns Response with 429 status and appropriate headers
   */
  createRateLimitErrorResponse: (params: { error: RateLimitError }) => Response;
}

/**
 * Creates a rate limit exceeded error.
 *
 * Includes detailed information about the limit, retry timing, and
 * user's plan tier.
 */
function createRateLimitError({
  organizationId,
  planTier,
  limit,
  resetAt,
  now,
}: {
  organizationId: string;
  planTier: PlanTier;
  limit: number;
  resetAt: Date;
  now: number;
}): RateLimitError {
  const retryAfter = Math.ceil((resetAt.getTime() - now) / 1000);

  return new RateLimitError({
    message: `Rate limit exceeded. Your ${planTier} plan allows ${limit} requests per minute. Please try again in ${retryAfter} seconds.`,
    organizationId,
    limit,
    retryAfter,
    planTier,
  });
}

/**
 * Core rate limit check implementation.
 *
 * Uses Cloudflare's native rate limiting API to determine if a request
 * should be allowed based on the organization's plan limits.
 */
function checkRateLimit({
  limiters,
  organizationId,
}: {
  limiters: {
    free: RateLimiterBinding;
    pro: RateLimiterBinding;
    team: RateLimiterBinding;
  };
  organizationId: string;
}): Effect.Effect<
  RateLimitResult,
  RateLimitError | ServiceUnavailableError,
  Payments
> {
  return Effect.gen(function* () {
    const payments = yield* Payments;

    // Step 1: Get plan tier and limits (wrap errors in ServiceUnavailableError)
    const planTier = yield* payments.customers.subscriptions
      .getPlan(organizationId)
      .pipe(
        Effect.mapError(
          (error) =>
            new ServiceUnavailableError({
              message: `Unable to determine plan tier: ${error instanceof Error ? error.message : String(error)}`,
              service: "payments",
            }),
        ),
      );
    const planLimits =
      yield* payments.customers.subscriptions.getPlanLimits(planTier);
    const limit = planLimits.apiRequestsPerMinute;

    // Step 2: Select appropriate rate limiter based on plan tier
    const limiter = limiters[planTier];

    // Step 3: Call Cloudflare rate limiter (fail-closed with 503 error)
    const result = yield* Effect.tryPromise(() =>
      limiter.limit({ key: organizationId }),
    ).pipe(
      Effect.mapError(
        (error) =>
          new ServiceUnavailableError({
            message: `Rate limiter service unavailable: ${error instanceof Error ? error.message : /* v8 ignore next 1 */ String(error)}`,
            service: "cloudflare-rate-limiter",
          }),
      ),
    );

    const now = Date.now();
    const resetAt = new Date(now + RATE_LIMIT_CONFIG.WINDOW_MS);

    // Step 4: Check if request is allowed
    if (result.success) {
      return {
        allowed: true,
        limit,
        resetAt,
      };
    }

    // Step 5: Rate limit exceeded - return error
    return yield* Effect.fail(
      createRateLimitError({ organizationId, planTier, limit, resetAt, now }),
    );
  });
}

/**
 * Add rate limit headers to a response.
 *
 * Adds standard X-RateLimit-* headers to inform clients about their
 * current rate limit status.
 */
function addRateLimitHeaders({
  response,
  result,
}: {
  response: Response;
  result: RateLimitResult;
}): Response {
  // Skip adding headers if limit is 0 (no rate limiting applied)
  if (result.limit === 0) {
    return response;
  }

  const headers = new Headers(response.headers);
  headers.set("X-RateLimit-Limit", result.limit.toString());
  headers.set(
    "X-RateLimit-Reset",
    Math.floor(result.resetAt.getTime() / 1000).toString(),
  );

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

/**
 * Create a 429 response with rate limit headers for RateLimitError.
 */
function createRateLimitErrorResponse({
  error,
}: {
  error: RateLimitError;
}): Response {
  const body = JSON.stringify({
    tag: "RateLimitError",
    message: error.message,
    organizationId: error.organizationId,
    limit: error.limit,
    retryAfter: error.retryAfter,
    planTier: error.planTier,
  });

  const headers = new Headers({
    "Content-Type": "application/json",
    "X-RateLimit-Limit": error.limit.toString(),
    "X-RateLimit-Reset": Math.floor(
      (Date.now() + error.retryAfter * 1000) / 1000,
    ).toString(),
    "Retry-After": error.retryAfter.toString(),
  });

  return new Response(body, {
    status: 429,
    statusText: "Too Many Requests",
    headers,
  });
}

/**
 * Rate limiter service tag for Effect dependency injection.
 *
 * Provides the RateLimiter service which can be used to check
 * and enforce rate limits across the application.
 */
export class RateLimiter extends Context.Tag("RateLimiter")<
  RateLimiter,
  RateLimiterClient
>() {
  /**
   * Live layer that creates the RateLimiter service.
   *
   * @param limiters - Cloudflare rate limiter bindings for each plan tier
   * @returns Layer that provides the RateLimiter service
   */
  static Live(limiters: {
    free: RateLimiterBinding;
    pro: RateLimiterBinding;
    team: RateLimiterBinding;
  }) {
    return Layer.succeed(RateLimiter, {
      checkRateLimit: ({ organizationId }: { organizationId: string }) =>
        Effect.gen(function* () {
          return yield* checkRateLimit({ limiters, organizationId });
        }),
      addRateLimitHeaders,
      createRateLimitErrorResponse,
    });
  }
}
