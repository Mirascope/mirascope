import { Effect } from "effect";
import { DatabaseService } from "@/db";
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

export const listApiKeysHandler = (environmentId: string) =>
  Effect.gen(function* () {
    const db = yield* DatabaseService;
    const user = yield* AuthenticatedUser;
    const apiKeys = yield* db.apiKeys.findByEnvironment(environmentId, user.id);
    return apiKeys.map(toApiKey);
  });

export const createApiKeyHandler = (
  environmentId: string,
  payload: CreateApiKeyRequest,
) =>
  Effect.gen(function* () {
    const db = yield* DatabaseService;
    const user = yield* AuthenticatedUser;
    const apiKey = yield* db.apiKeys.create(
      { name: payload.name, environmentId },
      user.id,
    );
    return toApiKeyCreateResponse(apiKey);
  });

export const getApiKeyHandler = (apiKeyId: string) =>
  Effect.gen(function* () {
    const db = yield* DatabaseService;
    const user = yield* AuthenticatedUser;
    const apiKey = yield* db.apiKeys.findById(apiKeyId, user.id);
    return toApiKey(apiKey);
  });

export const deleteApiKeyHandler = (apiKeyId: string) =>
  Effect.gen(function* () {
    const db = yield* DatabaseService;
    const user = yield* AuthenticatedUser;
    yield* db.apiKeys.delete(apiKeyId, user.id);
  });
