import { Context, Effect } from "effect";

import type {
  PublicUser,
  ApiKeyInfo,
  EnvironmentApiKeyInfo,
  OrgApiKeyInfo,
} from "@/db/schema";

import { UnauthorizedError } from "@/errors";

/** Auth result including optional API key info. */
export type AuthResult = {
  user: PublicUser;
  apiKeyInfo?: ApiKeyInfo;
};

/** Make specific fields of T required. */
export type RequireField<T, K extends keyof T> = Omit<T, K> &
  Required<Pick<T, K>>;

/** AuthResult with required apiKeyInfo. */
export type ApiKeyAuthResult = RequireField<AuthResult, "apiKeyInfo">;

/** AuthResult with required environment-scoped apiKeyInfo. */
export type EnvironmentApiKeyAuthResult = Omit<AuthResult, "apiKeyInfo"> & {
  apiKeyInfo: EnvironmentApiKeyInfo;
};

/** AuthResult with required org-scoped apiKeyInfo. */
export type OrgApiKeyAuthResult = Omit<AuthResult, "apiKeyInfo"> & {
  apiKeyInfo: OrgApiKeyInfo;
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
   * Fails if no API key or if the key is org-scoped (no environmentId).
   */
  static readonly EnvironmentApiKey: Effect.Effect<
    EnvironmentApiKeyAuthResult,
    UnauthorizedError,
    Authentication
  > = Effect.gen(function* () {
    const auth = yield* Authentication.ApiKey;
    if (
      auth.apiKeyInfo.environmentId === null ||
      auth.apiKeyInfo.projectId === null
    ) {
      return yield* Effect.fail(
        new UnauthorizedError({
          message:
            "This endpoint requires an environment-scoped API key. Org-scoped keys cannot be used here.",
        }),
      );
    }
    return auth as EnvironmentApiKeyAuthResult;
  });

  /**
   * Require org-scoped API key authentication.
   * Fails if no API key or if the key is environment-scoped.
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
            "This endpoint requires an org-scoped API key. Environment-scoped keys cannot be used here.",
        }),
      );
    }
    return auth as OrgApiKeyAuthResult;
  });
}
