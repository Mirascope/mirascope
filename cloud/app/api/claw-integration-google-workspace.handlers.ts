import { and, eq, isNull } from "drizzle-orm";
import { Effect } from "effect";

import {
  AuthenticationFailedError,
  InvalidStateError,
  MissingCredentialsError,
  OAuthError,
} from "@/auth/errors";
import { authenticate, getCookieValue, isSecure } from "@/auth/utils";
import { decryptSecrets, encryptSecrets } from "@/claws/crypto";
import { DrizzleORM } from "@/db/client";
import {
  claws,
  clawIntegrationGoogleWorkspace,
  organizationMemberships,
  organizations,
  users,
} from "@/db/schema";
import { signState, verifyState } from "@/integrations/google-workspace/hmac";
import { Settings } from "@/settings";

// =============================================================================
// Shared: Organization membership check
// =============================================================================

function verifyOrgMembership(
  userId: string,
  organizationId: string,
): Effect.Effect<void, OAuthError, DrizzleORM> {
  return Effect.gen(function* () {
    const client = yield* DrizzleORM;

    const [membership] = yield* client
      .select({ memberId: organizationMemberships.memberId })
      .from(organizationMemberships)
      .innerJoin(users, eq(organizationMemberships.memberId, users.id))
      .where(
        and(
          eq(organizationMemberships.memberId, userId),
          eq(organizationMemberships.organizationId, organizationId),
          isNull(users.deletedAt),
        ),
      )
      .limit(1)
      .pipe(
        Effect.mapError(
          () =>
            new OAuthError({
              message: "Failed to verify organization membership",
              provider: "google-workspace",
            }),
        ),
      );

    if (!membership) {
      return yield* Effect.fail(
        new OAuthError({
          message: "Not authorized to manage this claw's integrations",
          provider: "google-workspace",
        }),
      );
    }
  });
}

// =============================================================================
// Start OAuth handler
// =============================================================================

export function startOAuthEffect(request: Request) {
  return Effect.gen(function* () {
    const settings = yield* Settings;

    // Validate Google Workspace credentials are configured
    if (
      !settings.googleWorkspace.clientId ||
      !settings.googleWorkspace.clientSecret ||
      !settings.googleWorkspace.callbackUrl
    ) {
      return yield* Effect.fail(
        new MissingCredentialsError({
          message: "Google Workspace OAuth is not configured",
          provider: "google-workspace",
        }),
      );
    }

    // Authenticate the user
    const { user } = yield* authenticate(request).pipe(
      Effect.mapError(
        (e) =>
          new OAuthError({
            message: e.message,
            provider: "google-workspace",
          }),
      ),
    );

    // Get claw_id from query params
    const url = new URL(request.url);
    const clawId = url.searchParams.get("claw_id");
    if (!clawId) {
      return yield* Effect.fail(
        new OAuthError({
          message: "Missing claw_id parameter",
          provider: "google-workspace",
        }),
      );
    }

    // Verify claw exists
    const client = yield* DrizzleORM;
    const [claw] = yield* client
      .select({ organizationId: claws.organizationId })
      .from(claws)
      .where(eq(claws.id, clawId))
      .limit(1)
      .pipe(
        Effect.mapError(
          () =>
            new OAuthError({
              message: "Failed to look up claw",
              provider: "google-workspace",
            }),
        ),
      );

    if (!claw) {
      return yield* Effect.fail(
        new OAuthError({
          message: "Claw not found",
          provider: "google-workspace",
        }),
      );
    }

    // Verify user is a member of the claw's organization
    yield* verifyOrgMembership(user.id, claw.organizationId);

    // Generate state with CSRF token and claw_id
    const randomState = crypto.randomUUID();
    const stateData = {
      randomState,
      clawId,
      organizationId: claw.organizationId,
      userId: user.id,
    };

    // HMAC-sign the state
    const encodedState = yield* signState(stateData).pipe(
      Effect.mapError(
        (e) =>
          new OAuthError({
            message: e.message,
            provider: "google-workspace",
          }),
      ),
    );

    // Build Google OAuth URL
    const authUrl = new URL("https://accounts.google.com/o/oauth2/v2/auth");
    authUrl.searchParams.set("response_type", "code");
    authUrl.searchParams.set("client_id", settings.googleWorkspace.clientId);
    authUrl.searchParams.set(
      "redirect_uri",
      settings.googleWorkspace.callbackUrl,
    );
    authUrl.searchParams.set(
      "scope",
      [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/drive.file",
      ].join(" "),
    );
    authUrl.searchParams.set("state", encodedState);
    authUrl.searchParams.set("access_type", "offline");
    authUrl.searchParams.set("prompt", "consent");

    // Set state cookie and redirect
    const cookieParts = [
      `gw_oauth_state=${randomState}`,
      "HttpOnly",
      ...(isSecure(settings) ? ["Secure"] : []),
      "SameSite=Lax",
      "Max-Age=600",
      "Path=/",
    ];

    return new Response(null, {
      status: 302,
      headers: {
        Location: authUrl.toString(),
        "Set-Cookie": cookieParts.join("; "),
      },
    });
  });
}

// =============================================================================
// Callback OAuth handler
// =============================================================================

export function callbackOAuthEffect(request: Request) {
  return Effect.gen(function* () {
    const settings = yield* Settings;
    const siteUrl = settings.siteUrl;

    // Validate Google Workspace credentials are configured
    if (
      !settings.googleWorkspace.clientId ||
      !settings.googleWorkspace.clientSecret ||
      !settings.googleWorkspace.callbackUrl
    ) {
      return yield* Effect.fail(
        new MissingCredentialsError({
          message: "Google Workspace OAuth is not configured",
          provider: "google-workspace",
        }),
      );
    }

    const url = new URL(request.url);
    const error = url.searchParams.get("error");
    if (error) {
      return yield* Effect.fail(
        new OAuthError({
          message: `Google OAuth error: ${error}`,
          provider: "google-workspace",
        }),
      );
    }

    const code = url.searchParams.get("code");
    const encodedState = url.searchParams.get("state");
    if (!code || !encodedState) {
      return yield* Effect.fail(
        new OAuthError({
          message: "Missing code or state parameter",
          provider: "google-workspace",
        }),
      );
    }

    // Decode and verify HMAC-signed state
    const stateData = yield* verifyState(encodedState);

    // Validate CSRF state cookie
    const storedState = getCookieValue(request, "gw_oauth_state");
    if (!storedState || storedState !== stateData.randomState) {
      return yield* Effect.fail(
        new InvalidStateError({
          message: "Invalid state parameter",
        }),
      );
    }

    // Re-authenticate the session to verify the user
    const { user } = yield* authenticate(request).pipe(
      Effect.mapError(
        () =>
          new OAuthError({
            message: "Session expired or invalid. Please try connecting again.",
            provider: "google-workspace",
          }),
      ),
    );

    // Verify the session user matches the state
    if (user.id !== stateData.userId) {
      return yield* Effect.fail(
        new InvalidStateError({
          message: "Session user does not match OAuth state",
        }),
      );
    }

    // Exchange code for tokens
    const tokenResponse = yield* Effect.tryPromise({
      try: async () => {
        const response = await fetch("https://oauth2.googleapis.com/token", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: new URLSearchParams({
            grant_type: "authorization_code",
            client_id: settings.googleWorkspace.clientId!,
            client_secret: settings.googleWorkspace.clientSecret!,
            code,
            redirect_uri: settings.googleWorkspace.callbackUrl!,
          }),
        });
        return (await response.json()) as {
          access_token?: string;
          refresh_token?: string;
          expires_in?: number;
          scope?: string;
          error?: string;
          error_description?: string;
        };
      },
      catch: (e) =>
        new OAuthError({
          message: "Failed to exchange code for tokens",
          provider: "google-workspace",
          cause: e,
        }),
    });

    if (tokenResponse.error || !tokenResponse.access_token) {
      return yield* Effect.fail(
        new OAuthError({
          message: `Token exchange failed: ${tokenResponse.error_description || tokenResponse.error || "No access token"}`,
          provider: "google-workspace",
        }),
      );
    }

    if (!tokenResponse.refresh_token) {
      return yield* Effect.fail(
        new OAuthError({
          message:
            "No refresh token received. Please revoke app access in Google Account settings and try again.",
          provider: "google-workspace",
        }),
      );
    }

    // Fetch user info for connected email
    const userInfo = yield* Effect.tryPromise({
      try: async () => {
        const response = await fetch(
          "https://www.googleapis.com/oauth2/v2/userinfo",
          {
            headers: {
              Authorization: `Bearer ${tokenResponse.access_token}`,
            },
          },
        );
        return (await response.json()) as {
          email?: string;
          name?: string;
        };
      },
      catch: (e) =>
        new OAuthError({
          message: "Failed to fetch user info",
          provider: "google-workspace",
          cause: e,
        }),
    });

    if (!userInfo.email) {
      return yield* Effect.fail(
        new OAuthError({
          message: "No email returned from Google",
          provider: "google-workspace",
        }),
      );
    }

    // Encrypt refresh token using claws/crypto.ts
    const { ciphertext, keyId } = yield* encryptSecrets({
      refresh_token: tokenResponse.refresh_token,
    }).pipe(
      Effect.mapError(
        (e) =>
          new OAuthError({
            message: `Failed to encrypt token: ${e.message}`,
            provider: "google-workspace",
          }),
      ),
    );

    // Upsert into claw_integration_google_workspace
    const client = yield* DrizzleORM;
    const tokenExpiresAt = tokenResponse.expires_in
      ? new Date(Date.now() + tokenResponse.expires_in * 1000)
      : null;

    yield* client
      .insert(clawIntegrationGoogleWorkspace)
      .values({
        clawId: stateData.clawId,
        userId: user.id,
        encryptedRefreshToken: ciphertext,
        refreshTokenKeyId: keyId,
        scopes: tokenResponse.scope || "",
        connectedEmail: userInfo.email,
        tokenExpiresAt,
      })
      .onConflictDoUpdate({
        target: [clawIntegrationGoogleWorkspace.clawId],
        set: {
          userId: user.id,
          encryptedRefreshToken: ciphertext,
          refreshTokenKeyId: keyId,
          scopes: tokenResponse.scope || "",
          connectedEmail: userInfo.email,
          tokenExpiresAt,
          updatedAt: new Date(),
        },
      })
      .pipe(
        Effect.mapError(
          (e) =>
            new OAuthError({
              message: "Failed to save connection",
              provider: "google-workspace",
              cause: e,
            }),
        ),
      );

    // Clear state cookie
    const clearCookieParts = [
      "gw_oauth_state=;",
      "Expires=Thu, 01 Jan 1970 00:00:00 GMT",
      "HttpOnly",
      ...(isSecure(settings) ? ["Secure"] : []),
      "SameSite=Lax",
      "Path=/",
    ];

    // Look up org slug and claw slug for redirect
    const [clawRow] = yield* client
      .select({
        clawSlug: claws.slug,
        orgSlug: organizations.slug,
      })
      .from(claws)
      .innerJoin(organizations, eq(claws.organizationId, organizations.id))
      .where(eq(claws.id, stateData.clawId))
      .limit(1)
      .pipe(
        Effect.mapError(
          () =>
            new OAuthError({
              message: "Failed to look up claw for redirect",
              provider: "google-workspace",
            }),
        ),
      );

    // Fall back to dashboard if slug lookup fails
    let redirectUrl: URL;
    if (clawRow) {
      redirectUrl = new URL(
        `/${clawRow.orgSlug}/claws/${clawRow.clawSlug}/chat`,
        siteUrl,
      );
    } else {
      redirectUrl = new URL("/", siteUrl);
    }
    redirectUrl.searchParams.set("integration", "google-workspace");
    redirectUrl.searchParams.set("status", "connected");

    return new Response(null, {
      status: 302,
      headers: {
        Location: redirectUrl.toString(),
        "Set-Cookie": clearCookieParts.join("; "),
      },
    });
  });
}

// =============================================================================
// Revoke connection handler
// =============================================================================

export function revokeConnectionEffect(request: Request) {
  return Effect.gen(function* () {
    yield* Settings;

    // Authenticate the user
    const { user } = yield* authenticate(request).pipe(
      Effect.mapError(
        (e) =>
          new AuthenticationFailedError({
            message: e.message,
          }),
      ),
    );

    // Parse request body
    const body = yield* Effect.tryPromise({
      try: () => request.json() as Promise<{ claw_id: string }>,
      catch: () =>
        new OAuthError({
          message: "Invalid request body",
          provider: "google-workspace",
        }),
    });

    if (!body.claw_id) {
      return yield* Effect.fail(
        new OAuthError({
          message: "Missing claw_id",
          provider: "google-workspace",
        }),
      );
    }

    const client = yield* DrizzleORM;

    // Verify claw exists
    const [claw] = yield* client
      .select({ organizationId: claws.organizationId })
      .from(claws)
      .where(eq(claws.id, body.claw_id))
      .limit(1)
      .pipe(
        Effect.mapError(
          () =>
            new OAuthError({
              message: "Failed to look up claw",
              provider: "google-workspace",
            }),
        ),
      );

    if (!claw) {
      return yield* Effect.fail(
        new OAuthError({
          message: "Claw not found",
          provider: "google-workspace",
        }),
      );
    }

    // Verify user is a member of the claw's organization
    yield* verifyOrgMembership(user.id, claw.organizationId);

    // Get the connection
    const [connection] = yield* client
      .select({
        id: clawIntegrationGoogleWorkspace.id,
        encryptedRefreshToken: clawIntegrationGoogleWorkspace.encryptedRefreshToken,
        refreshTokenKeyId: clawIntegrationGoogleWorkspace.refreshTokenKeyId,
      })
      .from(clawIntegrationGoogleWorkspace)
      .where(eq(clawIntegrationGoogleWorkspace.clawId, body.claw_id))
      .limit(1)
      .pipe(
        Effect.mapError(
          () =>
            new OAuthError({
              message: "Failed to look up connection",
              provider: "google-workspace",
            }),
        ),
      );

    if (!connection) {
      return yield* Effect.fail(
        new OAuthError({
          message: "No Google Workspace connection found for this claw",
          provider: "google-workspace",
        }),
      );
    }

    // Decrypt refresh token to revoke with Google
    const secrets = yield* decryptSecrets(
      connection.encryptedRefreshToken,
      connection.refreshTokenKeyId,
    ).pipe(
      Effect.mapError(
        (e) =>
          new OAuthError({
            message: `Failed to decrypt token: ${e.message}`,
            provider: "google-workspace",
          }),
      ),
    );

    // Revoke token with Google (best-effort)
    if (secrets.refresh_token) {
      yield* Effect.tryPromise({
        try: () =>
          fetch("https://oauth2.googleapis.com/revoke", {
            method: "POST",
            headers: {
              "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams({
              token: secrets.refresh_token!,
            }),
          }),
        catch: () =>
          new OAuthError({
            message: "Failed to revoke token with Google",
            provider: "google-workspace",
          }),
      }).pipe(Effect.catchAll(() => Effect.void));
    }

    // Delete the connection from DB
    yield* client
      .delete(clawIntegrationGoogleWorkspace)
      .where(eq(clawIntegrationGoogleWorkspace.clawId, body.claw_id))
      .pipe(
        Effect.mapError(
          () =>
            new OAuthError({
              message: "Failed to delete connection",
              provider: "google-workspace",
            }),
        ),
      );

    return Response.json({ success: true });
  }).pipe(
    Effect.catchAll((error) => {
      if (error._tag === "AuthenticationFailedError") {
        return Effect.succeed(
          Response.json({ error: error.message }, { status: 401 }),
        );
      }
      if (
        error.message === "Not authorized to manage this claw's integrations"
      ) {
        return Effect.succeed(
          Response.json({ error: error.message }, { status: 403 }),
        );
      }
      if (
        error.message === "Claw not found" ||
        error.message === "No Google Workspace connection found for this claw"
      ) {
        return Effect.succeed(
          Response.json({ error: error.message }, { status: 404 }),
        );
      }
      return Effect.succeed(
        Response.json({ error: error.message }, { status: 500 }),
      );
    }),
  );
}
