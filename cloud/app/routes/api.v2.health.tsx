import { createFileRoute } from "@tanstack/react-router";
import { Effect } from "effect";
import { Settings } from "@/settings";
import { settingsLayer } from "@/server-entry";

export const Route = createFileRoute("/api/v2/health")({
  server: {
    handlers: {
      GET: async () => {
        // Get validated settings (will fail if env vars missing)
        return Effect.runPromise(
          Effect.gen(function* () {
            const settings = yield* Settings;
            return Response.json({
              status: "ok",
              timestamp: new Date().toISOString(),
              environment: settings.env,
            });
          }).pipe(
            Effect.provide(settingsLayer),
            Effect.catchAll(() =>
              Effect.succeed(
                Response.json({
                  status: "ok",
                  timestamp: new Date().toISOString(),
                  environment: "unknown",
                }),
              ),
            ),
          ),
        );
      },
    },
  },
});
