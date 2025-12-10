#!/usr/bin/env bun

import { existsSync, rmSync } from "fs";
import { mkdir, cp } from "fs/promises";
import { resolve } from "path";
import { spawnSync } from "child_process";

const REPO_URL = "https://github.com/mirascope/mirascope.git";
const BRANCH = "v2";
const CACHE_DIR = resolve(process.cwd(), ".build-cache/mirascope");
const DEST_BASE = resolve(process.cwd(), "content/docs/mirascope/v2");

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
    throw new Error(`Command failed with exit code ${result.status}: ${command} ${args.join(" ")}`);
  }
}

async function syncDocs(): Promise<void> {
  console.log("Syncing docs from mirascope repository...");

  // Clone or update repository
  if (existsSync(CACHE_DIR)) {
    console.log(`Updating existing repository at ${CACHE_DIR}...`);
    run("git", ["fetch", "origin"], CACHE_DIR);
    run("git", ["checkout", BRANCH], CACHE_DIR);
    run("git", ["reset", "--hard", `origin/${BRANCH}`], CACHE_DIR);
  } else {
    console.log(`Cloning repository to ${CACHE_DIR}...`);
    await mkdir(resolve(CACHE_DIR, ".."), { recursive: true });
    run("git", ["clone", "--branch", BRANCH, REPO_URL, CACHE_DIR]);
  }

  // Clean destination base directory
  if (existsSync(DEST_BASE)) {
    rmSync(DEST_BASE, { recursive: true, force: true });
  }

  // Sync each path
  for (const { src, dest } of SYNC_PATHS) {
    const sourcePath = resolve(CACHE_DIR, src);

    if (!existsSync(sourcePath)) {
      console.warn(`⚠️  Source path not found, skipping: ${sourcePath}`);
      continue;
    }

    console.log(`Copying ${src} to ${dest}...`);
    await mkdir(dest, { recursive: true });
    await cp(sourcePath, dest, { recursive: true });
  }

  console.log("✓ Docs sync complete");
}

syncDocs().catch((error) => {
  console.error("Error syncing docs:", error.message);
  process.exit(1);
});
