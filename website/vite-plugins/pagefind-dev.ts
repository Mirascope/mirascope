import fs from "fs";
import path from "path";
import { type Plugin } from "vite";

/**
 * Vite plugin for Vite's dev server only: serves the Pagefind index from dist/_pagefind.
 */
export function pagefindDev(): Plugin {
  return {
    name: "vite-plugin-pagefind-dev",
    configureServer(server) {
      // Add middleware to serve Pagefind files
      server.middlewares.use((req, res, next) => {
        // Check if the request is for Pagefind files
        if (req.url?.startsWith("/_pagefind/")) {
          const pagefindPath = req.url.replace("/_pagefind/", "");
          const filePath = path.resolve("dist/client/_pagefind", pagefindPath);

          // Check if the file exists
          if (fs.existsSync(filePath)) {
            // Determine MIME type
            let contentType = "text/plain";
            if (filePath.endsWith(".js")) {
              contentType = "application/javascript; charset=utf-8";
            } else if (filePath.endsWith(".json")) {
              contentType = "application/json";
            } else if (filePath.endsWith(".css")) {
              contentType = "text/css";
            } else if (filePath.endsWith(".wasm")) {
              contentType = "application/wasm";
            } else if (filePath.endsWith(".pf_meta")) {
              contentType = "application/octet-stream";
            }
            res.setHeader("Content-Type", contentType);

            // Read and serve the file
            const content = fs.readFileSync(filePath);
            return res.end(content);
          }

          // Special handling for pagefind-entry.json with query parameters
          // Pagefind often requests this with a timestamp
          if (pagefindPath.startsWith("pagefind-entry.json")) {
            const entryPath = path.resolve(
              "dist/client/_pagefind",
              "pagefind-entry.json",
            );
            if (fs.existsSync(entryPath)) {
              res.setHeader("Content-Type", "application/json");
              const content = fs.readFileSync(entryPath);
              return res.end(content);
            }
          }

          // If file doesn't exist, return 404
          res.statusCode = 404;
          return res.end("Not found");
        }

        // Continue to next middleware if not a Pagefind request
        next();
      });
    },
  };
}
