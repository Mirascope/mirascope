/**
 * R2 persistence via rclone.
 *
 * Provides restore (R2 → local) and persist (local → R2) operations.
 * Both are non-fatal — the gateway should start regardless of R2 status.
 */

import { execSync } from "child_process";
import { existsSync, readFileSync } from "fs";

import { log, logError } from "./logger";

// ============================================================
// Constants
// ============================================================

const RCLONE_CONF_PATH = "/root/.config/rclone/rclone.conf";
const RCLONE_FLAGS = "--transfers=16 --fast-list --s3-no-check-bucket";
const RCLONE_EXCLUDE =
  "--exclude='*.lock' --exclude='*.log' --exclude='*.tmp' --exclude='.git/**'";
const RCLONE_TIMEOUT = 30000;

// ============================================================
// Helpers
// ============================================================

/**
 * Check if rclone is configured (config file exists).
 */
export function isRcloneConfigured(): boolean {
  const exists = existsSync(RCLONE_CONF_PATH);
  log(`rclone config exists at ${RCLONE_CONF_PATH}: ${exists}`);
  if (exists) {
    try {
      const content = readFileSync(RCLONE_CONF_PATH, "utf8");
      log("rclone config size:", { bytes: content.length });
    } catch (err) {
      logError("Failed to read rclone config", err);
    }
  }
  return exists;
}

// ============================================================
// Operations
// ============================================================

export interface R2SyncResult {
  success: boolean;
  skipped: boolean;
  reason?: string;
  error?: string;
}

/**
 * Restore config from R2 to local directory.
 * Non-fatal — returns result instead of throwing.
 */
export function restoreFromR2(
  bucket: string | undefined,
  configDir: string,
): R2SyncResult {
  if (!bucket) {
    return { success: true, skipped: true, reason: "R2_BUCKET_NAME not set" };
  }

  if (!isRcloneConfigured()) {
    return { success: true, skipped: true, reason: "rclone not configured" };
  }

  try {
    const cmd = `rclone sync r2:${bucket}/openclaw/ ${configDir}/ ${RCLONE_FLAGS}`;
    log("Running rclone restore:", { cmd });
    const output = execSync(cmd, { stdio: "pipe", timeout: RCLONE_TIMEOUT })
      .toString()
      .trim();
    if (output) log("rclone restore output:", { output });
    return { success: true, skipped: false };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    logError("R2 restore failed (non-fatal)", err);
    return { success: false, skipped: false, error: msg };
  }
}

/**
 * Persist config from local directory to R2.
 * Non-fatal — returns result instead of throwing.
 */
export function persistToR2(
  bucket: string | undefined,
  configDir: string,
): R2SyncResult {
  if (!bucket) {
    return { success: true, skipped: true, reason: "R2_BUCKET_NAME not set" };
  }

  if (!isRcloneConfigured()) {
    return { success: true, skipped: true, reason: "rclone not configured" };
  }

  try {
    const cmd = `rclone sync ${configDir}/ r2:${bucket}/openclaw/ ${RCLONE_FLAGS} ${RCLONE_EXCLUDE}`;
    log("Running rclone persist:", { cmd });
    const output = execSync(cmd, { stdio: "pipe", timeout: RCLONE_TIMEOUT })
      .toString()
      .trim();
    if (output) log("rclone persist output:", { output });
    return { success: true, skipped: false };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    logError("R2 persist failed (non-fatal)", err);
    return { success: false, skipped: false, error: msg };
  }
}

/**
 * Sync a single file to R2 (best effort, e.g. gateway log).
 */
export function syncFileToR2(
  bucket: string | undefined,
  filePath: string,
): void {
  if (!bucket || !isRcloneConfigured()) return;

  try {
    log("Syncing file to R2:", { filePath });
    execSync(`rclone copy ${filePath} r2:${bucket}/ ${RCLONE_FLAGS}`, {
      stdio: "pipe",
      timeout: 10000,
    });
    log("File synced to R2");
  } catch {
    log("Failed to sync file to R2 (best effort, ignoring)");
  }
}
