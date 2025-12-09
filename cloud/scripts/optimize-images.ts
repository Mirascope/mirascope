#!/usr/bin/env bun
/**
 * Image Optimization Script
 *
 * This script optimizes WebP images in the public directory:
 * 1. Verifies all images are WebP format (fails if not)
 * 2. Creates medium and small responsive versions of WebP images
 * 3. Assumes base WebP files already exist (using convert-to-webp.ts)
 */

import path from "path";
import fs from "fs";
import { glob } from "glob";
import sharp from "sharp";

// Configuration
const CONFIG = {
  // Directories to process - public for dev, dist for production builds
  baseDirectories: ["public/assets", "dist/assets"],

  // Responsive image configurations based on path patterns
  responsiveConfigs: [
    {
      // Background images get larger medium breakpoint
      pattern: /\/backgrounds\//,
      quality: 95,
      sizes: [
        { name: "medium", width: 1200 },
        { name: "small", width: 800 },
      ],
    },
    {
      // Default responsive sizes for all other images
      pattern: /.*/, // Match all paths
      quality: 80,
      sizes: [
        { name: "medium", width: 1024 },
        { name: "small", width: 640 },
      ],
    },
  ],

  // Skip patterns if needed in the future
  skipPatterns: [] as RegExp[],
};

// File counters
let stats = {
  processed: 0,
  skipped: 0,
  errors: 0,
};

/**
 * Get responsive image config based on file path
 * Returns the most specific pattern match first
 */
function getResponsiveConfig(filePath: string) {
  // Try to find a specific pattern match first
  // The default pattern (/.*//) should be last in the config array
  for (let i = 0; i < CONFIG.responsiveConfigs.length - 1; i++) {
    const config = CONFIG.responsiveConfigs[i];
    if (config.pattern.test(filePath)) {
      return config;
    }
  }

  // Use default pattern if no specific matches
  return CONFIG.responsiveConfigs[CONFIG.responsiveConfigs.length - 1];
}

/**
 * Check if a file should be skipped
 */
function shouldSkipFile(filePath: string): boolean {
  // Skip files that match skip patterns
  if (CONFIG.skipPatterns.some((pattern) => pattern.test(filePath))) {
    return true;
  }

  // Skip SVG and GIF files - we don't want to create responsive versions for these
  // They should be served as-is
  const extension = path.extname(filePath).toLowerCase();
  if ([".svg", ".gif"].includes(extension)) {
    return true;
  }

  // Skip files that already have responsive suffixes (e.g., light-small.webp, light-medium.webp)
  const baseName = path.basename(filePath, extension);
  if (baseName.match(/-(small|medium)$/)) {
    return true;
  }

  // Check that the file is WebP, fail otherwise
  if (extension !== ".webp") {
    throw new Error(
      `Non-WebP image found: ${filePath}\n` +
        `All images must be WebP format before running image optimization.\n` +
        `Please convert this image using 'bun run convert-to-webp'.\n` +
        `Run 'bun run validate-assets --skip-dist-check' to identify all PNG/JPG files that need conversion.`
    );
  }

  return false;
}

/**
 * Process a single image file
 */
async function processImage(filePath: string) {
  // Skip if matches any pattern in the excluded list
  if (shouldSkipFile(filePath)) {
    console.log(`⏭️  Skipping: ${filePath}`);
    stats.skipped++;
    return;
  }

  try {
    const fileExt = path.extname(filePath).toLowerCase();
    const baseName = path.basename(filePath, fileExt);
    const dirName = path.dirname(filePath);
    const config = getResponsiveConfig(filePath);

    console.log(`🖼️  Optimizing: ${filePath}`);

    for (const size of config.sizes) {
      const suffix = `-${size.name}`;
      const outputPath = path.join(dirName, `${baseName}${suffix}.webp`);

      try {
        let sharpInstance = sharp(filePath);

        sharpInstance = sharpInstance.resize({ width: size.width });

        await sharpInstance.webp({ quality: config.quality }).toFile(outputPath);
      } catch (error) {
        console.error(`❌  Error processing ${outputPath}:`, error);
        stats.errors++;
      }
    }

    stats.processed++;
  } catch (error) {
    console.error(`❌  Error processing ${filePath}:`, error);
    stats.errors++;
  }
}

/**
 * Main function to run the optimization
 */
async function main() {
  console.log("🚀 Starting image optimization...");

  const startTime = Date.now();

  // Collect all image files from all base directories
  let allImageFiles: string[] = [];

  for (const baseDirectory of CONFIG.baseDirectories) {
    // Skip directories that don't exist (e.g., dist during dev)
    if (!fs.existsSync(baseDirectory)) {
      console.log(`⏭️  Skipping ${baseDirectory} (does not exist)`);
      continue;
    }

    // Find all images recursively in the base directory
    const imageFiles = await glob(`${baseDirectory}/**/*.{png,jpg,jpeg,webp}`, {
      absolute: true,
    });
    console.log(`📁 Found ${imageFiles.length} images in ${baseDirectory}`);
    allImageFiles.push(...imageFiles);
  }

  if (allImageFiles.length === 0) {
    console.warn("⚠️  No images found in any of the configured directories.");
    console.warn(`   Checked: ${CONFIG.baseDirectories.join(", ")}`);
    return;
  }

  // Process images in parallel, but with a limit
  const batchSize = 5; // Process 5 images at a time
  for (let i = 0; i < allImageFiles.length; i += batchSize) {
    const batch = allImageFiles.slice(i, i + batchSize);
    await Promise.all(batch.map((file) => processImage(file)));
  }

  const endTime = Date.now();
  const durationSeconds = ((endTime - startTime) / 1000).toFixed(2);

  // Log results
  console.log("\n🎉 Responsive WebP generation complete!");
  console.log(`⏱️  Duration: ${durationSeconds}s`);
  console.log(
    `📊 Processed: ${stats.processed} images, Skipped: ${stats.skipped}, Errors: ${stats.errors}`
  );
  console.log(`🔍 Created ${stats.processed * 2} responsive versions (medium and small sizes)`);

  if (stats.errors > 0) {
    process.exit(1);
  }
}

// Run the script
main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
