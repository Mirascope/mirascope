import { createFileRoute } from "@tanstack/react-router";
import { Effect, Layer } from "effect";
import { Settings, validateSettings } from "@/settings";

export const Route = createFileRoute("/api/v0/health")({
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
            Effect.provide(
              Layer.effect(Settings, validateSettings().pipe(Effect.orDie)),
            ),
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
