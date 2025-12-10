#!/usr/bin/env bun
/**
 * Test script for router-utils.ts
 * This script will enumerate all routes detected by the router utility
 * and display them in different categories
 */
import {
  getStaticRoutes,
  getBlogRoutes,
  getDocsRoutes,
  getAllRoutes,
} from "../src/lib/router-utils";

// ANSI color codes for better output
const RESET = "\x1b[0m";
const GREEN = "\x1b[32m";
const YELLOW = "\x1b[33m";
const BLUE = "\x1b[34m";
const MAGENTA = "\x1b[35m";
const CYAN = "\x1b[36m";

// Print a section header
function printHeader(title: string, color: string = BLUE): void {
  console.log("\n" + color + "=".repeat(50) + RESET);
  console.log(color + ` ${title} ` + RESET);
  console.log(color + "=".repeat(50) + RESET);
}

// Print a list of routes
function printRoutes(routes: string[], color: string = RESET): void {
  if (routes.length === 0) {
    console.log("  No routes found");
    return;
  }

  routes.forEach((route, index) => {
    console.log(`  ${color}${index + 1}. ${route}${RESET}`);
  });
  console.log(`\n  Total: ${color}${routes.length} routes${RESET}`);
}

// Main function to run tests
async function main() {
  printHeader("TanStack Router Utils Test", CYAN);
  console.log("Testing the router-utils.ts utility to verify route extraction\n");

  try {
    // Test static routes extraction
    printHeader("Static Routes (extracted from TanStack Router)", GREEN);
    const staticRoutes = getStaticRoutes();
    printRoutes(staticRoutes, GREEN);

    // Test blog routes extraction
    printHeader("Blog Routes (from posts list)", YELLOW);
    const blogRoutes = await getBlogRoutes();
    printRoutes(blogRoutes, YELLOW);

    // Test docs routes extraction
    printHeader("Docs Routes (from _meta.ts)", MAGENTA);
    const docsRoutes = getDocsRoutes();
    printRoutes(docsRoutes, MAGENTA);

    // Test all routes combined
    printHeader("All Routes Combined", CYAN);
    const allRoutes = await getAllRoutes();
    printRoutes(allRoutes, CYAN);

    // Look for potential duplicates or inconsistencies
    printHeader("Potential Issues", YELLOW);

    // Check if there are any static routes in docs routes
    const staticInDocs = staticRoutes.filter(
      (route) => docsRoutes.includes(route) && route.startsWith("/docs")
    );

    if (staticInDocs.length > 0) {
      console.log(
        `${YELLOW}Found ${staticInDocs.length} static routes that overlap with docs routes:${RESET}`
      );
      staticInDocs.forEach((route) => console.log(`  - ${route}`));
    } else {
      console.log(`${GREEN}No overlaps found between static and docs routes${RESET}`);
    }

    console.log("\n" + CYAN + "=".repeat(50) + RESET);
    console.log(`${GREEN}Test completed successfully!${RESET}`);
  } catch (error) {
    console.error(`\n${YELLOW}Error testing router utils:${RESET}`, error);
    process.exit(1);
  }
}

// Run the main function
main().catch((error) => {
  console.error("Unhandled error:", error);
  process.exit(1);
});
