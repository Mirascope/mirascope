import { createFileRoute } from "@tanstack/react-router";

import { startOAuthEffect } from "@/app/api/claw-integration-google-workspace.handlers";
import { runEffectResponse } from "@/app/lib/effect";

export const Route = createFileRoute("/integrations/google-workspace/auth/start")(
  {
    server: {
      handlers: {
        GET: async ({ request }) => {
          return await runEffectResponse(startOAuthEffect(request));
        },
      },
    },
  },
);
