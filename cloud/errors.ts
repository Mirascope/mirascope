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
