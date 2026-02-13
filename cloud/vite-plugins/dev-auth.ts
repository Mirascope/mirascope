/**
 * Vite dev server plugin for automatic authentication in local development.
 *
 * When ENVIRONMENT=development (or CLOUDFLARE_ENV=local), this plugin
 * automatically injects the dev session cookie into every request,
 * bypassing the OAuth login flow entirely.
 *
 * The session ID must match the one created by scripts/dev/seed.ts.
 *
 * This plugin is a no-op in production builds.
 */
import type { Plugin } from "vite";

const DEV_SESSION_ID = "00000000-0000-4000-8000-000000000004";

export function viteDevAuth(): Plugin {
  return {
    name: "vite-plugin-dev-auth",
    configureServer(server) {
      const env = process.env.CLOUDFLARE_ENV ?? process.env.ENVIRONMENT;
      if (env !== "local" && env !== "development") {
        return;
      }

      console.log("[dev-auth] Auto-auth enabled (dev session cookie injected)");

      // Use middleware to inject cookie BEFORE Cloudflare/TanStack processes the request
      server.middlewares.use((req, res, next) => {
        const cookieHeader = req.headers.cookie ?? "";

        // If no session cookie, inject one
        if (!cookieHeader.includes("session=")) {
          req.headers.cookie = cookieHeader
            ? `${cookieHeader}; session=${DEV_SESSION_ID}`
            : `session=${DEV_SESSION_ID}`;
        }

        // Also set the cookie in the browser on HTML page loads so DevTools shows it
        const accept = req.headers.accept ?? "";
        if (
          accept.includes("text/html") &&
          !cookieHeader.includes("session=")
        ) {
          const existingSetCookie = res.getHeader("set-cookie");
          const cookieValue = `session=${DEV_SESSION_ID}; Path=/; Max-Age=31536000; SameSite=Lax`;

          if (existingSetCookie) {
            const cookies = Array.isArray(existingSetCookie)
              ? existingSetCookie
              : [String(existingSetCookie)];
            res.setHeader("set-cookie", [...cookies, cookieValue]);
          } else {
            res.setHeader("set-cookie", cookieValue);
          }
        }

        next();
      });
    },
  };
}
