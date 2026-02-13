/**
 * @fileoverview Shared error types for the Mirascope SDK.
 *
 * All errors are Schema.TaggedError for type-safe discrimination
 * and consistent HTTP status mapping.
 */

import { Schema } from "effect";

export class ApiError extends Schema.TaggedError<ApiError>()("ApiError", {
  message: Schema.String,
  status: Schema.Number,
}) {}

export class NotFoundError extends Schema.TaggedError<NotFoundError>()(
  "NotFoundError",
  {
    message: Schema.String,
    resource: Schema.String,
    id: Schema.String,
  },
) {}

export class AuthError extends Schema.TaggedError<AuthError>()("AuthError", {
  message: Schema.String,
}) {}

export class ValidationError extends Schema.TaggedError<ValidationError>()(
  "ValidationError",
  {
    message: Schema.String,
    field: Schema.optional(Schema.String),
  },
) {}
