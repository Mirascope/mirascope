import { Schema } from "effect";

/**
 * Domain errors using Schema.TaggedError with HTTP status codes.
 *
 * Each error class has a static `status` property that maps to the appropriate
 * HTTP status code. Use with HttpApiEndpoint.addError():
 *
 * @example
 * HttpApiEndpoint.get("get", "/resource/:id")
 *   .addError(NotFoundError, { status: NotFoundError.status })
 */

export class DatabaseError extends Schema.TaggedError<DatabaseError>()(
  "DatabaseError",
  {
    message: Schema.String,
    cause: Schema.optional(Schema.Unknown),
  },
) {
  static readonly status = 500 as const;
}
export class NotFoundError extends Schema.TaggedError<NotFoundError>()(
  "NotFoundError",
  {
    message: Schema.String,
    resource: Schema.optional(Schema.String),
  },
) {
  static readonly status = 404 as const;
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

export class InvalidSessionError extends Schema.TaggedError<InvalidSessionError>()(
  "InvalidSessionError",
  {
    message: Schema.String,
    sessionId: Schema.optional(Schema.String),
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

export class PermissionDeniedError extends Schema.TaggedError<PermissionDeniedError>()(
  "PermissionDeniedError",
  {
    message: Schema.String,
    resource: Schema.optional(Schema.String),
  },
) {
  static readonly status = 403 as const;
}

export class UnauthorizedError extends Schema.TaggedError<UnauthorizedError>()(
  "UnauthorizedError",
  {
    message: Schema.String,
  },
) {
  static readonly status = 401 as const;
}

/**
 * Type for any error class with a status property.
 * Useful for generic error handling.
 */
export type HttpError =
  | typeof NotFoundError
  | typeof DatabaseError
  | typeof InvalidSessionError
  | typeof AlreadyExistsError
  | typeof PermissionDeniedError
  | typeof UnauthorizedError;
