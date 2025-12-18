import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/api/v0/docs")({
  server: {
    handlers: {
      GET: () => {
        const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Mirascope Cloud API - Swagger UI</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui.css" />
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-bundle.js" crossorigin></script>
  <script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-standalone-preset.js" crossorigin></script>
  <script>
    window.onload = () => {
      window.ui = SwaggerUIBundle({
        url: '/api/v0/docs/openapi.json',
        dom_id: '#swagger-ui',
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIStandalonePreset,
        ],
        deepLinking: true,
        showExtensions: true,
        showCommonExtensions: true,
      });
    };
  </script>
</body>
</html>`;
        return new Response(html, {
          headers: {
            "Content-Type": "text/html",
          },
        });
      },
    },
  },
});
