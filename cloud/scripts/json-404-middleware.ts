/**
 * JSON 404 middleware for Vite development server
 *
 * This middleware ensures that requests for non-existent JSON files
 * return a proper 404 response instead of falling back to index.html
 */

import fs from "fs";
import path from "path";
import type { Connect } from "vite";

/**
 * Create a Vite plugin that adds middleware to handle 404s for JSON requests
 */
export function json404Middleware() {
  return {
    name: "vite-plugin-json-404",
    configureServer(server: {
      middlewares: { use: (middleware: Connect.NextHandleFunction) => void };
    }) {
      console.log("🔍 JSON 404 middleware enabled");
      server.middlewares.use(createJson404Middleware());
    },
  };
}

/**
 * Create middleware that intercepts JSON requests and returns 404 for non-existent files
 */
function createJson404Middleware(): Connect.NextHandleFunction {
  return async (req, res, next) => {
    // Only handle JSON requests
    if (!req.url || !req.url.endsWith(".json")) {
      return next();
    }

    // Clean up URL and get file path
    const urlPath = req.url.startsWith("/") ? req.url.slice(1) : req.url;
    const filePath = path.resolve(process.cwd(), "public", urlPath);

    // Check if the file exists
    if (!fs.existsSync(filePath)) {
      // File doesn't exist, return 404
      res.statusCode = 404;
      res.setHeader("Content-Type", "application/json");
      res.end(
        JSON.stringify({
          error: "Not Found",
          message: `The requested resource ${req.url} could not be found.`,
        })
      );
      return;
    }

    // File exists, let the next middleware handle it
    next();
  };
}
