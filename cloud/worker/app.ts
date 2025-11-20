import { swaggerUI } from "@hono/swagger-ui";
import { OpenAPIHono } from "@hono/zod-openapi";
import type { Environment } from "@/worker/environment";
import { apiRouter } from "@/worker/api";
import { handleHealth, healthRoute } from "@/worker/health";

const app = new OpenAPIHono<{ Bindings: Environment }>();

app.doc("/openapi.json", {
  openapi: "3.1.0",
  info: {
    title: "Mirascope Cloud API",
    version: "0.1.0",
    description: "Complete API documentation for Mirascope Cloud",
  },
  servers: [
    {
      url: "https://v2.mirascope.com",
      description: "Production server",
      "x-fern-server-name": "production",
    },
    {
      url: "https://staging.mirascope.com",
      description: "Staging server",
      "x-fern-server-name": "staging",
    },
    {
      url: "http://localhost:3000",
      description: "Local development server",
      "x-fern-server-name": "local",
    },
  ],
  tags: [
    {
      name: "API",
      description: "Core API endpoints",
    },
  ],
});

app.route("/api", apiRouter);

app.get("/openapi-docs", swaggerUI({ url: "/openapi.json" }));

app.openapi(healthRoute, handleHealth);

app.notFound((c) => c.json({ error: "Not Found" }, 404));

export default app;
