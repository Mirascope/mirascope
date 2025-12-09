import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/db/errors";

// Base schema for API key (without the actual key)
export const ApiKeySchema = Schema.Struct({
  id: Schema.String,
  name: Schema.String,
  keyPrefix: Schema.String,
  environmentId: Schema.String,
  createdAt: Schema.NullOr(Schema.String),
  lastUsedAt: Schema.NullOr(Schema.String),
});

// Schema for create response (includes the plaintext key)
export const ApiKeyCreateResponseSchema = Schema.Struct({
  id: Schema.String,
  name: Schema.String,
  keyPrefix: Schema.String,
  environmentId: Schema.String,
  createdAt: Schema.NullOr(Schema.String),
  lastUsedAt: Schema.NullOr(Schema.String),
  key: Schema.String,
});

export const CreateApiKeyRequestSchema = Schema.Struct({
  name: Schema.String,
});

export type ApiKey = typeof ApiKeySchema.Type;
export type ApiKeyCreateResponse = typeof ApiKeyCreateResponseSchema.Type;
export type CreateApiKeyRequest = typeof CreateApiKeyRequestSchema.Type;

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
    HttpApiEndpoint.get("list", basePath)
      .setPath(BasePathParams)
      .addSuccess(Schema.Array(ApiKeySchema))
      .addError(PermissionDeniedError)
      .addError(DatabaseError),
  )
  .add(
    HttpApiEndpoint.post("create", basePath)
      .setPath(BasePathParams)
      .setPayload(CreateApiKeyRequestSchema)
      .addSuccess(ApiKeyCreateResponseSchema)
      .addError(AlreadyExistsError)
      .addError(PermissionDeniedError)
      .addError(DatabaseError),
  )
  .add(
    HttpApiEndpoint.get("get", itemPath)
      .setPath(ItemPathParams)
      .addSuccess(ApiKeySchema)
      .addError(NotFoundError)
      .addError(PermissionDeniedError)
      .addError(DatabaseError),
  )
  .add(
    HttpApiEndpoint.del("delete", itemPath)
      .setPath(ItemPathParams)
      .addSuccess(Schema.Void)
      .addError(NotFoundError)
      .addError(PermissionDeniedError)
      .addError(DatabaseError),
  ) {}
