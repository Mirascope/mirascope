import { Effect } from "effect";
import { Database } from "@/db";
import { DatabaseError, NotFoundError } from "@/errors";

/**
 * Header name for API key authentication
 */
export const API_KEY_HEADER = "X-API-Key";

/**
 * API key info returned from authentication
 */
export type ApiKeyInfo = {
  apiKeyId: string;
  environmentId: string;
  projectId: string;
  organizationId: string;
};

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
