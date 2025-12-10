#!/usr/bin/env bun
import { prerenderPage } from "./lib/prerender";
import path from "path";

/**
 * CLI script to prerender a route to static HTML
 *
 * Usage: bun run prerender /route/path [--output-dir=path/to/dir]
 */
async function main() {
  // Get command-line arguments
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === "--help" || args[0] === "-h") {
    console.log(`
Prerender a route to static HTML

Usage: 
  bun run prerender /route/path [--output-dir=path/to/dir] [--verbose]

Arguments:
  /route/path            The route to prerender (e.g., /privacy, /blog)
  
Options:
  --output-dir=DIR       Directory to write files to (default: public/ssg)
  --verbose              Show detailed logs
  --help, -h             Show this help
`);
    process.exit(0);
  }

  // Parse arguments and options
  const route = args[0];
  const outputDirArg = args.find((arg) => arg.startsWith("--output-dir="));
  const verbose = args.includes("--verbose");

  // Default output directory is dist
  let outputDir = path.join(process.cwd(), "dist");

  // Parse output directory if provided
  if (outputDirArg) {
    outputDir = outputDirArg.replace("--output-dir=", "");
    // Handle both absolute and relative paths
    if (!path.isAbsolute(outputDir)) {
      outputDir = path.join(process.cwd(), outputDir);
    }
  }

  try {
    // Ensure the route starts with a slash
    const normalizedRoute = route.startsWith("/") ? route : `/${route}`;

    // Prerender the page
    console.log(`Prerendering ${normalizedRoute} to ${outputDir}...`);
    const outputPath = await prerenderPage(normalizedRoute, outputDir, verbose);

    console.log(`✅ Successfully prerendered to ${outputPath}`);
    process.exit(0);
  } catch (error) {
    console.error("❌ Prerendering failed:", error);
    process.exit(1);
  }
}

// Run the script
main();
