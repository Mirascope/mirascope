import { Effect } from "effect";
import { Database } from "@/db";
import { UnauthorizedError } from "@/errors";
import type { PublicUser, ApiKeyInfo } from "@/db/schema";
import { getApiKeyFromRequest } from "@/auth/api-key";

function isSecure(): boolean {
  return (
    process.env.ENVIRONMENT === "production" ||
    (process.env.SITE_URL?.startsWith("https://") ?? false)
  );
}

function getCookieValue(request: Request, name: string): string | null {
  const cookieHeader = request.headers.get("Cookie");
  if (!cookieHeader) return null;

  const cookies = cookieHeader.split(";");
  for (const cookie of cookies) {
    const [cookieName, value] = cookie.trim().split("=");
    if (cookieName === name) {
      return value || null;
    }
  }
  return null;
}

export function getSessionIdFromCookie(request: Request): string | null {
  return getCookieValue(request, "session");
}

export function getOAuthStateFromCookie(request: Request): string | null {
  return getCookieValue(request, "oauth_state");
}

export function setSessionCookie(sessionId: string): string {
  const maxAge = 7 * 24 * 60 * 60; // 7 days in seconds

  const cookieParts = [
    `session=${sessionId}`,
    "HttpOnly",
    ...(isSecure() ? ["Secure"] : []),
    "SameSite=Lax",
    `Max-Age=${maxAge}`,
    "Path=/",
  ];

  return cookieParts.join("; ");
}

export function clearSessionCookie(): string {
  const cookieParts = [
    "session=;",
    "Expires=Thu, 01 Jan 1970 00:00:00 GMT",
    "HttpOnly",
    ...(isSecure() ? ["Secure"] : []),
    "SameSite=Lax",
    "Path=/",
  ];

  return cookieParts.join("; ");
}

export function setOAuthStateCookie(state: string): string {
  const cookieParts = [
    `oauth_state=${state}`,
    "HttpOnly",
    ...(isSecure() ? ["Secure"] : []),
    "SameSite=Lax",
    "Max-Age=600", // 10 minutes
    "Path=/",
  ];

  return cookieParts.join("; ");
}

export function clearOAuthStateCookie(): string {
  const cookieParts = [
    "oauth_state=;",
    "Expires=Thu, 01 Jan 1970 00:00:00 GMT",
    "HttpOnly",
    ...(isSecure() ? ["Secure"] : []),
    "SameSite=Lax",
    "Path=/",
  ];

  return cookieParts.join("; ");
}

export type PathParameters = {
  organizationId?: string;
  projectId?: string;
  environmentId?: string;
};

/**
 * Validates an API key against path parameters and retrieves complete API key information.
 *
 * Gets the API key info (including owner details) and ensures it has access to the specified
 * environment, project, or organization from the request path.
 *
 * @param apiKey - The API key to validate
 * @param pathParams - Optional path parameters to validate against
 * @returns Effect containing the complete API key info with owner details
 * @throws UnauthorizedError - If the API key is invalid, owner doesn't exist, or doesn't match path parameters
 */
export const validateApiKey = (
  apiKey: string,
  pathParams?: PathParameters,
): Effect.Effect<ApiKeyInfo, UnauthorizedError, Database> =>
  Effect.gen(function* () {
    const db = yield* Database;

    // Get the API key info (verifies key and ensures owner exists)
    const apiKeyInfo = yield* db.organizations.projects.environments.apiKeys
      .getApiKeyInfo(apiKey)
      .pipe(
        Effect.catchAll(() =>
          Effect.fail(
            new UnauthorizedError({
              message: "Invalid API key",
            }),
          ),
        ),
      );

    // If path parameters are provided, validate that the API key matches them
    if (pathParams) {
      // Validate environmentId if provided
      if (
        pathParams.environmentId &&
        pathParams.environmentId !== apiKeyInfo.environmentId
      ) {
        return yield* Effect.fail(
          new UnauthorizedError({
            message:
              "The environment ID in the request path does not match the environment associated with this API key",
          }),
        );
      }

      // Validate projectId if provided
      if (
        pathParams.projectId &&
        pathParams.projectId !== apiKeyInfo.projectId
      ) {
        return yield* Effect.fail(
          new UnauthorizedError({
            message:
              "The project ID in the request path does not match the project associated with this API key",
          }),
        );
      }

      // Validate organizationId if provided
      if (
        pathParams.organizationId &&
        pathParams.organizationId !== apiKeyInfo.organizationId
      ) {
        return yield* Effect.fail(
          new UnauthorizedError({
            message:
              "The organization ID in the request path does not match the organization associated with this API key",
          }),
        );
      }
    }

    return apiKeyInfo;
  });

/**
 * Gets the authenticated user from a request.
 *
 * Supports two authentication methods (checked in order):
 * 1. API Key (X-API-Key header or Authorization: Bearer)
 * 2. Session cookie
 *
 * For API keys, returns the user who owns the API key (from getApiKeyInfo).
 * For sessions, returns the user associated with the session.
 *
 * When path parameters are provided and API key authentication is used,
 * validates that the API key belongs to the specified environment/project/organization.
 * This prevents an API key from one environment being used to access another.
 *
 * @param request - The HTTP request
 * @param pathParams - Optional path parameters to validate against API key scope
 */
export const getAuthenticatedUser = (
  request: Request,
  pathParams?: PathParameters,
): Effect.Effect<PublicUser, UnauthorizedError, Database> =>
  Effect.gen(function* () {
    const db = yield* Database;

    // 1. Try API key authentication first
    const apiKey = getApiKeyFromRequest(request);
    if (apiKey) {
      // Validate the API key against path parameters and get complete info
      const apiKeyInfo = yield* validateApiKey(apiKey, pathParams);

      // Return the owner as the authenticated user
      // All owner fields come from the inner join in getApiKeyInfo
      return {
        id: apiKeyInfo.ownerId,
        email: apiKeyInfo.ownerEmail,
        name: apiKeyInfo.ownerName,
        deletedAt: apiKeyInfo.ownerDeletedAt,
      };
    }

    // 2. Fall back to session-based authentication
    const sessionId = getSessionIdFromCookie(request);
    if (!sessionId) {
      return yield* Effect.fail(
        new UnauthorizedError({
          message: "Authentication required",
        }),
      );
    }

    return yield* db.sessions.findUserBySessionId(sessionId).pipe(
      Effect.catchAll(() =>
        Effect.fail(
          new UnauthorizedError({
            message: "Invalid session",
          }),
        ),
      ),
    );
  });
