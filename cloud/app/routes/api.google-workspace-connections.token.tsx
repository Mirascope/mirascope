import { createFileRoute } from "@tanstack/react-router";
import { Effect, Layer } from "effect";

import { googleWorkspaceTokenEffect } from "@/app/api/google-workspace-connections.handlers";
import { Database } from "@/db/database";
import { settingsLayer } from "@/server-entry";
import { Settings } from "@/settings";

// eslint-disable-next-line @typescript-eslint/no-explicit-any -- route path not in generated route tree yet
export const Route = createFileRoute(
  "/api/google-workspace-connections/token" as any,
)({
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
