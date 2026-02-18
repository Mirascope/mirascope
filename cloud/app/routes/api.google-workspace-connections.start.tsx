import { createFileRoute } from "@tanstack/react-router";

import { startOAuthEffect } from "@/app/api/google-workspace-connections.handlers";
import { runEffectResponse } from "@/app/lib/effect";

export const Route = createFileRoute("/api/google-workspace-connections/start")(
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
