/**
 * Optimized image middleware for Vite development server
 *
 * This module provides on-demand WebP image processing during development.
 * Images are processed in memory without writing to the file system.
 */

import { resolve } from "path";
import fs from "fs";
import sharp from "sharp";
import type { Connect } from "vite";
import path from "path";

// Configuration for image processing
const CONFIG = {
  // Quality settings
  quality: {
    webp: 80,
  },

  // Responsive image sizes
  sizes: {
    medium: 1024,
    small: 640,
  },

  // Cache processed images in memory to avoid reprocessing
  imageCache: new Map<string, Buffer>(),
};

/**
 * Create a Vite plugin for on-demand optimized image processing
 */
export function optimizedImageMiddleware() {
  return {
    name: "vite-plugin-optimized-images",
    configureServer(server: {
      middlewares: { use: (middleware: Connect.NextHandleFunction) => void };
    }) {
      console.log("🖼️  Optimized image middleware enabled (quality: " + CONFIG.quality.webp + "%)");
      server.middlewares.use(createImageMiddleware());
    },
  };
}

/**
 * Create middleware for on-demand image processing
 */
function createImageMiddleware(): Connect.NextHandleFunction {
  return async (req, res, next) => {
    // Skip non-WebP requests
    if (!req.url || !req.url.includes(".webp")) {
      return next();
    }
    const url = req.url;

    // Skip for SVG and GIF WebP requests (which we don't generate)
    if (url.match(/\.(svg|gif)\.webp$/)) {
      return next();
    }

    // Check cache first
    if (CONFIG.imageCache.has(url)) {
      const imageBuffer = CONFIG.imageCache.get(url);
      if (imageBuffer) {
        res.setHeader("Content-Type", "image/webp");
        res.setHeader("Cache-Control", "max-age=3600");
        res.end(imageBuffer);
        return;
      }
    }

    try {
      // Parse the URL to get details about the requested image
      const { originalFilePath, size } = parseImageRequest(url);

      if (!originalFilePath) {
        console.log(`❌ Original image not found for: ${url}`);
        // Original image not found, continue to next middleware (will likely 404)
        return next();
      }

      // Process the image with the appropriate size
      let imageProcessor = sharp(originalFilePath);

      // Apply resize for responsive images if needed
      if (size !== "large") {
        const width = CONFIG.sizes[size];
        imageProcessor = imageProcessor.resize({ width });
      }

      // Convert to WebP and get buffer
      const imageBuffer = await imageProcessor.webp({ quality: CONFIG.quality.webp }).toBuffer();

      // Cache the processed image
      CONFIG.imageCache.set(url, imageBuffer);

      // Serve the processed image
      res.setHeader("Content-Type", "image/webp");
      res.setHeader("Cache-Control", "max-age=3600");
      res.end(imageBuffer);
    } catch (error) {
      console.error(`❌ Error processing image ${url}: ${error}`);
      return next();
    }
  };
}

/**
 * Parse an image request URL and find the original source file
 */
function parseImageRequest(url: string): {
  originalFilePath: string | null;
  size: "large" | "medium" | "small";
} {
  // Default to large size (original dimensions)
  let size: "large" | "medium" | "small" = "large";

  // Clean up URL and extract filename
  const urlPath = url.startsWith("/") ? url.slice(1) : url;
  const pathParts = urlPath.split("/");
  const filename = pathParts.pop() || "";
  const directory = pathParts.join("/");

  // Get base name without size suffix or extension
  let baseName = filename;

  // Handle responsive variants
  if (filename.includes("-medium.webp")) {
    size = "medium";
    baseName = filename.replace(/-medium\.webp$/, "");
  } else if (filename.includes("-small.webp")) {
    size = "small";
    baseName = filename.replace(/-small\.webp$/, "");
  } else if (filename.endsWith(".webp")) {
    baseName = filename.replace(/\.webp$/, "");
  }

  // Build the full directory path
  const dirPath = resolve(process.cwd(), "public", directory);

  // Find the original file to process
  const originalFilePath = findOriginalFile(dirPath, baseName);

  return { originalFilePath, size };
}

/**
 * Find the original image file to use as source
 */
function findOriginalFile(directory: string, baseName: string): string | null {
  // Extensions to try, in order of preference
  const extensions = [".webp", ".png", ".jpg", ".jpeg"];

  for (const ext of extensions) {
    const filePath = path.join(directory, `${baseName}${ext}`);
    if (fs.existsSync(filePath)) {
      return filePath;
    }
  }

  return null;
}
