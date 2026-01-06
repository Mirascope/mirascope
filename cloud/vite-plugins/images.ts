/**
 * Vite plugin for WebP image processing
 *
 * This plugin provides optimized image processing for both development and production.
 *
 * Features:
 * - On-demand WebP conversion for images in public/ (development)
 * - Build-time generation of responsive variants (production)
 * - Path-specific configs: backgrounds get 95% quality, 1200/800px; others get 80%, 1024/640px
 * - WebP validation: build fails if any PNG/JPG files are found in dist
 * - In-memory caching for fast subsequent requests (development)
 * - Automatic source format detection (.webp, .png, .jpg, .jpeg)
 *
 * Development Usage:
 * Request optimized images by URL pattern:
 * - `/assets/hero.webp` - Original size as WebP
 * - `/assets/hero-medium.webp` - Medium width (path-dependent)
 * - `/assets/hero-small.webp` - Small width (path-dependent)
 *
 * Build-time:
 * - Responsive variants are auto-generated for all images in CONFIG.baseDir before build
 * - After build, CONFIG.distAssetsDir is scanned to ensure only WebP images exist
 */

import { resolve } from "path";
import fs from "fs";
import fsp from "fs/promises";
import sharp from "sharp";
import type { Connect, Plugin } from "vite";
import type { IncomingMessage, ServerResponse } from "http";
import path from "path";

// Responsive image configuration by path pattern
interface ResponsiveConfig {
  pattern: RegExp;
  quality: number;
  sizes: { medium: number; small: number };
}

// Full configuration type (internal)
interface ImageConfig {
  baseDir: string;
  distAssetsDir: string;
  scanConcurrency: number;
  processConcurrency: number;
  responsiveConfigs: ResponsiveConfig[];
  verbose: boolean;
  skipPatterns: RegExp[];
  /** Environment names to run build hooks for (empty = all environments) */
  viteEnvironments: string[];
}

// Plugin options type (all optional for user convenience)
export interface ViteImagesOptions {
  /** Base directory for all assets (default: "public/assets") */
  baseDir?: string;
  /** Output directory to validate after build (default: "dist/client/assets") */
  distAssetsDir?: string;
  /** Max concurrent operations for directory scanning (default: 50) */
  scanConcurrency?: number;
  /** Max concurrent image processing operations (default: 10) */
  processConcurrency?: number;
  /** Path-specific quality and size settings */
  responsiveConfigs?: ResponsiveConfig[];
  /** Enable verbose logging (default: false) */
  verbose?: boolean;
  /** Patterns to skip during processing */
  skipPatterns?: RegExp[];
  /** Vite environment names to run build hooks for (default: [] = all environments) */
  viteEnvironments?: string[];
}

// Default configuration
const DEFAULT_CONFIG: ImageConfig = {
  baseDir: "public/assets",
  distAssetsDir: "dist/client/assets",
  scanConcurrency: 50,
  processConcurrency: 10,
  responsiveConfigs: [
    {
      // Background images get higher quality and larger breakpoints
      pattern: /\/backgrounds\//,
      quality: 95,
      sizes: { medium: 1200, small: 800 },
    },
    {
      // Default for all other images
      pattern: /.*/,
      quality: 80,
      sizes: { medium: 1024, small: 640 },
    },
  ],
  verbose: false,
  skipPatterns: [],
  viteEnvironments: [],
};

/**
 * Merge user options with default configuration
 */
function mergeConfig(options?: ViteImagesOptions): ImageConfig {
  if (!options) {
    return DEFAULT_CONFIG;
  }

  return {
    baseDir: options.baseDir ?? DEFAULT_CONFIG.baseDir,
    distAssetsDir: options.distAssetsDir ?? DEFAULT_CONFIG.distAssetsDir,
    scanConcurrency: options.scanConcurrency ?? DEFAULT_CONFIG.scanConcurrency,
    processConcurrency:
      options.processConcurrency ?? DEFAULT_CONFIG.processConcurrency,
    responsiveConfigs:
      options.responsiveConfigs ?? DEFAULT_CONFIG.responsiveConfigs,
    verbose: options.verbose ?? DEFAULT_CONFIG.verbose,
    skipPatterns: options.skipPatterns ?? DEFAULT_CONFIG.skipPatterns,
    viteEnvironments:
      options.viteEnvironments ?? DEFAULT_CONFIG.viteEnvironments,
  };
}

// In-memory cache for development
const imageCache = new Map<string, Buffer>();

type ImageSize = "large" | "medium" | "small";

// Supported source image formats
const SOURCE_IMAGE_REGEX = /\.(webp|png|jpe?g)$/i;

/**
 * Check if a filename is a supported source image format
 */
function isSourceImage(filename: string): boolean {
  return SOURCE_IMAGE_REGEX.test(filename);
}

/**
 * Check if a filename is a non-WebP raster image (invalid in dist output)
 */
function isNonWebPImage(filename: string): boolean {
  return isSourceImage(filename) && !filename.toLowerCase().endsWith(".webp");
}

/**
 * Extract base name from an image filename (removes extension)
 */
function getImageBaseName(filename: string): string {
  return filename.replace(SOURCE_IMAGE_REGEX, "");
}

/**
 * Recursively scan a directory for files matching a filter
 * Processes entries in parallel batches for performance
 */
async function scanDirectory(
  dir: string,
  shouldInclude: (entry: fs.Dirent, fullPath: string) => boolean,
  onMatch: (fullPath: string) => void,
  scanConcurrency: number,
): Promise<void> {
  const entries = await fsp.readdir(dir, { withFileTypes: true });

  const processEntry = async (entry: fs.Dirent): Promise<void> => {
    const fullPath = path.join(dir, entry.name);

    if (entry.isDirectory()) {
      await scanDirectory(fullPath, shouldInclude, onMatch, scanConcurrency);
    } else if (entry.isFile() && shouldInclude(entry, fullPath)) {
      onMatch(fullPath);
    }
  };

  // Process entries with limited concurrency
  for (let i = 0; i < entries.length; i += scanConcurrency) {
    const batch = entries.slice(i, i + scanConcurrency);
    await Promise.all(batch.map(processEntry));
  }
}

/**
 * Get responsive config for a file path based on pattern matching
 */
function getResponsiveConfig(
  filePath: string,
  responsiveConfigs: ResponsiveConfig[],
): ResponsiveConfig {
  for (const config of responsiveConfigs) {
    if (config.pattern.test(filePath)) {
      return config;
    }
  }
  // Fallback to last config (default)
  return responsiveConfigs[responsiveConfigs.length - 1];
}

/**
 * Check if the plugin should run for the current environment
 * Returns true if environments is empty (run for all) or if current environment is in the list
 */
function shouldRunEnvironment(
  currentEnvironment: string | undefined,
  allowedEnvironments: string[],
): boolean {
  // If no environment is specified, run for all
  if (!currentEnvironment) {
    return true;
  }

  // If no environments specified, run for all
  if (allowedEnvironments.length === 0) {
    return true;
  }
  // Otherwise, only run if current environment is in the list
  return allowedEnvironments.includes(currentEnvironment);
}

/**
 * Create a Vite plugin for optimized image processing
 */
export function viteImages(options?: ViteImagesOptions): Plugin {
  const config = mergeConfig(options);
  let isBuild = false;

  return {
    name: "vite-plugin-images",

    // Detect build vs serve mode
    config(_config, { command }) {
      isBuild = command === "build";
    },

    // Development: serve optimized images on-demand
    configureServer(server: {
      middlewares: { use: (middleware: Connect.NextHandleFunction) => void };
    }) {
      console.log(`[images] Optimized image middleware enabled`);
      server.middlewares.use(createImageMiddleware(config));
    },

    // Production: generate responsive variants before build
    async buildStart() {
      if (
        !isBuild ||
        !shouldRunEnvironment(this.environment?.name, config.viteEnvironments)
      ) {
        return;
      }
      await generateResponsiveImages(config);
    },

    // Production: validate only WebP images in dist after build
    closeBundle: {
      sequential: true,
      async handler() {
        if (
          !isBuild ||
          !shouldRunEnvironment(this.environment?.name, config.viteEnvironments)
        ) {
          return;
        }
        await validateWebPOnly(config);
      },
    },
  };
}

/**
 * Validate that only WebP images exist in dist/client/assets
 * Fails the build if any PNG/JPG files are found
 */
async function validateWebPOnly(config: ImageConfig): Promise<void> {
  const assetsDir = resolve(process.cwd(), config.distAssetsDir);

  if (!fs.existsSync(assetsDir)) {
    return;
  }

  const nonWebPFiles: string[] = [];

  await scanDirectory(
    assetsDir,
    (entry) => isNonWebPImage(entry.name),
    (fullPath) => nonWebPFiles.push(path.relative(process.cwd(), fullPath)),
    config.scanConcurrency,
  );

  if (nonWebPFiles.length > 0) {
    const fileList = nonWebPFiles.map((f) => `  - ${f}`).join("\n");
    throw new Error(
      `Non-WebP images found in build output:\n${fileList}\n\n` +
        `All images must be WebP format. Please convert these images or update references to use .webp extension.`,
    );
  }

  console.log(
    `[images] WebP validation passed: no PNG/JPG files in ${config.distAssetsDir}`,
  );
}

/**
 * Generate responsive image variants before build
 * Recursively scans baseDir for all images
 * Writes variants alongside source files so Vite can resolve references during build
 */
async function generateResponsiveImages(config: ImageConfig): Promise<void> {
  const baseDir = resolve(process.cwd(), config.baseDir);

  // Check if base directory exists
  if (!fs.existsSync(baseDir)) {
    console.log(
      `[images] Skipping responsive images: ${config.baseDir} not found`,
    );
    return;
  }

  const sourceImages: string[] = [];

  // Recursively find all source images
  await scanDirectory(
    baseDir,
    (entry) => {
      // Skip already resized variants
      if (entry.name.includes("-medium.") || entry.name.includes("-small.")) {
        return false;
      }
      return isSourceImage(entry.name);
    },
    (fullPath) => sourceImages.push(fullPath),
    config.scanConcurrency,
  );

  if (sourceImages.length === 0) {
    return;
  }

  // Build list of all image processing tasks
  interface ImageTask {
    sourcePath: string;
    outputPath: string;
    width: number;
    quality: number;
  }

  const tasks: ImageTask[] = [];
  for (const sourcePath of sourceImages) {
    const dir = path.dirname(sourcePath);
    const filename = path.basename(sourcePath);
    const baseName = getImageBaseName(filename);
    const responsiveConfig = getResponsiveConfig(
      sourcePath,
      config.responsiveConfigs,
    );

    for (const [sizeName, width] of Object.entries(responsiveConfig.sizes)) {
      const outputFilename = `${baseName}-${sizeName}.webp`;
      tasks.push({
        sourcePath,
        outputPath: path.join(dir, outputFilename),
        width,
        quality: responsiveConfig.quality,
      });
    }
  }

  console.log(
    `[images] Generating ${tasks.length} responsive variants for ${sourceImages.length} image(s) in ${baseDir}...`,
  );

  // Process images in parallel batches
  const processTask = async (task: ImageTask): Promise<void> => {
    const buffer = await sharp(task.sourcePath)
      .resize({ width: task.width })
      .webp({ quality: task.quality })
      .toBuffer();

    await fsp.writeFile(task.outputPath, buffer);
    const relativePath = path.relative(process.cwd(), task.outputPath);
    if (config.verbose) {
      console.log(`[images] - ${relativePath}`);
    }
  };

  for (let i = 0; i < tasks.length; i += config.processConcurrency) {
    const batch = tasks.slice(i, i + config.processConcurrency);
    await Promise.all(batch.map(processTask));
  }

  console.log(`[images] Responsive image generation complete`);
}

/**
 * Create middleware for on-demand image processing
 */
function createImageMiddleware(
  config: ImageConfig,
): Connect.NextHandleFunction {
  return (req, res, next) => {
    void handleImageRequest(req, res, next, config);
  };
}

/**
 * Strip query parameters from a URL path
 */
function stripQueryParams(url: string): string {
  const queryIndex = url.indexOf("?");
  return queryIndex === -1 ? url : url.slice(0, queryIndex);
}

/**
 * Handle an image request - process and serve optimized WebP images
 */
async function handleImageRequest(
  req: IncomingMessage,
  res: ServerResponse,
  next: Connect.NextFunction,
  config: ImageConfig,
): Promise<void> {
  const url = req.url;
  if (!url) {
    next();
    return;
  }

  // Strip query parameters for path matching, but keep original URL for cache key
  // This supports cache-busting parameters like ?v=123
  const cleanUrl = stripQueryParams(url);

  // Skip non-WebP requests
  if (!isWebPRequest(cleanUrl)) {
    next();
    return;
  }

  // Check cache first (use original URL to support cache-busting)
  const cachedImage = imageCache.get(url);
  if (cachedImage) {
    serveImage(res, cachedImage);
    return;
  }

  try {
    const { originalFilePath, size } = parseImageRequest(cleanUrl);

    if (!originalFilePath) {
      console.log(`[images] Original image not found for: ${url}`);
      next();
      return;
    }

    const imageBuffer = await processImage(
      originalFilePath,
      size,
      config.responsiveConfigs,
    );
    imageCache.set(url, imageBuffer);
    serveImage(res, imageBuffer);
  } catch (error) {
    console.error(`[images] Error processing image ${url}:`, error);
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
  responsiveConfigs: ResponsiveConfig[],
): Promise<Buffer> {
  const config = getResponsiveConfig(filePath, responsiveConfigs);
  let processor = sharp(filePath);

  if (size !== "large") {
    const width = config.sizes[size];
    processor = processor.resize({ width });
  }

  return processor.webp({ quality: config.quality }).toBuffer();
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
    console.error(`[images] Invalid image request: ${url}`);
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
