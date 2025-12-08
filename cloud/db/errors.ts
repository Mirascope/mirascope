import { Schema } from "effect";

/**
 * Domain errors using Schema.TaggedError.
 * These work as both:
 * - Effect errors: Effect.fail(new NotFoundError({...}))
 * - API schemas: HttpApiEndpoint.addError(NotFoundError, { status: 404 })
 */

export class NotFoundError extends Schema.TaggedError<NotFoundError>()(
  "NotFoundError",
  {
    message: Schema.String,
    resource: Schema.optional(Schema.String),
  },
) {}

export class DatabaseError extends Schema.TaggedError<DatabaseError>()(
  "DatabaseError",
  {
    message: Schema.String,
    cause: Schema.optional(Schema.Unknown),
  },
) {}

export class InvalidSessionError extends Schema.TaggedError<InvalidSessionError>()(
  "InvalidSessionError",
  {
    message: Schema.String,
    sessionId: Schema.optional(Schema.String),
  },
) {}

export class AlreadyExistsError extends Schema.TaggedError<AlreadyExistsError>()(
  "AlreadyExistsError",
  {
    message: Schema.String,
    resource: Schema.optional(Schema.String),
  },
) {}

export class PermissionDeniedError extends Schema.TaggedError<PermissionDeniedError>()(
  "PermissionDeniedError",
  {
    message: Schema.String,
    resource: Schema.optional(Schema.String),
  },
) {}

export class UnauthorizedError extends Schema.TaggedError<UnauthorizedError>()(
  "UnauthorizedError",
  {
    message: Schema.String,
  },
) {}
