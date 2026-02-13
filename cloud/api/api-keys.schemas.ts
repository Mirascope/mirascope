import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";

import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/errors";

// Base schema for API key (without the actual key)
export const ApiKeySchema = Schema.Struct({
  id: Schema.String,
  name: Schema.String,
  keyPrefix: Schema.String,
  environmentId: Schema.String,
  ownerId: Schema.String,
  createdAt: Schema.NullOr(Schema.String),
  lastUsedAt: Schema.NullOr(Schema.String),
});

// Schema for create response (includes the plaintext key)
export const ApiKeyCreateResponseSchema = Schema.Struct({
  id: Schema.String,
  name: Schema.String,
  keyPrefix: Schema.String,
  environmentId: Schema.String,
  ownerId: Schema.String,
  createdAt: Schema.NullOr(Schema.String),
  lastUsedAt: Schema.NullOr(Schema.String),
  key: Schema.String,
});

// Schema for API key with display context.
// Environment-scoped keys have environmentId/projectId/projectName/environmentName set.
// Org-scoped keys have organizationId/organizationName set and environmentId null.
export const ApiKeyWithContextSchema = Schema.Struct({
  id: Schema.String,
  name: Schema.String,
  keyPrefix: Schema.String,
  environmentId: Schema.NullOr(Schema.String),
  ownerId: Schema.String,
  createdAt: Schema.NullOr(Schema.String),
  lastUsedAt: Schema.NullOr(Schema.String),
  // Environment-scoped fields (null for org-scoped keys)
  projectId: Schema.optional(Schema.String),
  projectName: Schema.optional(Schema.String),
  environmentName: Schema.optional(Schema.String),
  // Org-scoped fields (null for environment-scoped keys)
  organizationId: Schema.optional(Schema.String),
  organizationName: Schema.optional(Schema.String),
  // Owner context
  ownerName: Schema.NullOr(Schema.String),
  ownerAccountType: Schema.Literal("user", "claw"),
});

// API key name must be 1-100 characters
const ApiKeyNameSchema = Schema.String.pipe(
  Schema.minLength(1, { message: () => "API key name is required" }),
  Schema.maxLength(100, {
    message: () => "API key name must be at most 100 characters",
  }),
);

export const CreateApiKeyRequestSchema = Schema.Struct({
  name: ApiKeyNameSchema,
});

export type ApiKey = typeof ApiKeySchema.Type;
export type ApiKeyCreateResponse = typeof ApiKeyCreateResponseSchema.Type;
export type ApiKeyWithContext = typeof ApiKeyWithContextSchema.Type;
export type CreateApiKeyRequest = typeof CreateApiKeyRequestSchema.Type;

// Path for listing all API keys in an organization
const orgApiKeysPath = "/organizations/:organizationId/api-keys";

const OrgPathParams = Schema.Struct({
  organizationId: Schema.String,
});

const basePath =
  "/organizations/:organizationId/projects/:projectId/environments/:environmentId/api-keys";
const itemPath = `${basePath}/:apiKeyId`;

const BasePathParams = Schema.Struct({
  organizationId: Schema.String,
  projectId: Schema.String,
  environmentId: Schema.String,
});

const ItemPathParams = Schema.Struct({
  organizationId: Schema.String,
  projectId: Schema.String,
  environmentId: Schema.String,
  apiKeyId: Schema.String,
});

export class ApiKeysApi extends HttpApiGroup.make("apiKeys")
  .add(
    HttpApiEndpoint.get("listAllForOrg", orgApiKeysPath)
      .setPath(OrgPathParams)
      .addSuccess(Schema.Array(ApiKeyWithContextSchema))
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get("list", basePath)
      .setPath(BasePathParams)
      .addSuccess(Schema.Array(ApiKeySchema))
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.post("create", basePath)
      .setPath(BasePathParams)
      .setPayload(CreateApiKeyRequestSchema)
      .addSuccess(ApiKeyCreateResponseSchema)
      .addError(AlreadyExistsError, { status: AlreadyExistsError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get("get", itemPath)
      .setPath(ItemPathParams)
      .addSuccess(ApiKeySchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.del("delete", itemPath)
      .setPath(ItemPathParams)
      .addSuccess(Schema.Void)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  ) {}
