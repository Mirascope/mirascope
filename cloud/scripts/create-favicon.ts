#!/usr/bin/env bun
/**
 * Favicon Generator Script
 *
 * This script creates:
 * 1. favicon.png (32x32) - PNG fallback for Safari and browsers without SVG support
 * 2. apple-touch-icon.png (180x180) - For iOS devices
 * 3. Outputs the optimized inline SVG code for use in HTML
 */

import path from "path";
import fs from "fs";
import sharp from "sharp";

async function main() {
  console.log("🚀 Creating favicons from SVG...");

  const svgPath = path.join(process.cwd(), "public/assets/branding/mirascope-favicon.svg");

  try {
    // Create favicon.png (32x32) for Safari fallback
    const faviconPath = path.join(process.cwd(), "public/favicon.png");
    await sharp(svgPath).resize(32, 32).png().toFile(faviconPath);

    const faviconStats = fs.statSync(faviconPath);
    console.log(`✅ favicon.png created: ${(faviconStats.size / 1024).toFixed(2)}KB`);

    // Create apple-touch-icon.png (180x180) for iOS devices
    const appleTouchPath = path.join(process.cwd(), "public/apple-touch-icon.png");
    await sharp(svgPath).resize(180, 180).png().toFile(appleTouchPath);

    const appleTouchStats = fs.statSync(appleTouchPath);
    console.log(`✅ apple-touch-icon.png created: ${(appleTouchStats.size / 1024).toFixed(2)}KB`);

    // Generate the inline SVG code
    const svgContent = fs.readFileSync(svgPath, "utf8");

    // Create a minified version by removing comments, extra whitespace and unnecessary attributes
    const minifiedSvg = svgContent
      .replace(/<!--[\s\S]*?-->/g, "") // Remove XML comments
      .replace(/\s+/g, " ") // Collapse whitespace
      .replace(/>\s+</g, "><") // Remove whitespace between tags
      .trim();

    // Create a data URI-safe version
    const dataUriSvg = minifiedSvg
      .replace(/"/g, "'") // Convert double to single quotes
      .replace(/%/g, "%25") // Encode % signs
      .replace(/#/g, "%23") // Encode # signs
      .replace(/{/g, "%7B") // Encode { signs
      .replace(/}/g, "%7D") // Encode } signs
      .replace(/</g, "%3C") // Encode < signs
      .replace(/>/g, "%3E") // Encode > signs
      .replace(/\s+/g, " ") // Collapse remaining whitespace
      .trim();

    console.log("\n✅ All favicons created successfully!");
    console.log("\n📋 Use this code in your HTML <head> section:");
    console.log(`
<!-- PNG fallback for Safari and other browsers that don't support SVG -->
<link rel="icon" href="/favicon.png" sizes="32x32" type="image/png">

<!-- SVG favicon for modern browsers -->
<link rel="icon" href="data:image/svg+xml,${dataUriSvg}" type="image/svg+xml">

<!-- Apple Touch Icon for iOS devices -->
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
`);
  } catch (error) {
    console.error("❌ Error creating favicons:", error);
    process.exit(1);
  }
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
