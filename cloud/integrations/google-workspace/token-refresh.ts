import { eq } from "drizzle-orm";
import { Data, Effect } from "effect";

import { decryptSecrets } from "@/claws/crypto";
import { DrizzleORM } from "@/db/client";
import { googleWorkspaceConnections } from "@/db/schema";
import { Settings } from "@/settings";

export class TokenNotFoundError extends Data.TaggedError("TokenNotFoundError")<{
  readonly message: string;
  readonly clawId: string;
}> {}

export class TokenRefreshError extends Data.TaggedError("TokenRefreshError")<{
  readonly message: string;
  readonly cause?: unknown;
}> {}

export class TokenDecryptionError extends Data.TaggedError(
  "TokenDecryptionError",
)<{
  readonly message: string;
  readonly cause?: unknown;
}> {}

/**
 * Refreshes the Google Workspace access token for a given claw.
 *
 * Reads the encrypted refresh token from the database, decrypts it,
 * and exchanges it for a fresh access token via Google's token endpoint.
 */
export function refreshAccessToken(
  clawId: string,
): Effect.Effect<
  { accessToken: string; expiresIn: number },
  TokenNotFoundError | TokenDecryptionError | TokenRefreshError,
  DrizzleORM | Settings
> {
  return Effect.gen(function* () {
    const settings = yield* Settings;
    const client = yield* DrizzleORM;

    // Validate Google Workspace credentials are configured
    if (
      !settings.googleWorkspace.clientId ||
      !settings.googleWorkspace.clientSecret
    ) {
      return yield* Effect.fail(
        new TokenRefreshError({
          message: "Google Workspace OAuth is not configured",
        }),
      );
    }

    // Look up the connection
    const [connection] = yield* client
      .select({
        encryptedRefreshToken: googleWorkspaceConnections.encryptedRefreshToken,
        refreshTokenKeyId: googleWorkspaceConnections.refreshTokenKeyId,
      })
      .from(googleWorkspaceConnections)
      .where(eq(googleWorkspaceConnections.clawId, clawId))
      .limit(1)
      .pipe(
        Effect.mapError(
          () =>
            new TokenNotFoundError({
              message: "Failed to query connection",
              clawId,
            }),
        ),
      );

    if (!connection) {
      return yield* Effect.fail(
        new TokenNotFoundError({
          message: "No Google Workspace connection found for this claw",
          clawId,
        }),
      );
    }

    // Decrypt the refresh token
    const secrets = yield* decryptSecrets(
      connection.encryptedRefreshToken,
      connection.refreshTokenKeyId,
    ).pipe(
      Effect.mapError(
        (e) =>
          new TokenDecryptionError({
            message: `Failed to decrypt refresh token: ${e.message}`,
            cause: e,
          }),
      ),
    );

    if (!secrets.refresh_token) {
      return yield* Effect.fail(
        new TokenNotFoundError({
          message: "Decrypted secrets do not contain a refresh token",
          clawId,
        }),
      );
    }

    // Exchange refresh token for a new access token
    const tokenResponse = yield* Effect.tryPromise({
      try: async () => {
        const response = await fetch("https://oauth2.googleapis.com/token", {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams({
            grant_type: "refresh_token",
            client_id: settings.googleWorkspace.clientId!,
            client_secret: settings.googleWorkspace.clientSecret!,
            refresh_token: secrets.refresh_token!,
          }),
        });
        return (await response.json()) as {
          access_token?: string;
          expires_in?: number;
          error?: string;
          error_description?: string;
        };
      },
      catch: (e) =>
        new TokenRefreshError({
          message: "Failed to call Google token endpoint",
          cause: e,
        }),
    });

    if (tokenResponse.error || !tokenResponse.access_token) {
      return yield* Effect.fail(
        new TokenRefreshError({
          message: `Token refresh failed: ${tokenResponse.error_description || tokenResponse.error || "No access token"}`,
        }),
      );
    }

    // Update token expiry in DB
    const expiresIn = tokenResponse.expires_in || 3600;
    yield* client
      .update(googleWorkspaceConnections)
      .set({
        tokenExpiresAt: new Date(Date.now() + expiresIn * 1000),
        updatedAt: new Date(),
      })
      .where(eq(googleWorkspaceConnections.clawId, clawId))
      .pipe(
        Effect.mapError(
          () =>
            new TokenRefreshError({
              message: "Failed to update token expiry in database",
            }),
        ),
      );

    return {
      accessToken: tokenResponse.access_token,
      expiresIn,
    };
  });
}
