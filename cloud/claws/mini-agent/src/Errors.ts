/**
 * Tagged errors for the Mini Agent.
 * Uses Schema.TaggedError so they can be used in HttpApi error schemas.
 */
import { Schema } from "effect";

export class ExecError extends Schema.TaggedError<ExecError>()(
  "ExecError",
  {
    message: Schema.String,
    command: Schema.String,
    exitCode: Schema.Number,
    stderr: Schema.String,
  },
) {}

export class ProvisioningError extends Schema.TaggedError<ProvisioningError>()(
  "ProvisioningError",
  {
    message: Schema.String,
    step: Schema.String,
  },
) {}

export class NotFoundError extends Schema.TaggedError<NotFoundError>()(
  "NotFoundError",
  {
    message: Schema.String,
  },
) {}

export class CapacityError extends Schema.TaggedError<CapacityError>()(
  "CapacityError",
  {
    message: Schema.String,
    current: Schema.Number,
    max: Schema.Number,
  },
) {}

export class ValidationError extends Schema.TaggedError<ValidationError>()(
  "ValidationError",
  {
    message: Schema.String,
  },
) {}

export class AuthError extends Schema.TaggedError<AuthError>()(
  "AuthError",
  {
    message: Schema.String,
  },
) {}

export class InternalError extends Schema.TaggedError<InternalError>()(
  "InternalError",
  {
    message: Schema.String,
  },
) {}
