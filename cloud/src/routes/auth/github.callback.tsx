import { createFileRoute } from "@tanstack/react-router";
import { Effect } from "effect";
import { AuthService } from "@/auth";
import { runEffectResponse } from "@/src/lib/effect";

export const Route = createFileRoute("/auth/github/callback")({
  server: {
    handlers: {
      GET: async ({ request }) => {
        return await runEffectResponse(
          Effect.gen(function* () {
            const auth = yield* AuthService;
            const provider = yield* auth.createGitHubProvider;
            return yield* auth.handleCallback(request, provider);
          }),
        );
      },
    },
  },
});
