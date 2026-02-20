import { createFileRoute } from "@tanstack/react-router";

import { callbackOAuthEffect } from "@/app/api/google-workspace-connections.handlers";
import { runEffectResponse } from "@/app/lib/effect";

export const Route = createFileRoute(
  "/integrations/google-workspace/auth/callback",
)({
  server: {
    handlers: {
      GET: async ({ request }) => {
        return await runEffectResponse(callbackOAuthEffect(request));
      },
    },
  },
});
