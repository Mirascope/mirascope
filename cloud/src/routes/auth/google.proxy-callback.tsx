import { createFileRoute } from "@tanstack/react-router";
import { Effect } from "effect";
import { AuthService } from "@/auth";
import { runHandler } from "@/src/lib/effect";

export const Route = createFileRoute("/auth/google/proxy-callback")({
  server: {
    handlers: {
      GET: async ({ request }) => {
        return await runHandler(
          Effect.gen(function* () {
            const auth = yield* AuthService;
            return yield* auth.handleProxyCallback(request, "google");
          }),
        );
      },
    },
  },
});
