#!/usr/bin/env bun

import { existsSync, rmSync } from "fs";
import { mkdir, cp } from "fs/promises";
import { resolve } from "path";
import { spawnSync } from "child_process";

const REPO_URL = "https://github.com/mirascope/website.git";
const BRANCH = "10-23-feat_pull_in_v2_content_from_real_repo";
const CACHE_DIR = resolve(process.cwd(), ".build-cache/mirascope-website");
const DEST_BASE = resolve(CACHE_DIR, "content/docs/mirascope-v2");
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

  // Clone or update website repository
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

  // Clean destination base directory
  if (existsSync(DEST_BASE)) {
    rmSync(DEST_BASE, { recursive: true, force: true });
  }

  // Sync each path
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
}

syncWebsite().catch((error) => {
  console.error("Error syncing website:", error.message);
  process.exit(1);
});
