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

/** Validate an API key and optional path scope. */
export const validateApiKey = (
  apiKey: string,
  pathParams?: PathParameters,
): Effect.Effect<ApiKeyInfo, UnauthorizedError, Database> =>
  Effect.gen(function* () {
    const db = yield* Database;

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

    if (pathParams) {
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

/** Auth result including optional API key info. */
export type AuthenticationResult = {
  user: PublicUser;
  apiKeyInfo: ApiKeyInfo | null;
};

/** Authenticate with API key or session and return user + optional ApiKeyInfo. */
export const authenticate = (
  request: Request,
  pathParams?: PathParameters,
): Effect.Effect<AuthenticationResult, UnauthorizedError, Database> =>
  Effect.gen(function* () {
    const db = yield* Database;

    const apiKey = getApiKeyFromRequest(request);
    if (apiKey) {
      const apiKeyInfo = yield* validateApiKey(apiKey, pathParams);

      return {
        user: {
          id: apiKeyInfo.ownerId,
          email: apiKeyInfo.ownerEmail,
          name: apiKeyInfo.ownerName,
          deletedAt: apiKeyInfo.ownerDeletedAt,
        },
        apiKeyInfo,
      };
    }

    const sessionId = getSessionIdFromCookie(request);
    if (!sessionId) {
      return yield* Effect.fail(
        new UnauthorizedError({
          message: "Authentication required",
        }),
      );
    }

    const user = yield* db.sessions.findUserBySessionId(sessionId).pipe(
      Effect.catchAll(() =>
        Effect.fail(
          new UnauthorizedError({
            message: "Invalid session",
          }),
        ),
      ),
    );

    return { user, apiKeyInfo: null };
  });

/** Authenticate and return the user. */
export const getAuthenticatedUser = (
  request: Request,
  pathParams?: PathParameters,
): Effect.Effect<PublicUser, UnauthorizedError, Database> =>
  authenticate(request, pathParams).pipe(Effect.map((result) => result.user));
