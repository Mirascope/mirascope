import { Data, Effect } from "effect";

import {
  DedicatedWorkspaceAuthError,
  MissingConfigError,
  getAccessToken,
} from "@/integrations/dedicated-workspace/auth";
import { Settings } from "@/settings";

export class DedicatedWorkspaceProvisioningError extends Data.TaggedError(
  "DedicatedWorkspaceProvisioningError",
)<{
  readonly message: string;
  readonly cause?: unknown;
}> {}

const ADMIN_API_BASE = "https://admin.googleapis.com/admin/directory/v1/users";

type AdminUser = {
  readonly id: string;
  readonly primaryEmail: string;
  readonly name: { readonly fullName: string };
  readonly suspended: boolean;
  readonly isAdmin: boolean;
  readonly creationTime: string;
};

type AdminUserListResponse = {
  readonly users?: AdminUser[];
  readonly nextPageToken?: string;
};

/**
 * Generates a random password suitable for provisioned accounts.
 */
function generatePassword(): string {
  const bytes = new Uint8Array(24);
  crypto.getRandomValues(bytes);
  return btoa(String.fromCharCode(...bytes));
}

/**
 * Helper to make an authenticated Admin SDK request.
 */
function adminRequest<T>(
  method: string,
  url: string,
  accessToken: string,
  body?: unknown,
): Effect.Effect<T, DedicatedWorkspaceProvisioningError> {
  return Effect.tryPromise({
    try: async () => {
      const init: RequestInit = {
        method,
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
      };
      if (body !== undefined) {
        init.body = JSON.stringify(body);
      }
      const response = await fetch(url, init);

      if (method === "DELETE" && response.status === 204) {
        return undefined as T;
      }

      const json = (await response.json()) as
        | T
        | { error: { message: string; code: number } };

      if (
        json !== null &&
        typeof json === "object" &&
        "error" in json &&
        json.error
      ) {
        throw new Error(
          `Admin API ${response.status}: ${(json as { error: { message: string } }).error.message}`,
        );
      }

      return json as T;
    },
    catch: (e) =>
      new DedicatedWorkspaceProvisioningError({
        message:
          e instanceof Error
            ? e.message
            : `Admin API request failed: ${method} ${url}`,
        cause: e,
      }),
  });
}

/**
 * Creates an account in the dedicated workspace for the given claw slug.
 *
 * Generates `<slug>@<domain>` and if taken, tries `<slug>-2`, `<slug>-3`, etc.
 * Returns the created email address.
 */
export function createAccount(
  clawSlug: string,
): Effect.Effect<
  { email: string; password: string },
  | MissingConfigError
  | DedicatedWorkspaceAuthError
  | DedicatedWorkspaceProvisioningError,
  Settings
> {
  return Effect.gen(function* () {
    const settings = yield* Settings;
    const { accessToken } = yield* getAccessToken();
    const domain = settings.dedicatedWorkspace.domain;

    let email = `${clawSlug}@${domain}`;
    let attempt = 1;
    const maxAttempts = 10;
    const password = generatePassword();

    while (attempt <= maxAttempts) {
      const result = yield* Effect.tryPromise({
        try: async () => {
          const response = await fetch(ADMIN_API_BASE, {
            method: "POST",
            headers: {
              Authorization: `Bearer ${accessToken}`,
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              primaryEmail: email,
              name: {
                givenName: clawSlug,
                familyName: "Claw",
              },
              password,
              changePasswordAtNextLogin: false,
            }),
          });

          const json = (await response.json()) as
            | AdminUser
            | { error: { message: string; code: number } };

          return { status: response.status, body: json };
        },
        catch: (e) =>
          new DedicatedWorkspaceProvisioningError({
            message: "Failed to create account",
            cause: e,
          }),
      });

      // 409 = entity already exists, try next suffix
      if (result.status === 409) {
        attempt++;
        email = `${clawSlug}-${attempt}@${domain}`;
        continue;
      }

      if (
        result.body !== null &&
        typeof result.body === "object" &&
        "error" in result.body &&
        result.body.error
      ) {
        return yield* Effect.fail(
          new DedicatedWorkspaceProvisioningError({
            message: `Failed to create account ${email}: ${result.body.error.message}`,
          }),
        );
      }

      return { email: (result.body as AdminUser).primaryEmail, password };
    }

    return yield* Effect.fail(
      new DedicatedWorkspaceProvisioningError({
        message: `All ${maxAttempts} email variations for slug "${clawSlug}" are taken`,
      }),
    );
  });
}

/**
 * Lists all users in the dedicated workspace domain.
 */
export function listAccounts(): Effect.Effect<
  AdminUser[],
  | MissingConfigError
  | DedicatedWorkspaceAuthError
  | DedicatedWorkspaceProvisioningError,
  Settings
> {
  return Effect.gen(function* () {
    const settings = yield* Settings;
    const { accessToken } = yield* getAccessToken();
    const domain = settings.dedicatedWorkspace.domain;

    const url = `${ADMIN_API_BASE}?domain=${domain}&maxResults=500`;
    const result = yield* adminRequest<AdminUserListResponse>(
      "GET",
      url,
      accessToken,
    );

    return result.users ?? [];
  });
}

/**
 * Gets details of a specific account by email.
 */
export function getAccount(
  email: string,
): Effect.Effect<
  AdminUser,
  | MissingConfigError
  | DedicatedWorkspaceAuthError
  | DedicatedWorkspaceProvisioningError,
  Settings
> {
  return Effect.gen(function* () {
    const { accessToken } = yield* getAccessToken();

    const url = `${ADMIN_API_BASE}/${encodeURIComponent(email)}`;
    return yield* adminRequest<AdminUser>("GET", url, accessToken);
  });
}

/**
 * Suspends a user account in the dedicated workspace.
 */
export function suspendAccount(
  email: string,
): Effect.Effect<
  AdminUser,
  | MissingConfigError
  | DedicatedWorkspaceAuthError
  | DedicatedWorkspaceProvisioningError,
  Settings
> {
  return Effect.gen(function* () {
    const { accessToken } = yield* getAccessToken();

    const url = `${ADMIN_API_BASE}/${encodeURIComponent(email)}`;
    return yield* adminRequest<AdminUser>("PUT", url, accessToken, {
      suspended: true,
    });
  });
}

/**
 * Deletes a user account from the dedicated workspace.
 */
export function deleteAccount(
  email: string,
): Effect.Effect<
  void,
  | MissingConfigError
  | DedicatedWorkspaceAuthError
  | DedicatedWorkspaceProvisioningError,
  Settings
> {
  return Effect.gen(function* () {
    const { accessToken } = yield* getAccessToken();

    const url = `${ADMIN_API_BASE}/${encodeURIComponent(email)}`;
    yield* adminRequest<void>("DELETE", url, accessToken);
  });
}
