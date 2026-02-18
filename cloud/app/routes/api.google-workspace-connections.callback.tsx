import { createFileRoute } from "@tanstack/react-router";
import { eq } from "drizzle-orm";
import { Effect } from "effect";

import { runEffectResponse } from "@/app/lib/effect";
import { InvalidStateError, OAuthError } from "@/auth/errors";
import { isSecure } from "@/auth/utils";
import { encryptSecrets } from "@/claws/crypto";
import { DrizzleORM } from "@/db/client";
import { claws, googleWorkspaceConnections, organizations } from "@/db/schema";
import { Settings } from "@/settings";

function getCookieValue(request: Request, name: string): string | null {
  const cookieHeader = request.headers.get("Cookie");
  if (!cookieHeader) return null;
  for (const cookie of cookieHeader.split(";")) {
    const [cookieName, value] = cookie.trim().split("=");
    if (cookieName === name) return value || null;
  }
  return null;
}

export const Route = createFileRoute(
  "/api/google-workspace-connections/callback",
)({
  server: {
    handlers: {
      GET: async ({ request }) => {
        return await runEffectResponse(
          Effect.gen(function* () {
            const settings = yield* Settings;
            const siteUrl = settings.siteUrl;

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

            // Decode state
            const stateData = yield* Effect.try({
              try: () =>
                JSON.parse(atob(encodedState)) as {
                  randomState: string;
                  clawId: string;
                  organizationId: string;
                  userId: string;
                },
              catch: () =>
                new InvalidStateError({
                  message: "Failed to decode state parameter",
                }),
            });

            // Validate CSRF state cookie
            const storedState = getCookieValue(request, "gw_oauth_state");
            if (!storedState || storedState !== stateData.randomState) {
              return yield* Effect.fail(
                new InvalidStateError({
                  message: "Invalid state parameter",
                }),
              );
            }

            // Exchange code for tokens
            const tokenResponse = yield* Effect.tryPromise({
              try: async () => {
                const response = await fetch(
                  "https://oauth2.googleapis.com/token",
                  {
                    method: "POST",
                    headers: {
                      "Content-Type": "application/x-www-form-urlencoded",
                    },
                    body: new URLSearchParams({
                      grant_type: "authorization_code",
                      client_id: settings.googleWorkspace.clientId,
                      client_secret: settings.googleWorkspace.clientSecret,
                      code,
                      redirect_uri: settings.googleWorkspace.callbackUrl,
                    }),
                  },
                );
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

            // Upsert into google_workspace_connections
            const client = yield* DrizzleORM;
            const tokenExpiresAt = tokenResponse.expires_in
              ? new Date(Date.now() + tokenResponse.expires_in * 1000)
              : null;

            yield* client
              .insert(googleWorkspaceConnections)
              .values({
                clawId: stateData.clawId,
                userId: stateData.userId,
                encryptedRefreshToken: ciphertext,
                refreshTokenKeyId: keyId,
                scopes: tokenResponse.scope || "",
                connectedEmail: userInfo.email,
                tokenExpiresAt,
              })
              .onConflictDoUpdate({
                target: [googleWorkspaceConnections.clawId],
                set: {
                  userId: stateData.userId,
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

            // Look up org slug and claw slug for redirect
            const [clawRow] = yield* client
              .select({
                clawSlug: claws.slug,
                orgSlug: organizations.slug,
              })
              .from(claws)
              .innerJoin(
                organizations,
                eq(claws.organizationId, organizations.id),
              )
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

            // Clear state cookie and redirect to claw settings
            const clearCookieParts = [
              "gw_oauth_state=;",
              "Expires=Thu, 01 Jan 1970 00:00:00 GMT",
              "HttpOnly",
              ...(isSecure(settings) ? ["Secure"] : []),
              "SameSite=Lax",
              "Path=/",
            ];

            const orgSlug = clawRow?.orgSlug || stateData.organizationId;
            const clawSlug = clawRow?.clawSlug || stateData.clawId;
            const redirectUrl = new URL(
              `/${orgSlug}/claws/${clawSlug}/settings`,
              siteUrl,
            );
            redirectUrl.searchParams.set("integration", "google-workspace");
            redirectUrl.searchParams.set("status", "connected");

            return new Response(null, {
              status: 302,
              headers: {
                Location: redirectUrl.toString(),
                "Set-Cookie": clearCookieParts.join("; "),
              },
            });
          }),
        );
      },
    },
  },
});
