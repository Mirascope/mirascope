import { Schema } from "effect";

// Keep in sync with error classes in @/db/errors.ts

export const NotFoundErrorSchema = Schema.Struct({
  _tag: Schema.Literal("NotFoundError"),
  message: Schema.String,
  resource: Schema.optional(Schema.String),
});

export type NotFoundError = typeof NotFoundErrorSchema.Type;

export const AlreadyExistsErrorSchema = Schema.Struct({
  _tag: Schema.Literal("AlreadyExistsError"),
  message: Schema.String,
  resource: Schema.optional(Schema.String),
});

export type AlreadyExistsError = typeof AlreadyExistsErrorSchema.Type;

export const PermissionDeniedErrorSchema = Schema.Struct({
  _tag: Schema.Literal("PermissionDeniedError"),
  message: Schema.String,
  resource: Schema.optional(Schema.String),
});

export type PermissionDeniedError = typeof PermissionDeniedErrorSchema.Type;

export const UnauthorizedErrorSchema = Schema.Struct({
  _tag: Schema.Literal("UnauthorizedError"),
  message: Schema.String,
});

export type UnauthorizedError = typeof UnauthorizedErrorSchema.Type;

export const DatabaseErrorSchema = Schema.Struct({
  _tag: Schema.Literal("DatabaseError"),
  message: Schema.String,
});

export type DatabaseError = typeof DatabaseErrorSchema.Type;

export const AuthenticatedEndpointErrors = {
  UnauthorizedErrorSchema,
  DatabaseErrorSchema,
} as const;

export const CrudEndpointErrors = {
  ...AuthenticatedEndpointErrors,
  NotFoundErrorSchema,
  AlreadyExistsErrorSchema,
  PermissionDeniedErrorSchema,
} as const;
