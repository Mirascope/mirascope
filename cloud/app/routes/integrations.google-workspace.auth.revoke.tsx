import { createFileRoute } from "@tanstack/react-router";

import { revokeConnectionEffect } from "@/app/api/google-workspace-connections.handlers";
import { runEffectResponse } from "@/app/lib/effect";

export const Route = createFileRoute(
  "/integrations/google-workspace/auth/revoke",
)({
  server: {
    handlers: {
      POST: async ({ request }) => {
        return await runEffectResponse(revokeConnectionEffect(request));
      },
    },
  },
});
