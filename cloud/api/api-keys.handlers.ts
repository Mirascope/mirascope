import { Effect } from "effect";
import { Database } from "@/db";
import { AuthenticatedUser } from "@/auth";
import type { CreateApiKeyRequest } from "@/api/api-keys.schemas";
import type { PublicApiKey, ApiKeyCreateResponse } from "@/db/schema";

export * from "@/api/api-keys.schemas";

// Helper to convert Date to ISO string for API response
export const toApiKey = (apiKey: PublicApiKey) => ({
  ...apiKey,
  createdAt: apiKey.createdAt?.toISOString() ?? null,
  lastUsedAt: apiKey.lastUsedAt?.toISOString() ?? null,
});

export const toApiKeyCreateResponse = (apiKey: ApiKeyCreateResponse) => ({
  ...apiKey,
  createdAt: apiKey.createdAt?.toISOString() ?? null,
  lastUsedAt: apiKey.lastUsedAt?.toISOString() ?? null,
});

export const listApiKeysHandler = (
  organizationId: string,
  projectId: string,
  environmentId: string,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const apiKeys =
      yield* db.organizations.projects.environments.apiKeys.findAll({
        userId: user.id,
        organizationId,
        projectId,
        environmentId,
      });
    return apiKeys.map(toApiKey);
  });

export const createApiKeyHandler = (
  organizationId: string,
  projectId: string,
  environmentId: string,
  payload: CreateApiKeyRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const apiKey = yield* db.organizations.projects.environments.apiKeys.create(
      {
        userId: user.id,
        organizationId,
        projectId,
        environmentId,
        data: { name: payload.name },
      },
    );
    return toApiKeyCreateResponse(apiKey);
  });

export const getApiKeyHandler = (
  organizationId: string,
  projectId: string,
  environmentId: string,
  apiKeyId: string,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const apiKey =
      yield* db.organizations.projects.environments.apiKeys.findById({
        userId: user.id,
        organizationId,
        projectId,
        environmentId,
        apiKeyId,
      });
    return toApiKey(apiKey);
  });

export const deleteApiKeyHandler = (
  organizationId: string,
  projectId: string,
  environmentId: string,
  apiKeyId: string,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    yield* db.organizations.projects.environments.apiKeys.delete({
      userId: user.id,
      organizationId,
      projectId,
      environmentId,
      apiKeyId,
    });
  });
