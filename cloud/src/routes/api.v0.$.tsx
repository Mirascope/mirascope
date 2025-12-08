import { createFileRoute } from "@tanstack/react-router";
import { Effect } from "effect";
import { handleRequest } from "@/api/handler";
import { getSessionIdFromCookie } from "@/auth/utils";
import { getDatabase } from "@/db";
import type { PublicUser } from "@/db/schema";

async function getAuthenticatedUser(
  request: Request,
): Promise<PublicUser | null> {
  const sessionId = getSessionIdFromCookie(request);
  if (!sessionId) {
    return null;
  }

  const databaseUrl = process.env.DATABASE_URL;
  if (!databaseUrl) {
    return null;
  }

  const db = getDatabase(databaseUrl);

  return Effect.runPromise(
    db.sessions
      .findUserBySessionId(sessionId)
      .pipe(Effect.catchAll(() => Effect.succeed(null))),
  );
}

// TODO: discuss API versioning/naming strategy before release
export const Route = createFileRoute("/api/v0/$")({
  server: {
    handlers: {
      ANY: async ({ request }: { request: Request }) => {
        // All API v0 routes require authentication
        const authenticatedUser = await getAuthenticatedUser(request);
        if (!authenticatedUser) {
          return Response.json(
            {
              _tag: "UnauthorizedError",
              message: "Authentication required",
            },
            { status: 401 },
          );
        }

        const { matched, response } = await handleRequest(request, {
          environment: process.env.ENVIRONMENT || "development",
          prefix: "/api/v0",
          authenticatedUser,
          databaseUrl: process.env.DATABASE_URL,
        });

        if (matched) {
          return response;
        }

        return new Response("Not Found", { status: 404 });
      },
    },
  },
});
