import { createFileRoute } from "@tanstack/react-router";
import { generateOpenApiSpec } from "@/api/generate-openapi";

export const Route = createFileRoute("/api/v0/docs/openapi.json")({
  server: {
    handlers: {
      GET: () => {
        const spec = generateOpenApiSpec();
        return Response.json(spec, {
          headers: {
            "Content-Type": "application/json",
            "Cache-Control": "public, max-age=3600", // Cache for 1 hour
          },
        });
      },
    },
  },
});
