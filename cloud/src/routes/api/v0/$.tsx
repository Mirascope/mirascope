import { createFileRoute } from "@tanstack/react-router";
import { handleRequest } from "@/api/handler";

// Effect Platform API route handler
// TODO: discuss API versioning/naming strategy before release
export const Route = createFileRoute("/api/v0/$")({
  server: {
    handlers: {
      ANY: async ({ request }: { request: Request }) => {
        const { matched, response } = await handleRequest(request, {
          environment: process.env.ENVIRONMENT || "development",
          prefix: "/api/v0",
        });

        if (matched) {
          return response;
        }

        return new Response("Not Found", { status: 404 });
      },
    },
  },
});
