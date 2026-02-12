/**
 * @fileoverview GET /api/v1/auth/me — introspect authenticated API key.
 *
 * Returns the user and API key info (including organizationId).
 * Used by the CLI to discover which org to target in subsequent v2 API calls.
 */

import { createFileRoute } from "@tanstack/react-router";
import { Effect, Layer } from "effect";

import { handleErrors, handleDefects } from "@/api/utils";
import { authenticate } from "@/auth/utils";
import { Database } from "@/db/database";
import { UnauthorizedError } from "@/errors";
import { settingsLayer } from "@/server-entry";
import { Settings } from "@/settings";

export const Route = createFileRoute("/api/v1/auth/me")({
  server: {
    handlers: {
      GET: async ({ request }: { request: Request }) => {
        const handler = Effect.gen(function* () {
          const authResult = yield* authenticate(request);

          if (!authResult.apiKeyInfo) {
            return yield* new UnauthorizedError({
              message:
                "Org-scoped API key required. Provide Authorization: Bearer <key> header.",
            });
          }

          if (!authResult.apiKeyInfo.organizationId) {
            return yield* new UnauthorizedError({
              message:
                "This API key is not org-scoped. Create an org-scoped key from the dashboard.",
            });
          }

          return new Response(
            JSON.stringify({
              user: {
                id: authResult.user.id,
                email: authResult.user.email,
                name: authResult.user.name,
              },
              apiKey: {
                id: authResult.apiKeyInfo.apiKeyId,
                organizationId: authResult.apiKeyInfo.organizationId,
                environmentId: authResult.apiKeyInfo.environmentId ?? null,
                projectId: authResult.apiKeyInfo.projectId ?? null,
              },
            }),
            { status: 200, headers: { "Content-Type": "application/json" } },
          );
        }).pipe(
          Effect.provide(
            Layer.unwrapEffect(
              Effect.gen(function* () {
                const settings = yield* Settings;
                return Database.Live({
                  database: { connectionString: settings.databaseUrl },
                  payments: settings.stripe,
                });
              }).pipe(Effect.provide(settingsLayer)),
            ),
          ),
          handleErrors,
          handleDefects,
        );

        return Effect.runPromise(handler);
      },
    },
  },
});
