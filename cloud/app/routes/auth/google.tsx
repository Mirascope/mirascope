import { createFileRoute } from "@tanstack/react-router";
import { Effect } from "effect";
import { AuthService } from "@/auth";
import { runEffectResponse } from "@/app/lib/effect";

export const Route = createFileRoute("/auth/google")({
  server: {
    handlers: {
      GET: async ({ request }) => {
        return await runEffectResponse(
          Effect.gen(function* () {
            const auth = yield* AuthService;
            const provider = yield* auth.createGoogleProvider;
            const currentUrl = new URL(request.url).origin;
            return yield* auth.initiateOAuth(provider, currentUrl);
          }),
        );
      },
    },
  },
});
