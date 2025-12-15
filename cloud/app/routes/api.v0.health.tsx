import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/api/v0/health")({
  server: {
    handlers: {
      GET: () => {
        return Response.json({
          status: "ok",
          timestamp: new Date().toISOString(),
          environment: process.env.ENVIRONMENT || "development",
        });
      },
    },
  },
});
