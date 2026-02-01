import { createFileRoute } from "@tanstack/react-router";
import { Effect } from "effect";

import { runEffectResponse } from "@/app/lib/effect";
import { AuthService } from "@/auth";

export const Route = createFileRoute("/auth/google/proxy-callback")({
  server: {
    handlers: {
      GET: async ({ request }) => {
        return await runEffectResponse(
          Effect.gen(function* () {
            const auth = yield* AuthService;
            return yield* auth.handleProxyCallback(request, "google");
          }),
        );
      },
    },
  },
});
