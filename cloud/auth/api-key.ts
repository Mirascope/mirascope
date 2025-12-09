import { Effect } from "effect";
import { DatabaseService } from "@/db";
import { NotFoundError, DatabaseError } from "@/db/errors";
import type { PublicUser } from "@/db/schema";

/**
 * Information about an authenticated API key
 */
export type ApiKeyInfo = {
  apiKeyId: string;
  environmentId: string;
};

/**
 * Header name for API key authentication
 */
export const API_KEY_HEADER = "X-API-Key";

/**
 * Extract API key from request headers
 */
export function getApiKeyFromRequest(request: Request): string | null {
  // Check X-API-Key header first
  const apiKeyHeader = request.headers.get(API_KEY_HEADER);
  if (apiKeyHeader) {
    return apiKeyHeader;
  }

  // Check Authorization header with Bearer scheme
  const authHeader = request.headers.get("Authorization");
  if (authHeader?.startsWith("Bearer ")) {
    return authHeader.slice(7);
  }

  return null;
}

/**
 * Authenticate a request using an API key
 * Returns the API key info if valid, null if no API key provided, or fails with NotFoundError if invalid
 */
export const authenticateWithApiKey = (
  request: Request,
): Effect.Effect<
  ApiKeyInfo | null,
  NotFoundError | DatabaseError,
  DatabaseService
> =>
  Effect.gen(function* () {
    const apiKey = getApiKeyFromRequest(request);
    if (!apiKey) {
      return null;
    }

    const db = yield* DatabaseService;
    return yield* db.apiKeys.verifyApiKey(apiKey);
  });

/**
 * Result of API key authentication including user context
 */
export type ApiKeyAuthResult = {
  apiKeyInfo: ApiKeyInfo;
  user: PublicUser;
};

/**
 * Authenticate with API key and resolve to a user with access
 * Returns null if no API key provided, fails with error if invalid
 */
export const authenticateApiKeyWithUser = (
  request: Request,
): Effect.Effect<
  ApiKeyAuthResult | null,
  NotFoundError | DatabaseError,
  DatabaseService
> =>
  Effect.gen(function* () {
    const apiKey = getApiKeyFromRequest(request);
    if (!apiKey) {
      return null;
    }

    const db = yield* DatabaseService;
    const apiKeyInfo = yield* db.apiKeys.verifyApiKey(apiKey);

    // Get a user with access to this environment's organization
    const user = yield* db.apiKeys.getUserForEnvironment(
      apiKeyInfo.environmentId,
    );

    return { apiKeyInfo, user };
  });
