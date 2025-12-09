import { Effect, Option } from "effect";
import { Database } from "@/db";
import type { ApiKeyInfo } from "@/db/schema";
import { DatabaseError, NotFoundError, UnauthorizedError } from "@/errors";
import { AuthenticatedApiKey } from "@/auth/context";

/**
 * Header name for API key authentication
 */
export const API_KEY_HEADER = "X-API-Key";

// Re-export ApiKeyInfo for convenience
export type { ApiKeyInfo } from "@/db/schema";

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
 * Authenticate a request using an API key.
 *
 * Extracts the API key from the request headers (X-API-Key or Bearer token)
 * and validates it against the database.
 *
 * @param request - The incoming HTTP request
 * @returns ApiKeyInfo if valid, null if no key provided
 * @throws NotFoundError - If the API key is invalid
 * @throws DatabaseError - If the database operation fails
 */
export function authenticateWithApiKey(
  request: Request,
): Effect.Effect<ApiKeyInfo | null, NotFoundError | DatabaseError, Database> {
  return Effect.gen(function* () {
    const key = getApiKeyFromRequest(request);
    if (!key) {
      return null;
    }

    const db = yield* Database;
    const apiKeyInfo =
      yield* db.organizations.projects.environments.apiKeys.getApiKeyInfo(key);

    return apiKeyInfo;
  });
}

/**
 * Require API key authentication from context.
 *
 * This checks if AuthenticatedApiKey context is available (set by api.v0 handler)
 * and returns the API key info. If not present, fails with UnauthorizedError.
 *
 * Use this in handlers that require API key authentication:
 *
 * @example
 * ```ts
 * export const myHandler = Effect.gen(function* () {
 *   const apiKeyInfo = yield* requireApiKeyAuth;
 *   // apiKeyInfo.environmentId, apiKeyInfo.ownerId, etc.
 *   // ... handler logic
 * });
 * ```
 */
export const requireApiKeyAuth: Effect.Effect<ApiKeyInfo, UnauthorizedError> =
  Effect.gen(function* () {
    const maybeApiKeyInfo = yield* Effect.serviceOption(AuthenticatedApiKey);
    if (Option.isNone(maybeApiKeyInfo)) {
      return yield* Effect.fail(
        new UnauthorizedError({
          message:
            "API key required. Provide X-API-Key header or Bearer token.",
        }),
      );
    }
    return maybeApiKeyInfo.value;
  });
