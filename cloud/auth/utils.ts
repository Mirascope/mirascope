import { Effect } from "effect";

import type { AuthResult } from "@/auth/context";
import type { ApiKeyInfo } from "@/db/schema";
import type { SettingsConfig } from "@/settings";

import { getApiKeyFromRequest } from "@/auth/api-key";
import { Database } from "@/db/database";
import { UnauthorizedError } from "@/errors";

export function getCookieDomain(settings: SettingsConfig): string | null {
  try {
    const url = new URL(settings.siteUrl);
    const hostname = url.hostname;
    // localhost or IP addresses don't get a domain attribute
    if (hostname === "localhost" || /^\d+\.\d+\.\d+\.\d+$/.test(hostname)) {
      return null;
    }
    // Prefix with dot for subdomain coverage
    // e.g., staging.mirascope.com → .staging.mirascope.com
    // e.g., mirascope.com → .mirascope.com
    return `.${hostname}`;
  } catch {
    return null;
  }
}

export function isSecure(settings: SettingsConfig): boolean {
  return (
    settings.env === "production" || settings.siteUrl.startsWith("https://")
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

export function setSessionCookie(
  sessionId: string,
  settings: SettingsConfig,
): string {
  const maxAge = 7 * 24 * 60 * 60; // 7 days in seconds

  const domain = getCookieDomain(settings);
  const cookieParts = [
    `session=${sessionId}`,
    "HttpOnly",
    ...(isSecure(settings) ? ["Secure"] : []),
    "SameSite=Lax",
    `Max-Age=${maxAge}`,
    "Path=/",
    ...(domain ? [`Domain=${domain}`] : []),
  ];

  return cookieParts.join("; ");
}

export function clearSessionCookie(settings: SettingsConfig): string {
  const domain = getCookieDomain(settings);
  const cookieParts = [
    "session=;",
    "Expires=Thu, 01 Jan 1970 00:00:00 GMT",
    "HttpOnly",
    ...(isSecure(settings) ? ["Secure"] : []),
    "SameSite=Lax",
    "Path=/",
    ...(domain ? [`Domain=${domain}`] : []),
  ];

  return cookieParts.join("; ");
}

export function setOAuthStateCookie(
  state: string,
  settings: SettingsConfig,
): string {
  const cookieParts = [
    `oauth_state=${state}`,
    "HttpOnly",
    ...(isSecure(settings) ? ["Secure"] : []),
    "SameSite=Lax",
    "Max-Age=600", // 10 minutes
    "Path=/",
  ];

  return cookieParts.join("; ");
}

export function clearOAuthStateCookie(settings: SettingsConfig): string {
  const cookieParts = [
    "oauth_state=;",
    "Expires=Thu, 01 Jan 1970 00:00:00 GMT",
    "HttpOnly",
    ...(isSecure(settings) ? ["Secure"] : []),
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
      // Org-scoped keys can access any resource within their org
      const isOrgScoped =
        apiKeyInfo.environmentId === null && apiKeyInfo.projectId === null;

      // Validate organizationId if provided (applies to both scopes)
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

      // Environment-scoped keys must also match project and environment
      if (!isOrgScoped) {
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
      }
    }

    return apiKeyInfo;
  });

/** Authenticate with API key or session and return user + optional ApiKeyInfo. */
export const authenticate = (
  request: Request,
  pathParams?: PathParameters,
): Effect.Effect<AuthResult, UnauthorizedError, Database> =>
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
        user: {
          id: apiKeyInfo.ownerId,
          email: apiKeyInfo.ownerEmail,
          name: apiKeyInfo.ownerName,
          accountType: apiKeyInfo.ownerAccountType,
          deletedAt: apiKeyInfo.ownerDeletedAt,
        },
        apiKeyInfo,
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

    const user = yield* db.sessions.findUserBySessionId(sessionId).pipe(
      Effect.catchAll(() =>
        Effect.fail(
          new UnauthorizedError({
            message: "Invalid session",
          }),
        ),
      ),
    );

    return { user };
  });
