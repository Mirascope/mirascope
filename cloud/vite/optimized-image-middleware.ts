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
import type { IncomingMessage, ServerResponse } from "http";
import path from "path";

// Configuration for image processing
const CONFIG = {
  quality: {
    webp: 80,
  },
  sizes: {
    medium: 1024,
    small: 640,
  },
  imageCache: new Map<string, Buffer>(),
};

type ImageSize = "large" | "medium" | "small";

/**
 * Create a Vite plugin for on-demand optimized image processing
 */
export function optimizedImageMiddleware() {
  return {
    name: "vite-plugin-optimized-images",
    configureServer(server: {
      middlewares: { use: (middleware: Connect.NextHandleFunction) => void };
    }) {
      console.log(
        `🖼️  Optimized image middleware enabled (quality: ${CONFIG.quality.webp}%)`,
      );
      server.middlewares.use(createImageMiddleware());
    },
  };
}

/**
 * Create middleware for on-demand image processing
 */
function createImageMiddleware(): Connect.NextHandleFunction {
  return (req, res, next) => {
    void handleImageRequest(req, res, next);
  };
}

/**
 * Handle an image request - process and serve optimized WebP images
 */
async function handleImageRequest(
  req: IncomingMessage,
  res: ServerResponse,
  next: Connect.NextFunction,
): Promise<void> {
  const url = req.url;
  if (!url) {
    next();
    return;
  }

  // Skip non-WebP requests
  if (!isWebPRequest(url)) {
    next();
    return;
  }

  // Check cache first
  const cachedImage = CONFIG.imageCache.get(url);
  if (cachedImage) {
    serveImage(res, cachedImage);
    return;
  }

  try {
    const { originalFilePath, size } = parseImageRequest(url);

    if (!originalFilePath) {
      console.log(`❌ Original image not found for: ${url}`);
      next();
      return;
    }

    const imageBuffer = await processImage(originalFilePath, size);
    CONFIG.imageCache.set(url, imageBuffer);
    serveImage(res, imageBuffer);
  } catch (error) {
    console.error(`❌ Error processing image ${url}:`, error);
    next();
  }
}

/**
 * Check if the request is for a WebP image we should process
 */
function isWebPRequest(url: string): boolean {
  if (!url.includes(".webp")) {
    return false;
  }
  // Skip SVG and GIF WebP requests (which we don't generate)
  return !url.match(/\.(svg|gif)\.webp$/);
}

/**
 * Serve an image buffer with appropriate headers
 */
function serveImage(res: ServerResponse, buffer: Buffer): void {
  res.setHeader("Content-Type", "image/webp");
  res.setHeader("Cache-Control", "max-age=3600");
  res.end(buffer);
}

/**
 * Process an image: resize if needed and convert to WebP
 */
async function processImage(
  filePath: string,
  size: ImageSize,
): Promise<Buffer> {
  let processor = sharp(filePath);

  if (size !== "large") {
    const width = CONFIG.sizes[size];
    processor = processor.resize({ width });
  }

  return processor.webp({ quality: CONFIG.quality.webp }).toBuffer();
}

/**
 * Parse an image request URL and find the original source file
 */
function parseImageRequest(url: string): {
  originalFilePath: string | null;
  size: ImageSize;
} {
  const { filename, directory } = extractPathComponents(url);
  const { baseName, size } = extractImageSize(filename);
  const dirPath = resolve(process.cwd(), "public", directory);
  const publicDir = resolve(process.cwd(), "public");
  if (!dirPath.startsWith(publicDir)) {
    console.error(`❌ Invalid image request: ${url}`);
    return { originalFilePath: null, size };
  }
  const originalFilePath = findOriginalFile(dirPath, baseName);

  return { originalFilePath, size };
}

/**
 * Extract filename and directory from URL
 */
function extractPathComponents(url: string): {
  filename: string;
  directory: string;
} {
  const urlPath = url.startsWith("/") ? url.slice(1) : url;
  const pathParts = urlPath.split("/");
  const filename = pathParts.pop() || "";
  const directory = pathParts.join("/");

  return { filename, directory };
}

/**
 * Extract base name and size from filename
 */
function extractImageSize(filename: string): {
  baseName: string;
  size: ImageSize;
} {
  if (filename.includes("-medium.webp")) {
    return {
      baseName: filename.replace(/-medium\.webp$/, ""),
      size: "medium",
    };
  }

  if (filename.includes("-small.webp")) {
    return {
      baseName: filename.replace(/-small\.webp$/, ""),
      size: "small",
    };
  }

  if (filename.endsWith(".webp")) {
    return {
      baseName: filename.replace(/\.webp$/, ""),
      size: "large",
    };
  }

  return { baseName: filename, size: "large" };
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
