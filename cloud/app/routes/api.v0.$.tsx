import { createFileRoute } from "@tanstack/react-router";
import { Effect } from "effect";
import { handleRequest } from "@/api/handler";
import { handleErrors, handleDefects } from "@/api/utils";
import { UnauthorizedError, NotFoundError, InternalError } from "@/errors";
import { getAuthenticatedUser } from "@/auth";
import { EffectDatabase } from "@/db";

export const Route = createFileRoute("/api/v0/$")({
  server: {
    handlers: {
      ANY: async ({ request }: { request: Request }) => {
        const databaseUrl = process.env.DATABASE_URL;

        const handler = Effect.gen(function* () {
          if (!databaseUrl) {
            return yield* new InternalError({
              message: "Database not configured",
            });
          }

          const authenticatedUser = yield* getAuthenticatedUser(request);

          if (!authenticatedUser) {
            return yield* new UnauthorizedError({
              message: "Authentication required",
            });
          }

          const result = yield* handleRequest(request, {
            prefix: "/api/v0",
            authenticatedUser,
            environment: process.env.ENVIRONMENT || "development",
          });

          if (!result.matched) {
            return yield* new NotFoundError({ message: "Route not found" });
          }

          return result.response;
        }).pipe(
          Effect.provide(
            EffectDatabase.Live({ connectionString: databaseUrl }),
          ),
          handleErrors,
          handleDefects,
        );

        return Effect.runPromise(handler);
      },
    },
  },
});
