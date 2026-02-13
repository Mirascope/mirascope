import { Effect } from "effect";

import type { CreateApiKeyRequest } from "@/api/api-keys.schemas";
import type {
  EnvironmentPublicApiKey,
  EnvironmentApiKeyCreateResponse,
  ApiKeyWithContext,
} from "@/db/schema";

import { Analytics } from "@/analytics";
import { AuthenticatedUser } from "@/auth";
import { Database } from "@/db/database";

export * from "@/api/api-keys.schemas";

// Helpers to convert Date to ISO string for API responses.
// Environment-scoped helpers for env-specific endpoints.
export const toApiKey = (apiKey: EnvironmentPublicApiKey) => ({
  ...apiKey,
  createdAt: apiKey.createdAt?.toISOString() ?? null,
  lastUsedAt: apiKey.lastUsedAt?.toISOString() ?? null,
});

export const toApiKeyCreateResponse = (
  apiKey: EnvironmentApiKeyCreateResponse,
) => ({
  ...apiKey,
  createdAt: apiKey.createdAt?.toISOString() ?? null,
  lastUsedAt: apiKey.lastUsedAt?.toISOString() ?? null,
});

export const toApiKeyWithContext = (apiKey: ApiKeyWithContext) => ({
  ...apiKey,
  createdAt: apiKey.createdAt?.toISOString() ?? null,
  lastUsedAt: apiKey.lastUsedAt?.toISOString() ?? null,
});

export const listAllApiKeysHandler = (organizationId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const apiKeys =
      yield* db.organizations.projects.environments.apiKeys.findAllForOrganization(
        {
          userId: user.id,
          organizationId,
        },
      );
    return apiKeys.map(toApiKeyWithContext);
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
    const analytics = yield* Analytics;

    const apiKey = yield* db.organizations.projects.environments.apiKeys.create(
      {
        userId: user.id,
        organizationId,
        projectId,
        environmentId,
        data: { name: payload.name },
      },
    );

    yield* analytics.trackEvent({
      name: "api_key_created",
      properties: {
        apiKeyId: apiKey.id,
        organizationId,
        projectId,
        environmentId,
        userId: user.id,
      },
      distinctId: user.id,
    });

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
    const analytics = yield* Analytics;

    yield* db.organizations.projects.environments.apiKeys.delete({
      userId: user.id,
      organizationId,
      projectId,
      environmentId,
      apiKeyId,
    });

    yield* analytics.trackEvent({
      name: "api_key_deleted",
      properties: {
        apiKeyId,
        organizationId,
        projectId,
        environmentId,
        userId: user.id,
      },
      distinctId: user.id,
    });
  });
