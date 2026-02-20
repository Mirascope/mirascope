import { createFileRoute } from "@tanstack/react-router";
import { Effect, Layer } from "effect";

import { googleWorkspaceTokenEffect } from "@/app/api/claw-integration-google-workspace.handlers";
import { Database } from "@/db/database";
import { settingsLayer } from "@/server-entry";
import { Settings } from "@/settings";

export const Route = createFileRoute("/integrations/google-workspace/token")({
  server: {
    handlers: {
      GET: async ({ request }) => {
        const effect = googleWorkspaceTokenEffect(request).pipe(
          Effect.provide(
            Layer.merge(
              settingsLayer,
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
          ),
        );

        return Effect.runPromise(effect);
      },
    },
  },
});
