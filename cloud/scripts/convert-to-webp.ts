#!/usr/bin/env bun
/**
 * Script to convert PNG/JPG images to WebP format
 * This helps reduce repository size and speeds up builds
 */
import fs from "fs";
import path from "path";
import { glob } from "glob";
import sharp from "sharp";
import { printHeader, icons, coloredLog } from "./lib/terminal";

interface ConversionStats {
  converted: number;
  skipped: number;
  errors: number;
  sizeBefore: number;
  sizeAfter: number;
}

/**
 * Convert image to WebP format
 */
async function convertImageToWebP(
  filePath: string,
  quality: number = 95,
  removeOriginal: boolean = true,
): Promise<boolean> {
  try {
    // Generate WebP output path
    const fileExt = path.extname(filePath);
    const baseName = path.basename(filePath, fileExt);
    const dirName = path.dirname(filePath);
    const webpPath = path.join(dirName, `${baseName}.webp`);

    console.log(`🔄 Converting: ${filePath} -> ${webpPath}`);

    // Process the image with sharp
    await sharp(filePath).webp({ quality }).toFile(webpPath);

    // Optionally remove the original file
    if (removeOriginal) {
      fs.unlinkSync(filePath);
      console.log(`   ✅ Removed original: ${filePath}`);
    }

    return true;
  } catch (error) {
    console.error(`❌ Error converting ${filePath}:`, error);
    return false;
  }
}

/**
 * Convert all PNG/JPG files in the public/assets directory to WebP
 */
async function convertToWebP(
  options: {
    sourcePath?: string;
    quality?: number;
    removeOriginals?: boolean;
    verbose?: boolean;
  } = {},
): Promise<ConversionStats> {
  const {
    sourcePath = "public/assets",
    quality = 80,
    removeOriginals = true,
  } = options;

  printHeader("Converting Images to WebP");
  console.log(`📁 Source directory: ${sourcePath}`);
  console.log(`⚙️  Quality: ${quality}`);
  console.log(`🗑️  Remove originals: ${removeOriginals ? "Yes" : "No"}`);

  // Find all PNG/JPG images
  const imagePatterns = "**/*.{png,jpg,jpeg}";
  const imagePaths = await glob(path.join(sourcePath, imagePatterns), {
    absolute: true,
  });

  console.log(`\n🔍 Found ${imagePaths.length} images to convert`);

  // Process stats
  const stats: ConversionStats = {
    converted: 0,
    skipped: 0,
    errors: 0,
    sizeBefore: 0,
    sizeAfter: 0,
  };

  // Process each image
  for (const imagePath of imagePaths) {
    // Get file stats before conversion
    try {
      const fileStats = fs.statSync(imagePath);
      stats.sizeBefore += fileStats.size;

      // Convert image
      const success = await convertImageToWebP(
        imagePath,
        quality,
        removeOriginals,
      );

      if (success) {
        stats.converted++;

        // Get size of WebP version
        const webpPath = imagePath.replace(/\.(png|jpg|jpeg)$/i, ".webp");
        if (fs.existsSync(webpPath)) {
          const webpStats = fs.statSync(webpPath);
          stats.sizeAfter += webpStats.size;
        }
      } else {
        stats.errors++;
      }
    } catch (error) {
      console.error(`❌ Error processing ${imagePath}:`, error);
      stats.errors++;
    }
  }

  // Calculate savings
  const savingsBytes = stats.sizeBefore - stats.sizeAfter;
  const savingsPercent = stats.sizeBefore
    ? ((savingsBytes / stats.sizeBefore) * 100).toFixed(1)
    : "0";
  const sizeBefore = (stats.sizeBefore / (1024 * 1024)).toFixed(2);
  const sizeAfter = (stats.sizeAfter / (1024 * 1024)).toFixed(2);

  // Output results
  coloredLog("\n🎉 Conversion complete!", "green");
  console.log(
    `📊 Converted: ${stats.converted} images, Errors: ${stats.errors}`,
  );
  console.log(
    `💾 Size reduction: ${sizeBefore} MB → ${sizeAfter} MB (${savingsPercent}% saved)`,
  );

  return stats;
}

/**
 * Main function to run the script
 */
async function main() {
  const args = process.argv.slice(2);
  const verbose = args.includes("--verbose");
  const noRemove = args.includes("--no-remove");
  const qualityArg = args.find((arg) => arg.startsWith("--quality="));
  const quality = qualityArg
    ? parseInt(qualityArg.split("=")[1], 10)
    : undefined;

  try {
    await convertToWebP({
      quality,
      removeOriginals: !noRemove,
      verbose,
    });
  } catch (error) {
    coloredLog(`${icons.error} Error converting images:`, "red");
    console.error(error);
    process.exit(1);
  }
}

// Run the script if invoked directly
if (import.meta.path === Bun.main) {
  await main();
}

// Export for use in other scripts
export { convertToWebP };
