#!/usr/bin/env bun

/**
 * Script to run TypeScript type checking regardless of what files were changed
 * This ensures we check the entire project graph, not just modified files
 *
 * Usage from lint-staged: "*.{ts,tsx}": ["bun scripts/check-ts.ts", "bun test"]
 */

import { execSync } from "child_process";

// Run the TypeScript check on the entire project, ignoring any specific paths
console.log("Running TypeScript check on the entire project...");

try {
  // Execute the type checking command - using the same as our lint:ts script
  execSync("bun run tsc --noEmit", { stdio: "inherit" });
  console.log("TypeScript check passed");
} catch (error) {
  console.error("TypeScript check failed!");
  process.exit(1);
}

try {
  // Execute the type checking command - using the same as our lint:ts script
  execSync("bun test", { stdio: "inherit" });
  console.log("TypeScript tests passed");
  process.exit(0);
} catch (error) {
  console.error("TypeScript tests failed!");
  process.exit(1);
}
