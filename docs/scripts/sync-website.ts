#!/usr/bin/env bun

import { existsSync, rmSync } from "fs";
import { mkdir, cp } from "fs/promises";
import { resolve, relative } from "path";
import { spawnSync } from "child_process";
import chokidar from "chokidar";

const REPO_URL = "https://github.com/mirascope/website.git";
const BRANCH = "main";
const CACHE_DIR = resolve(process.cwd(), ".build-cache/mirascope-website");
const DEST_BASE = resolve(CACHE_DIR, "content/docs/mirascope/v2");
const V2_ROOT = resolve(process.cwd(), "..");

// Define source/destination pairs to sync
const SYNC_PATHS = [
  { src: "docs/content", dest: DEST_BASE },
  { src: "python/examples", dest: resolve(DEST_BASE, "examples") },
];

function run(command: string, args: string[], cwd?: string): void {
  const result = spawnSync(command, args, {
    cwd: cwd || process.cwd(),
    stdio: "inherit",
    shell: false,
  });

  if (result.error) {
    throw new Error(`Failed to execute ${command}: ${result.error.message}`);
  }

  if (result.status !== 0) {
    throw new Error(
      `Command failed with exit code ${result.status}: ${command} ${args.join(
        " "
      )}`
    );
  }
}

async function syncWebsite(): Promise<void> {
  console.log("Syncing content to website repository...");

  if (existsSync(CACHE_DIR)) {
    console.log(`Updating existing repository at ${CACHE_DIR}...`);
    run("git", ["fetch", "origin"], CACHE_DIR);
    run("git", ["checkout", BRANCH], CACHE_DIR);
    run("git", ["reset", "--hard", `origin/${BRANCH}`], CACHE_DIR);
  } else {
    console.log(`Cloning website repository to ${CACHE_DIR}...`);
    await mkdir(resolve(CACHE_DIR, ".."), { recursive: true });
    run("git", ["clone", "--branch", BRANCH, REPO_URL, CACHE_DIR]);
  }

  if (existsSync(DEST_BASE)) {
    rmSync(DEST_BASE, { recursive: true, force: true });
  }

  for (const { src, dest } of SYNC_PATHS) {
    const sourcePath = resolve(V2_ROOT, src);

    if (!existsSync(sourcePath)) {
      console.warn(`⚠️  Source path not found, skipping: ${sourcePath}`);
      continue;
    }

    console.log(`Copying ${src} to ${dest}...`);
    await mkdir(dest, { recursive: true });
    await cp(sourcePath, dest, { recursive: true });
  }

  console.log("✓ Content sync complete");

  // Generate API documentation
  console.log("\nGenerating API documentation...");
  generateApiDocs();

  console.log("✓ API documentation generated");
}

function generateApiDocs(): void {
  const pythonSourcePath = resolve(V2_ROOT, "python");
  const apiDocsOutput = resolve(DEST_BASE, "api");

  run(
    "bun",
    [
      "run",
      "generate-api-docs",
      "--source-path",
      pythonSourcePath,
      "--package",
      "mirascope.llm",
      "--output",
      apiDocsOutput,
    ],
    CACHE_DIR
  );
}

function startWatching(): void {
  console.log("\n👀 Watching for content changes...");

  // Ensure the cache directory exists before watching
  if (!existsSync(CACHE_DIR)) {
    console.error(`❌ Cache directory not found: ${CACHE_DIR}`);
    console.error("Please run 'bun run prepare-website' first.");
    process.exit(1);
  }

  const watchers: chokidar.FSWatcher[] = [];

  // Cleanup function to close all watchers
  const cleanup = async () => {
    console.log("\n🛑 Shutting down watchers...");
    await Promise.all(watchers.map((w) => w.close()));
    process.exit(0);
  };

  // Register cleanup handlers
  process.on("SIGINT", cleanup); // Ctrl+C
  process.on("SIGTERM", cleanup); // kill command

  for (const { src, dest } of SYNC_PATHS) {
    const sourcePath = resolve(V2_ROOT, src);

    if (!existsSync(sourcePath)) {
      console.warn(`⚠️  Source path not found, skipping watch: ${sourcePath}`);
      continue;
    }

    if (!existsSync(dest)) {
      console.error(`❌ Destination not found: ${dest}`);
      console.error("Please run 'bun run prepare-website' first.");
      process.exit(1);
    }

    const watcher = chokidar.watch(sourcePath, {
      persistent: true,
      ignoreInitial: true, // Don't trigger events for existing files
      awaitWriteFinish: {
        stabilityThreshold: 100, // Wait 100ms after last change
        pollInterval: 50,
      },
    });

    watchers.push(watcher);

    watcher.on("add", async (filePath) => {
      await handleFileChange(filePath, sourcePath, dest, "add");
    });

    watcher.on("change", async (filePath) => {
      await handleFileChange(filePath, sourcePath, dest, "change");
    });

    watcher.on("unlink", async (filePath) => {
      await handleFileDelete(filePath, sourcePath, dest);
    });

    watcher.on("addDir", async (dirPath) => {
      const relativePath = relative(sourcePath, dirPath);
      const destDir = resolve(dest, relativePath);
      await mkdir(destDir, { recursive: true });
    });

    watcher.on("unlinkDir", async (dirPath) => {
      const relativePath = relative(sourcePath, dirPath);
      const destDir = resolve(dest, relativePath);
      if (existsSync(destDir)) {
        rmSync(destDir, { recursive: true, force: true });
        console.log(`🗑️  Deleted directory: ${relative(V2_ROOT, dirPath)}`);
      }
    });

    console.log(`  Watching: ${relative(V2_ROOT, sourcePath)}`);
  }

  // Watch Python source for API doc regeneration
  const pythonSourcePath = resolve(V2_ROOT, "python/mirascope");

  if (existsSync(pythonSourcePath)) {
    let regenerateTimeout: NodeJS.Timeout | null = null;
    const REGENERATE_DEBOUNCE_MS = 200;

    const pythonWatcher = chokidar.watch(pythonSourcePath, {
      persistent: true,
      ignoreInitial: true,
      awaitWriteFinish: {
        stabilityThreshold: 100,
        pollInterval: 50,
      },
      ignored: [
        "**/node_modules/**",
        "**/__pycache__/**",
        "**/*.pyc",
        "**/.*", // Ignore hidden files
        "**/dist/**",
        "**/build/**",
      ],
    });

    watchers.push(pythonWatcher);

    const regenerateApiDocs = async () => {
      console.log("\nRegenerating API documentation...");
      try {
        generateApiDocs();
        console.log("✓ API documentation regenerated");
      } catch (error) {
        console.error(
          "❌ Failed to regenerate API docs:",
          error instanceof Error ? error.message : error
        );
      }
    };

    const handlePythonChange = async (filePath: string, eventType: string) => {
      // Only regenerate for .py files
      if (!filePath.endsWith(".py")) return;

      console.log(
        `🔄 Python file ${eventType}: ${relative(V2_ROOT, filePath)}`
      );

      // Clear existing timeout and set a new one
      if (regenerateTimeout) {
        clearTimeout(regenerateTimeout);
      }

      regenerateTimeout = setTimeout(regenerateApiDocs, REGENERATE_DEBOUNCE_MS);
    };

    pythonWatcher.on("add", async (filePath) => {
      await handlePythonChange(filePath, "added");
    });

    pythonWatcher.on("change", async (filePath) => {
      await handlePythonChange(filePath, "changed");
    });

    pythonWatcher.on("unlink", async (filePath) => {
      await handlePythonChange(filePath, "deleted");
    });

    console.log(
      `  Watching Python source: ${relative(V2_ROOT, pythonSourcePath)}`
    );
  } else {
    console.warn(`⚠️  Python source not found: ${pythonSourcePath}`);
  }

  console.log("\n✓ Watching started. Press Ctrl+C to stop.\n");
}

async function handleFileChange(
  filePath: string,
  sourcePath: string,
  dest: string,
  eventType: "add" | "change"
): Promise<void> {
  try {
    const relativePath = relative(sourcePath, filePath);
    const destFile = resolve(dest, relativePath);

    // Ensure parent directory exists
    await mkdir(resolve(destFile, ".."), { recursive: true });
    await cp(filePath, destFile);

    const action = eventType === "add" ? "Added" : "Updated";
    console.log(`📝 ${action}: ${relative(V2_ROOT, filePath)}`);
  } catch (error) {
    console.error(
      `❌ Error processing ${relative(V2_ROOT, filePath)}:`,
      error instanceof Error ? error.message : error
    );
  }
}

async function handleFileDelete(
  filePath: string,
  sourcePath: string,
  dest: string
): Promise<void> {
  try {
    const relativePath = relative(sourcePath, filePath);
    const destFile = resolve(dest, relativePath);

    if (existsSync(destFile)) {
      rmSync(destFile, { recursive: true, force: true });
      console.log(`🗑️  Deleted: ${relative(V2_ROOT, filePath)}`);
    }
  } catch (error) {
    console.error(
      `❌ Error deleting ${relative(V2_ROOT, filePath)}:`,
      error instanceof Error ? error.message : error
    );
  }
}

const args = process.argv.slice(2);
const shouldWatch = args.includes("--watch");
const skipInitialSync = args.includes("--skip-initial-sync");

const runSync = skipInitialSync ? Promise.resolve() : syncWebsite();

runSync
  .then(() => {
    if (shouldWatch) {
      startWatching();
    }
  })
  .catch((error) => {
    console.error("Error syncing website:", error.message);
    process.exit(1);
  });
