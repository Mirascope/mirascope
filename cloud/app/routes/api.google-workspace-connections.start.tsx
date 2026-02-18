import { createFileRoute } from "@tanstack/react-router";
import { eq } from "drizzle-orm";
import { Effect } from "effect";

import { runEffectResponse } from "@/app/lib/effect";
import { MissingCredentialsError, OAuthError } from "@/auth/errors";
import { authenticate, isSecure } from "@/auth/utils";
import { DrizzleORM } from "@/db/client";
import { claws } from "@/db/schema";
import { Settings } from "@/settings";

export const Route = createFileRoute(
  "/api/google-workspace-connections/start",
)({
  server: {
    handlers: {
      GET: async ({ request }) => {
        return await runEffectResponse(
          Effect.gen(function* () {
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

            // Verify claw exists and user has access via org membership
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

            // Generate state with CSRF token and claw_id
            const randomState = crypto.randomUUID();
            const stateData = {
              randomState,
              clawId,
              organizationId: claw.organizationId,
              userId: user.id,
            };
            const encodedState = btoa(JSON.stringify(stateData));

            // Build Google OAuth URL
            const authUrl = new URL(
              "https://accounts.google.com/o/oauth2/v2/auth",
            );
            authUrl.searchParams.set("response_type", "code");
            authUrl.searchParams.set(
              "client_id",
              settings.googleWorkspace.clientId,
            );
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
          }),
        );
      },
    },
  },
});
