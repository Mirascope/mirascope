import { Effect, Option } from "effect";
import type { ApiKeyInfo } from "@/db/schema";
import { UnauthorizedError } from "@/errors";
import { AuthenticatedApiKey } from "@/auth/context";

/**
 * Header name for API key authentication
 */
export const API_KEY_HEADER = "X-API-Key";

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
 * Require API key authentication from context.
 * Fails with UnauthorizedError if not present.
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
