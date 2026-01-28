#!/usr/bin/env bun

/**
 * Generate Python code snippets from MDX documentation.
 *
 * It always:
 * - Cleans the output directory
 * - Extracts all snippets from mdx files in the content directory
 * - Outputs to .extracted-snippets directory (not checked into git)
 *
 * Usage:
 *   bun run scripts/generate-snippets                    # Generate all snippets (excludes blog)
 *   bun run scripts/generate-snippets --blog             # Generate snippets from blog posts only
 *   bun run scripts/generate-snippets --file=<path>      # Generate snippets from a single file
 *   bun run scripts/generate-snippets --verbose          # Show more detailed output
 *
 * Exit codes:
 *   0: Success (all snippets generated)
 *   1: Error (some snippets failed to generate)
 */

import * as fs from "fs/promises";
import * as path from "path";

/**
 * Check if a path exists (async replacement for fs.existsSync)
 */
async function pathExists(filePath: string): Promise<boolean> {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

// Import our low-level extraction functions
import { processFile } from "../app/lib/snippet-extractor";

// Root directory for extracted snippets (changed to .extracted-snippets)
const SNIPPETS_ROOT = path.join(process.cwd(), ".extracted-snippets");

// Docs root directory
const CONTENT_ROOT = path.join(process.cwd(), "../content");

const IGNORED_PATHS = [
  "content/blog", // 434 errors
  "content/docs/v1/guides/getting-started", // 62 errors
  "content/docs/v1/guides/agents", // 197 errors
  "content/docs/v1/guides/evals", // 117 errors
  "content/docs/v1/guides/more-advanced", // 281 errors
  "content/docs/v1/guides/prompt-engineering", // 86 errors
  "content/docs/v1/guides/langgraph-vs-mirascope", // 111 errors
  "content/docs/v1/api", // 76 errors
  "content/dev",
];

/**
 * Recursively find all MDX files in a directory
 */
async function findMdxFilesRecursive(
  directory: string,
  relativePath: string = "",
): Promise<string[]> {
  const paths: string[] = [];

  // Read all entries in the directory
  const entries = await fs.readdir(directory, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(directory, entry.name);
    const relPath = relativePath
      ? path.join(relativePath, entry.name)
      : entry.name;

    if (entry.isDirectory()) {
      // Skip node_modules and hidden directories
      if (entry.name === "node_modules" || entry.name.startsWith(".")) {
        continue;
      }

      // Recursively scan subdirectories
      paths.push(...(await findMdxFilesRecursive(fullPath, relPath)));
    } else if (entry.isFile() && entry.name.endsWith(".mdx")) {
      paths.push(fullPath);
    }
  }

  return paths;
}

/**
 * Generate snippets for a single doc
 */
async function generateDocSnippets(
  filePath: string,
  contentRoot: string,
  verbose = false,
): Promise<boolean> {
  try {
    // Extract new snippets
    const files = await processFile(filePath, contentRoot);

    if (files.length > 0) {
      if (verbose) {
        console.log(`Generated ${files.length} snippets for ${filePath}`);
      }
      return true;
    } else {
      if (verbose) {
        // Since we try generating snippets for every mdx file, this is expected.
        console.log(`No snippets found in ${filePath}`);
      }
      return true;
    }
  } catch (error) {
    if (
      error instanceof Error &&
      error.message.includes("Unsupported Python block type")
    ) {
      // Provide a clearer error message for unsupported block types
      console.error(`Error in ${filePath}: ${error.message}`);
      console.error("Make sure to use only these block types:");
      console.error(
        "  ```python (or ```py)           - Standard Python block for extraction",
      );
      console.error(
        "  ```python-snippet-concat (or ```py-snippet-concat) - To concat with the previous Python block",
      );
      console.error(
        "  ```python-snippet-skip (or ```py-snippet-skip)   - Python code that should not be extracted",
      );
    } else {
      console.error(`Error generating snippets for ${filePath}:`, error);
    }
    return false;
  }
}

/**
 * Clean the output directory
 */
async function cleanOutputDirectory(): Promise<void> {
  if (await pathExists(SNIPPETS_ROOT)) {
    console.log(`Cleaning output directory: ${SNIPPETS_ROOT}`);
    await fs.rm(SNIPPETS_ROOT, { recursive: true, force: true });
  }

  // Recreate the directory
  await fs.mkdir(SNIPPETS_ROOT, { recursive: true });
}

/**
 * Main function
 */
async function main(): Promise<number> {
  const verbose = process.argv.includes("--verbose");
  const blogOnly = process.argv.includes("--blog");
  const fileArg = process.argv.find((arg) => arg.startsWith("--file="));

  // Check for help flag
  if (process.argv.includes("--help") || process.argv.includes("-h")) {
    console.log("Usage: bun run scripts/generate-snippets [options]");
    console.log("");
    console.log("Options:");
    console.log("  --verbose       Show more detailed output");
    console.log("  --blog          Process only blog posts (content/blog)");
    console.log("  --file=<path>   Process a single MDX file");
    console.log("  --help          Show this help message");
    return 0;
  }

  // Always clean the output directory first
  await cleanOutputDirectory();

  // Handle single file mode
  if (fileArg) {
    const filePath = fileArg.substring("--file=".length);
    const absolutePath = path.isAbsolute(filePath)
      ? filePath
      : path.join(process.cwd(), filePath);

    if (!(await pathExists(absolutePath))) {
      console.error(`Error: File not found: ${absolutePath}`);
      return 1;
    }

    console.log(`Processing single file: ${absolutePath}`);
    const success = await generateDocSnippets(
      absolutePath,
      CONTENT_ROOT,
      verbose,
    );
    return success ? 0 : 1;
  }

  // Find all extractable docs
  let paths = await findMdxFilesRecursive(CONTENT_ROOT);

  // Apply filtering based on mode
  if (blogOnly) {
    // Blog mode: only process content/blog
    paths = paths.filter((p) => p.includes("content/blog"));
    console.log(`Blog mode: processing only content/blog`);
  } else {
    // Normal mode: apply IGNORED_PATHS
    paths = paths.filter(
      (p) => !IGNORED_PATHS.some((ignoredPath) => p.includes(ignoredPath)),
    );
  }

  if (paths.length === 0) {
    console.warn("No MDX documents found for snippet extraction.");
    return 0; // Exit success, since there's nothing to do
  }

  console.log(`Found ${paths.length} MDX documents for snippet extraction.`);
  console.log("Generating snippets...");

  // Generate snippets for each doc
  let allSuccessful = true;
  for (const filePath of paths) {
    const success = await generateDocSnippets(filePath, CONTENT_ROOT, verbose);
    allSuccessful = allSuccessful && success;
  }

  if (allSuccessful) {
    console.log("All snippets generated successfully.");
    return 0;
  } else {
    console.error("Some snippets failed to generate.");
    return 1;
  }
}

// Run the main function and exit with the appropriate code
void main().then((code) => process.exit(code));
