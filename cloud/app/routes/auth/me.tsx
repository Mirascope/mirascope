import { createFileRoute } from "@tanstack/react-router";
import { Effect } from "effect";

import { runEffectResponse } from "@/app/lib/effect";
import { getSessionIdFromCookie } from "@/auth/utils";
import { Database } from "@/db/database";

export const Route = createFileRoute("/auth/me")({
  server: {
    handlers: {
      GET: async ({ request }) => {
        return await runEffectResponse(
          Effect.gen(function* () {
            const sessionId = getSessionIdFromCookie(request);

            if (!sessionId) {
              return Response.json(
                { success: false, error: "Not authenticated" },
                { status: 401 },
              );
            }

            const db = yield* Database;
            const user = yield* db.sessions.findUserBySessionId(sessionId);

            return Response.json({
              success: true,
              user,
            });
          }),
        );
      },
    },
  },
});
