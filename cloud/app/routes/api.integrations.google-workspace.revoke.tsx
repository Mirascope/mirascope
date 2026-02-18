import { createFileRoute } from "@tanstack/react-router";
import { eq } from "drizzle-orm";
import { Effect } from "effect";

import { runEffect } from "@/app/lib/effect";
import { OAuthError } from "@/auth/errors";
import { authenticate } from "@/auth/utils";
import { decryptSecrets } from "@/claws/crypto";
import { DrizzleORM } from "@/db/client";
import { claws, googleWorkspaceConnections } from "@/db/schema";
import { Settings } from "@/settings";

export const Route = createFileRoute(
  "/api/integrations/google-workspace/revoke",
)({
  server: {
    handlers: {
      POST: async ({ request }) => {
        const result = await runEffect(
          Effect.gen(function* () {
            yield* Settings;

            // Authenticate the user
            yield* authenticate(request).pipe(
              Effect.mapError(
                (e) =>
                  new OAuthError({
                    message: e.message,
                    provider: "google-workspace",
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

            // Get the connection
            const [connection] = yield* client
              .select({
                id: googleWorkspaceConnections.id,
                encryptedRefreshToken:
                  googleWorkspaceConnections.encryptedRefreshToken,
                refreshTokenKeyId: googleWorkspaceConnections.refreshTokenKeyId,
              })
              .from(googleWorkspaceConnections)
              .where(eq(googleWorkspaceConnections.clawId, body.claw_id))
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
              .delete(googleWorkspaceConnections)
              .where(eq(googleWorkspaceConnections.clawId, body.claw_id))
              .pipe(
                Effect.mapError(
                  () =>
                    new OAuthError({
                      message: "Failed to delete connection",
                      provider: "google-workspace",
                    }),
                ),
              );

            return { success: true };
          }),
        );

        if (result.success) {
          return Response.json(result.data);
        }
        return Response.json({ error: result.error }, { status: 400 });
      },
    },
  },
});
