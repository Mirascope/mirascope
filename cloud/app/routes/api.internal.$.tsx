/**
 * Internal API route handler: /api/internal/*
 *
 * Serves internal endpoints called by the dispatch worker via Cloudflare
 * service binding. NOT part of the public API — no user authentication.
 *
 * Routes:
 *   GET  /api/internal/claws/resolve/:orgSlug/:clawSlug  → resolveClawHandler
 *   GET  /api/internal/claws/:clawId/bootstrap            → bootstrapClawHandler
 *   POST /api/internal/claws/:clawId/status               → reportClawStatusHandler
 */
import { createFileRoute } from "@tanstack/react-router";
import { Effect, Layer, Schema } from "effect";

import {
  resolveClawHandler,
  bootstrapClawHandler,
  reportClawStatusHandler,
  ClawStatusReportSchema,
} from "@/api/claws-internal.handlers";
import { handleErrors, handleDefects } from "@/api/utils";
import { DrizzleORM } from "@/db/client";
import { Database } from "@/db/database";
import { DatabaseError, EncryptionError, NotFoundError } from "@/errors";
import { settingsLayer } from "@/server-entry";
import { Settings } from "@/settings";

type InternalError = NotFoundError | DatabaseError | EncryptionError;

/**
 * Match the splat path against known internal routes.
 *
 * Returns the Effect to run, or null if no route matches.
 */
function matchRoute(
  method: string,
  splat: string | undefined,
  getBody: () => Promise<unknown>,
): Effect.Effect<unknown, InternalError, DrizzleORM | Settings> | null {
  if (!splat) return null;

  const parts = splat.split("/").filter(Boolean);

  // GET claws/resolve/:orgSlug/:clawSlug
  if (
    method === "GET" &&
    parts.length === 4 &&
    parts[0] === "claws" &&
    parts[1] === "resolve"
  ) {
    return resolveClawHandler(parts[2], parts[3]);
  }

  // GET claws/:clawId/bootstrap
  if (
    method === "GET" &&
    parts.length === 3 &&
    parts[0] === "claws" &&
    parts[2] === "bootstrap"
  ) {
    return bootstrapClawHandler(parts[1]);
  }

  // POST claws/:clawId/status
  if (
    method === "POST" &&
    parts.length === 3 &&
    parts[0] === "claws" &&
    parts[2] === "status"
  ) {
    const clawId = parts[1];
    return Effect.gen(function* () {
      const raw = yield* Effect.promise(getBody);
      const decodeResult = Schema.decodeUnknownEither(ClawStatusReportSchema)(
        raw,
      );
      if (decodeResult._tag === "Left") {
        return yield* Effect.fail(
          new NotFoundError({
            message: "Invalid status report payload",
          }),
        );
      }
      return yield* reportClawStatusHandler(clawId, decodeResult.right);
    });
  }

  return null;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any -- route path not in generated route tree yet
export const Route = createFileRoute("/api/internal/$" as any)({
  server: {
    handlers: {
      ANY: async ({
        request,
        params,
      }: {
        request: Request;
        params: { "*"?: string };
      }) => {
        const handler = Effect.gen(function* () {
          const matched = matchRoute(request.method, params["*"], () =>
            request.json(),
          );

          if (!matched) {
            return new Response(JSON.stringify({ error: "Not found" }), {
              status: 404,
              headers: { "Content-Type": "application/json" },
            });
          }

          const result = yield* matched;

          return new Response(JSON.stringify(result ?? { ok: true }), {
            status: 200,
            headers: { "Content-Type": "application/json" },
          });
        }).pipe(
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
          handleErrors,
          handleDefects,
        );

        return Effect.runPromise(handler);
      },
    },
  },
});
