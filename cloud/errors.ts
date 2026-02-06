import { Schema } from "effect";

/**
 * Unified error definitions for the Mirascope Cloud application.
 *
 * All errors use Schema.TaggedError with a static `status` property
 * for HTTP status code mapping.
 */

// =============================================================================
// Database Errors
// =============================================================================

export class DatabaseError extends Schema.TaggedError<DatabaseError>()(
  "DatabaseError",
  {
    message: Schema.String,
    cause: Schema.optional(Schema.Unknown),
  },
) {
  static readonly status = 500 as const;
}
export class DeletedUserError extends Schema.TaggedError<DeletedUserError>()(
  "DeletedUserError",
  {
    message: Schema.String,
    resource: Schema.optional(Schema.String),
  },
) {
  static readonly status = 401 as const;
}

export class AlreadyExistsError extends Schema.TaggedError<AlreadyExistsError>()(
  "AlreadyExistsError",
  {
    message: Schema.String,
    resource: Schema.optional(Schema.String),
  },
) {
  static readonly status = 409 as const;
}

export class InvalidSessionError extends Schema.TaggedError<InvalidSessionError>()(
  "InvalidSessionError",
  {
    message: Schema.String,
    sessionId: Schema.optional(Schema.String),
  },
) {
  static readonly status = 401 as const;
}

// =============================================================================
// API Errors
// =============================================================================

export class HandlerError extends Schema.TaggedError<HandlerError>()(
  "HandlerError",
  {
    message: Schema.String,
    cause: Schema.optional(Schema.Unknown),
  },
) {
  static readonly status = 500 as const;
}

export class InternalError extends Schema.TaggedError<InternalError>()(
  "InternalError",
  {
    message: Schema.String,
    cause: Schema.optional(Schema.Unknown),
  },
) {
  static readonly status = 500 as const;
}

// =============================================================================
// HTTP Errors (shared)
// =============================================================================

export class NotFoundError extends Schema.TaggedError<NotFoundError>()(
  "NotFoundError",
  {
    message: Schema.String,
    resource: Schema.optional(Schema.String),
  },
) {
  static readonly status = 404 as const;
}

export class UnauthorizedError extends Schema.TaggedError<UnauthorizedError>()(
  "UnauthorizedError",
  {
    message: Schema.String,
  },
) {
  static readonly status = 401 as const;
}

export class PermissionDeniedError extends Schema.TaggedError<PermissionDeniedError>()(
  "PermissionDeniedError",
  {
    message: Schema.String,
    resource: Schema.optional(Schema.String),
  },
) {
  static readonly status = 403 as const;
}

/**
 * Error for attempting to update an immutable resource.
 *
 * Used when a resource cannot be modified after creation, regardless of
 * the user's permissions. This is distinct from PermissionDeniedError
 * which indicates insufficient permissions.
 */
export class ImmutableResourceError extends Schema.TaggedError<ImmutableResourceError>()(
  "ImmutableResourceError",
  {
    message: Schema.String,
    resource: Schema.optional(Schema.String),
  },
) {
  static readonly status = 400 as const;
}

// =============================================================================
// Configuration Errors
// =============================================================================

/**
 * Error that occurs when required environment variables are missing or empty.
 *
 * This error is raised during Settings layer creation when one or more
 * required environment variables are not set. The application cannot
 * start without all required configuration.
 *
 * @example
 * ```ts
 * // At app startup, this becomes a fatal error with clear message
 * const AppLayer = Settings.Live.pipe(
 *   Layer.orDieWith((error) =>
 *     new Error(`Settings validation failed:\n${error.message}`)
 *   )
 * );
 * ```
 */
export class SettingsValidationError extends Schema.TaggedError<SettingsValidationError>()(
  "SettingsValidationError",
  {
    message: Schema.String,
    missingVariables: Schema.Array(Schema.String),
  },
) {
  static readonly status = 500 as const;
}

// =============================================================================
// Payment Errors
// =============================================================================

/**
 * Error that occurs during Stripe API operations.
 *
 * This error wraps any failures from the Stripe SDK, including:
 * - Network errors
 * - API errors (invalid parameters, authentication failures, etc.)
 * - Rate limiting
 * - Server errors
 *
 * @example
 * ```ts
 * const customer = yield* stripe.customers.create({ email: "..." }).pipe(
 *   Effect.catchTag("StripeError", (error) => {
 *     console.error("Stripe operation failed:", error.message);
 *     return Effect.succeed(null);
 *   })
 * );
 * ```
 */
export class StripeError extends Schema.TaggedError<StripeError>()(
  "StripeError",
  {
    message: Schema.String,
    cause: Schema.optional(Schema.Unknown),
  },
) {
  static readonly status = 500 as const;
}

/**
 * Error that occurs when attempting to cancel subscriptions but past_due subscriptions exist.
 *
 * This error is raised when trying to cancel all subscriptions (e.g., during org deletion)
 * but one or more subscriptions have a past_due status, indicating failed payments.
 * Past_due subscriptions represent outstanding debt and should be resolved before
 * allowing cancellation or org deletion.
 *
 * The HTTP status code is 409 (Conflict) to indicate that the operation conflicts
 * with the current state of the subscriptions.
 *
 * @example
 * ```ts
 * yield* payments.customers.subscriptions.cancel(stripeCustomerId).pipe(
 *   Effect.catchTag("SubscriptionPastDueError", (error) => {
 *     console.error("Cannot cancel - resolve past_due subscriptions first");
 *     return Effect.fail(new HandlerError({
 *       message: "Resolve outstanding payments before deletion"
 *     }));
 *   })
 * );
 * ```
 */
export class SubscriptionPastDueError extends Schema.TaggedError<SubscriptionPastDueError>()(
  "SubscriptionPastDueError",
  {
    message: Schema.String,
    stripeCustomerId: Schema.String,
    pastDueSubscriptionIds: Schema.Array(Schema.String),
  },
) {
  static readonly status = 409 as const;
}

// =============================================================================
// Email Errors
// =============================================================================

/**
 * Error that occurs during Resend API operations.
 *
 * This error wraps any failures from the Resend SDK, including:
 * - Network errors
 * - API errors (invalid parameters, authentication failures, etc.)
 * - Rate limiting
 * - Server errors
 *
 * @example
 * ```ts
 * const email = yield* resend.emails.send({ ... }).pipe(
 *   Effect.catchTag("ResendError", (error) => {
 *     console.error("Resend operation failed:", error.message);
 *     return Effect.succeed(null);
 *   })
 * );
 * ```
 */
export class ResendError extends Schema.TaggedError<ResendError>()(
  "ResendError",
  {
    message: Schema.String,
    cause: Schema.optional(Schema.Unknown),
  },
) {
  static readonly status = 500 as const;
}

/**
 * Error that occurs when rendering an email template fails.
 *
 * This error is raised when React Email's render() function fails to convert
 * a React component to HTML. This can happen due to:
 * - Invalid JSX in the template
 * - Errors thrown during component render
 * - Missing or invalid props
 *
 * @example
 * ```ts
 * const html = yield* renderEmailTemplate(component).pipe(
 *   Effect.catchTag("EmailRenderError", (error) => {
 *     console.error("Template rendering failed:", error.message);
 *     return Effect.succeed(null);
 *   })
 * );
 * ```
 */
export class EmailRenderError extends Schema.TaggedError<EmailRenderError>()(
  "EmailRenderError",
  {
    message: Schema.String,
    cause: Schema.optional(Schema.Unknown),
  },
) {
  static readonly status = 500 as const;
}

/**
 * Error that occurs when attempting to reserve funds but insufficient balance is available.
 *
 * This error is returned when:
 * - Available balance < estimated cost
 * - Available = total balance - SUM(active reservations)
 *
 * The HTTP status code is 402 (Payment Required) to indicate that the user
 * needs to add more credits before they can make the request.
 *
 * @example
 * ```ts
 * const reservation = yield* payments.customers.reserveFunds({ ... }).pipe(
 *   Effect.catchTag("InsufficientFundsError", (error) => {
 *     console.error(`Need $${error.required}, have $${error.available}`);
 *     return Effect.fail(new UnauthorizedError({ message: "Top up your credits" }));
 *   })
 * );
 * ```
 */
export class InsufficientFundsError extends Schema.TaggedError<InsufficientFundsError>()(
  "InsufficientFundsError",
  {
    message: Schema.String,
    required: Schema.Number,
    available: Schema.Number,
  },
) {
  static readonly status = 402 as const;
}

/**
 * Error that occurs when attempting to modify a credit reservation in an invalid state.
 *
 * This error is returned when trying to settle or release a reservation that:
 * - Doesn't exist (may have been deleted or never created)
 * - Is already settled (would cause double-charging)
 * - Is already released (conflicting lifecycle transitions)
 * - Is expired (should use CRON job to handle)
 *
 * The HTTP status code is 500 because this indicates a bug in our reservation
 * lifecycle management that should never happen in normal operation.
 *
 * @example
 * ```ts
 * yield* payments.customers.settleFunds(reservationId, actualCost).pipe(
 *   Effect.catchTag("ReservationStateError", (error) => {
 *     console.error(`Reservation ${error.reservationId} in invalid state:`, error.message);
 *     // Log for investigation - this indicates a bug
 *     return Effect.fail(new InternalError({ message: "Reservation error" }));
 *   })
 * );
 * ```
 */
export class ReservationStateError extends Schema.TaggedError<ReservationStateError>()(
  "ReservationStateError",
  {
    message: Schema.String,
    reservationId: Schema.String,
  },
) {
  static readonly status = 500 as const;
}

// =============================================================================
// Proxy Errors
// =============================================================================

/**
 * Error that occurs during AI provider proxy operations.
 *
 * This error wraps failures when proxying requests to external AI providers
 * (OpenAI, Anthropic, Google AI), including:
 * - Network errors
 * - Provider API errors
 * - Configuration errors (missing API keys)
 * - Timeout errors
 *
 * @example
 * ```ts
 * const response = yield* proxyToProvider({ ... }).pipe(
 *   Effect.catchTag("ProxyError", (error) => {
 *     console.error("Proxy failed:", error.message);
 *     return Effect.fail(new InternalError({ message: "Provider unavailable" }));
 *   })
 * );
 * ```
 */
export class ProxyError extends Schema.TaggedError<ProxyError>()("ProxyError", {
  message: Schema.String,
  cause: Schema.optional(Schema.Unknown),
}) {
  static readonly status = 502 as const;
}

// =============================================================================
// Analytics Errors
// =============================================================================

/**
 * Error that occurs during analytics operations (Google Analytics, PostHog, etc.).
 *
 * NOTE: Analytics errors are typically caught internally and logged rather than
 * thrown, ensuring analytics failures never break the application. This error is
 * defined for consistency with other services but should rarely be seen by
 * consumers.
 *
 * This error wraps failures from analytics providers, including:
 * - Script loading errors
 * - Network errors
 * - API errors
 * - Configuration errors
 *
 * @example
 * ```ts
 * const result = yield* analytics.trackEvent({ name: "signup" }).pipe(
 *   Effect.catchTag("AnalyticsError", (error) => {
 *     console.error(`${error.provider} tracking failed:`, error.message);
 *     return Effect.succeed(void 0);
 *   })
 * );
 * ```
 */
export class AnalyticsError extends Schema.TaggedError<AnalyticsError>()(
  "AnalyticsError",
  {
    message: Schema.String,
    provider: Schema.optional(Schema.Literal("GoogleAnalytics", "PostHog")),
    cause: Schema.optional(Schema.Unknown),
  },
) {
  static readonly status = 500 as const;
}

/**
 * Error that occurs during ClickHouse operations.
 *
 * This error wraps any failures from ClickHouse client operations, including:
 * - Connection errors
 * - Query execution errors
 * - Insert failures
 * - Timeout errors
 *
 * @example
 * ```ts
 * const result = yield* clickhouse.unsafeQuery<Span>("SELECT * FROM spans").pipe(
 *   Effect.catchTag("ClickHouseError", (error) => {
 *     console.error("ClickHouse operation failed:", error.message);
 *     return Effect.succeed([]);
 *   })
 * );
 * ```
 */
export class ClickHouseError extends Schema.TaggedError<ClickHouseError>()(
  "ClickHouseError",
  {
    message: Schema.String,
    cause: Schema.optional(Schema.Unknown),
  },
) {
  static readonly status = 500 as const;
}

// =============================================================================
// Cloudflare Errors
// =============================================================================

/**
 * Error thrown by Cloudflare API operations.
 *
 * Covers R2 bucket operations, Durable Object management, container lifecycle,
 * and API token creation failures.
 */
export class CloudflareApiError extends Schema.TaggedError<CloudflareApiError>()(
  "CloudflareApiError",
  {
    message: Schema.String,
    cause: Schema.optional(Schema.Unknown),
  },
) {
  static readonly status = 502 as const;
}

// =============================================================================
// Pricing Errors
// =============================================================================

/**
 * Error that occurs when pricing data is unavailable for cost estimation.
 *
 * This error is raised when we cannot retrieve pricing information needed to
 * estimate the cost of a request. When this occurs, the request should be
 * rejected rather than proxied, as we cannot lock sufficient funds without
 * a cost estimate.
 *
 * @example
 * ```ts
 * const estimate = yield* estimateCost({ ... }).pipe(
 *   Effect.catchTag("PricingUnavailableError", (error) => {
 *     console.error("Cannot estimate cost:", error.message);
 *     return Effect.fail(new HandlerError({ message: "Pricing unavailable" }));
 *   })
 * );
 * ```
 */
export class PricingUnavailableError extends Schema.TaggedError<PricingUnavailableError>()(
  "PricingUnavailableError",
  {
    message: Schema.String,
    provider: Schema.optional(Schema.String),
    model: Schema.optional(Schema.String),
  },
) {
  static readonly status = 503 as const;
}

/**
 * Error that occurs when a plan limit has been exceeded.
 *
 * This error is raised when an organization attempts to exceed the limits
 * of their current plan (e.g., seats, projects, spans). The error includes
 * information about the limit type, current usage, and upgrade path.
 *
 * The HTTP status code is 402 (Payment Required) to indicate that the user
 * needs to upgrade their plan to continue.
 *
 * @example
 * ```ts
 * yield* checkSeatLimit({ organizationId }).pipe(
 *   Effect.catchTag("PlanLimitExceededError", (error) => {
 *     console.error(`${error.limitType} limit exceeded:`, error.message);
 *     return Effect.fail(new HandlerError({ message: "Upgrade required" }));
 *   })
 * );
 * ```
 */
export class PlanLimitExceededError extends Schema.TaggedError<PlanLimitExceededError>()(
  "PlanLimitExceededError",
  {
    message: Schema.String,
    resource: Schema.String,
    limitType: Schema.String, // "seats", "projects", "spans"
    currentUsage: Schema.Number,
    limit: Schema.Number,
    planTier: Schema.String,
  },
) {
  static readonly status = 402 as const;
}

/**
 * Error that occurs when an organization exceeds their rate limit.
 *
 * This error is raised when an organization makes too many API requests
 * within the time window defined by their plan tier. Rate limits are
 * enforced per-organization across all API keys and users.
 *
 * The HTTP status code is 429 (Too Many Requests) - the standard status
 * for rate limiting. The response includes X-RateLimit-* headers to help
 * clients implement exponential backoff.
 *
 * @example
 * ```ts
 * yield* rateLimiter.checkRateLimit({ organizationId, planTier }).pipe(
 *   Effect.catchTag("RateLimitError", (error) => {
 *     console.error(`Rate limit exceeded:`, error.message);
 *     return Effect.fail(error); // Propagate with 429 status
 *   })
 * );
 * ```
 */
export class RateLimitError extends Schema.TaggedError<RateLimitError>()(
  "RateLimitError",
  {
    message: Schema.String,
    organizationId: Schema.String,
    limit: Schema.Number,
    retryAfter: Schema.Number, // seconds until rate limit resets
    planTier: Schema.String,
  },
) {
  static readonly status = 429 as const;
}

/**
 * ServiceUnavailableError indicates a downstream service is temporarily unavailable.
 *
 * Maps to HTTP 503 Service Unavailable.
 *
 * @example
 * ```ts
 * new ServiceUnavailableError({
 *   message: "Rate limiter service unavailable",
 *   service: "cloudflare-rate-limiter"
 * })
 * ```
 */
export class ServiceUnavailableError extends Schema.TaggedError<ServiceUnavailableError>()(
  "ServiceUnavailableError",
  {
    message: Schema.String,
    service: Schema.optional(Schema.String),
  },
) {
  static readonly status = 503 as const;
}
