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

/**
 * Factory function to create a TaggedError class that serializes with `tag` instead of `_tag`.
 * This is needed because Fern SDK expects `tag` but Effect uses `_tag`.
 */
function TaggedHttpError<Self>() {
  return <Tag extends string, Fields extends Schema.Struct.Fields>(
    tag: Tag,
    fields: Fields,
  ) => {
    const Base = Schema.TaggedError<Self>()(tag, fields);
    const fieldKeys = Object.keys(fields) as (keyof Fields)[];
    return class extends Base {
      toJSON() {
        const result: Record<string, unknown> = { tag: this._tag };
        for (const key of fieldKeys) {
          result[key as string] = (this as unknown as Record<string, unknown>)[
            key as string
          ];
        }
        return result;
      }
    };
  };
}

export class NotFoundError extends TaggedHttpError<NotFoundError>()(
  "NotFoundError",
  {
    message: Schema.String,
    resource: Schema.optional(Schema.String),
  },
) {
  static readonly status = 404 as const;
}

export class DatabaseError extends TaggedHttpError<DatabaseError>()(
  "DatabaseError",
  {
    message: Schema.String,
    cause: Schema.optional(Schema.Unknown),
  },
) {
  static readonly status = 500 as const;
}

export class InvalidSessionError extends TaggedHttpError<InvalidSessionError>()(
  "InvalidSessionError",
  {
    message: Schema.String,
    sessionId: Schema.optional(Schema.String),
  },
) {
  static readonly status = 401 as const;
}

export class AlreadyExistsError extends TaggedHttpError<AlreadyExistsError>()(
  "AlreadyExistsError",
  {
    message: Schema.String,
    resource: Schema.optional(Schema.String),
  },
) {
  static readonly status = 409 as const;
}

export class PermissionDeniedError extends TaggedHttpError<PermissionDeniedError>()(
  "PermissionDeniedError",
  {
    message: Schema.String,
    resource: Schema.optional(Schema.String),
  },
) {
  static readonly status = 403 as const;
}

export class UnauthorizedError extends TaggedHttpError<UnauthorizedError>()(
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
