import { Context, Effect } from "effect";

import type {
  PublicUser,
  ApiKeyAuth,
  EnvironmentApiKeyAuth,
  OrgApiKeyAuth,
} from "@/db/schema";

import { UnauthorizedError } from "@/errors";

/** Auth result including optional API key info. */
export type AuthResult = {
  user: PublicUser;
  apiKeyInfo?: ApiKeyAuth;
};

/** Make specific fields of T required. */
export type RequireField<T, K extends keyof T> = Omit<T, K> &
  Required<Pick<T, K>>;

/** AuthResult with required apiKeyInfo. */
export type ApiKeyAuthResult = RequireField<AuthResult, "apiKeyInfo">;

/** AuthResult with required environment-scoped apiKeyInfo. */
export type EnvironmentApiKeyAuthResult = Omit<AuthResult, "apiKeyInfo"> & {
  apiKeyInfo: EnvironmentApiKeyAuth;
};

/** AuthResult with required org-scoped apiKeyInfo. */
export type OrgApiKeyAuthResult = Omit<AuthResult, "apiKeyInfo"> & {
  apiKeyInfo: OrgApiKeyAuth;
};

/**
 * Context that provides the authenticated user for the current request.
 * This is set by the request handler and required by authenticated endpoints.
 */
export class AuthenticatedUser extends Context.Tag("AuthenticatedUser")<
  AuthenticatedUser,
  PublicUser
>() {}

/**
 * Context that provides authentication result for the current request.
 * Contains the authenticated user and optional API key info.
 */
export class Authentication extends Context.Tag("Authentication")<
  Authentication,
  AuthResult
>() {
  /**
   * Require API key authentication.
   * Fails with UnauthorizedError if apiKeyInfo is not present.
   */
  static readonly ApiKey: Effect.Effect<
    ApiKeyAuthResult,
    UnauthorizedError,
    Authentication
  > = Effect.gen(function* () {
    const auth = yield* Authentication;
    if (!auth.apiKeyInfo) {
      return yield* Effect.fail(
        new UnauthorizedError({
          message:
            "API key required. Provide X-API-Key header or Bearer token.",
        }),
      );
    }
    return auth as ApiKeyAuthResult;
  });

  /**
   * Require environment-scoped API key authentication.
   * Narrows the union to EnvironmentApiKeyAuth via environmentId check.
   */
  static readonly EnvironmentApiKey: Effect.Effect<
    EnvironmentApiKeyAuthResult,
    UnauthorizedError,
    Authentication
  > = Effect.gen(function* () {
    const auth = yield* Authentication.ApiKey;
    if (auth.apiKeyInfo.environmentId === null) {
      return yield* Effect.fail(
        new UnauthorizedError({
          message:
            "Environment-scoped API key required. This org-scoped key cannot access environment resources.",
        }),
      );
    }
    return auth as EnvironmentApiKeyAuthResult;
  });

  /**
   * Require org-scoped API key authentication.
   * Narrows the union to OrgApiKeyAuth via environmentId check.
   */
  static readonly OrgApiKey: Effect.Effect<
    OrgApiKeyAuthResult,
    UnauthorizedError,
    Authentication
  > = Effect.gen(function* () {
    const auth = yield* Authentication.ApiKey;
    if (auth.apiKeyInfo.environmentId !== null) {
      return yield* Effect.fail(
        new UnauthorizedError({
          message:
            "Org-scoped API key required. This environment-scoped key cannot access org-level resources.",
        }),
      );
    }
    return auth as OrgApiKeyAuthResult;
  });
}
