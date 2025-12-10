#!/usr/bin/env bun
/**
 * A custom static file server that properly handles SPA routing
 * This ensures routes like /privacy correctly serve /privacy/index.html
 */
import { createServer, type IncomingMessage, type ServerResponse } from "http";
import fs from "node:fs";
import path from "node:path";

// MIME type mapping
const MIME_TYPES: Record<string, string> = {
  ".html": "text/html",
  ".js": "application/javascript",
  ".css": "text/css",
  ".json": "application/json",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
  ".webp": "image/webp",
  ".webm": "video/webm",
  ".mp4": "video/mp4",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".ttf": "font/ttf",
  ".otf": "font/otf",
  ".eot": "application/vnd.ms-fontobject",
  ".xml": "application/xml",
  ".pdf": "application/pdf",
  ".txt": "text/plain",
  ".map": "application/json",
};

// Parse command line arguments for port (first arg is the port)
const PORT = parseInt(process.argv[2], 10) || 3000; // Default to 3000, matching dev server
const HOST = "127.0.0.1"; // Use IPv4 explicitly
const distDir = path.resolve(process.cwd(), "dist");

// Check if the dist directory exists
if (!fs.existsSync(distDir)) {
  console.error("❌ Dist directory not found. Run `bun run build` first.");
  process.exit(1);
}

// Check if the port is in use before starting
async function checkPort() {
  return new Promise<boolean>((resolve) => {
    const testServer = createServer();

    testServer.once("error", (err: NodeJS.ErrnoException) => {
      if (err.code === "EADDRINUSE") {
        console.error(`❌ Error: Port ${PORT} is already in use. Please try another port.`);
        resolve(false);
      } else {
        console.error(`❌ Error checking port: ${err.message}`);
        resolve(false);
      }
    });

    testServer.once("listening", () => {
      testServer.close();
      resolve(true);
    });

    testServer.listen(PORT, HOST);
  });
}

// Create HTTP server
const server = createServer((req, res) => {
  console.log(`${req.method} ${req.url}`);

  // Get URL path
  let url = req.url || "/";

  // Enhanced security check for path traversal attempts
  // Normalize the path and check for traversal attempts
  const normalizedUrl = path.normalize(url);

  // Check for path traversal attempts
  if (
    normalizedUrl.includes("..") ||
    normalizedUrl.includes("\0") ||
    url !== decodeURIComponent(encodeURIComponent(url)) ||
    url.includes("//")
  ) {
    res.statusCode = 403;
    res.end("Forbidden");
    return;
  }

  // Check if this is an asset request
  if (url.startsWith("/assets/")) {
    serveFile(url, res);
    return;
  }

  // Handle other static files with direct file extension
  if (path.extname(url)) {
    serveFile(url, res);
    return;
  }

  // Handle directory-style URLs (e.g., /privacy, /docs/mirascope)
  const urlWithoutQuery = url.split("?")[0];
  let normalizedPath = urlWithoutQuery;

  // Add trailing slash if needed
  if (!normalizedPath.endsWith("/")) {
    normalizedPath += "/";
  }

  // Check if there's an index.html in the requested directory
  const indexFilePath = path.join(distDir, normalizedPath.slice(1), "index.html");

  if (fs.existsSync(indexFilePath)) {
    serveFile(path.join(normalizedPath, "index.html"), res);
    return;
  }

  // Fallback to root index.html for SPA navigation
  serveFile("/index.html", res);
});

// Helper function to serve static files
function serveFile(url: string, res: ServerResponse<IncomingMessage>) {
  const filePath = path.join(distDir, url.startsWith("/") ? url.slice(1) : url);

  // Check if file exists
  if (!fs.existsSync(filePath)) {
    console.error(`File not found: ${filePath}`);
    res.statusCode = 404;
    res.end("Not Found");
    return;
  }

  // Set content type based on file extension
  const ext = path.extname(filePath);
  const contentType = MIME_TYPES[ext] || "application/octet-stream";
  res.setHeader("Content-Type", contentType);

  // Stream the file
  const fileStream = fs.createReadStream(filePath);
  fileStream.pipe(res);

  // Handle stream errors
  fileStream.on("error", (err) => {
    console.error(`Error reading file: ${err}`);
    res.statusCode = 500;
    res.end("Internal Server Error");
  });
}

// Start the server after checking the port
async function start() {
  console.log(`Checking if port ${PORT} is available on ${HOST}...`);
  const isAvailable = await checkPort();

  if (!isAvailable) {
    process.exit(1);
  }

  server.listen(PORT, HOST, () => {
    console.log(`✅ Static site server running at http://${HOST}:${PORT}`);
  });
}

// Handle server errors
server.on("error", (err) => {
  console.error("❌ Server error:", err);
  process.exit(1);
});

// Start the server
start();
