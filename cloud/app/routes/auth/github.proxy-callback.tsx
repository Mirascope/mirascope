import { createFileRoute } from "@tanstack/react-router";
import { Effect } from "effect";
import { AuthService } from "@/auth";
import { runEffectResponse } from "@/app/lib/effect";

export const Route = createFileRoute("/auth/github/proxy-callback")({
  server: {
    handlers: {
      GET: async ({ request }) => {
        return await runEffectResponse(
          Effect.gen(function* () {
            const auth = yield* AuthService;
            return yield* auth.handleProxyCallback(request, "github");
          }),
        );
      },
    },
  },
});
