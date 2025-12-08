import { createFileRoute } from "@tanstack/react-router";
import { Effect, Layer } from "effect";
import { handleRequest, type App } from "@/api/handler";
import { getAuthenticatedUser } from "@/auth";
import { DatabaseService, getDatabase } from "@/db";
import { UnauthorizedError } from "@/db/errors";

export const Route = createFileRoute("/api/v0/$")({
  server: {
    handlers: {
      ANY: async ({ request }: { request: Request }) => {
        const databaseUrl = process.env.DATABASE_URL;
        if (!databaseUrl) {
          return new Response("Database not configured", { status: 500 });
        }

        const database = getDatabase(databaseUrl);

        try {
          const databaseLayer = Layer.succeed(DatabaseService, database);

          const authenticatedUser = await Effect.runPromise(
            getAuthenticatedUser(request).pipe(Effect.provide(databaseLayer)),
          );

          if (!authenticatedUser) {
            return Response.json(
              new UnauthorizedError({ message: "Authentication required" }),
              { status: 401 },
            );
          }

          const app: App = {
            environment: process.env.ENVIRONMENT || "development",
            database,
            authenticatedUser,
          };

          const { matched, response } = await handleRequest(request, {
            app,
            prefix: "/api/v0",
          });

          if (matched) {
            return response;
          }

          return new Response("Not Found", { status: 404 });
        } finally {
          await database.close();
        }
      },
    },
  },
});
