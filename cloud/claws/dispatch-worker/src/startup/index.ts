/**
 * Startup orchestrator for OpenClaw in Cloudflare Sandbox.
 *
 * Coordinates the startup sequence:
 * 1. Check if gateway is already running
 * 2. Create directories
 * 3. Restore config from R2 (non-fatal)
 * 4. Build openclaw.json from environment
 * 5. Persist config to R2 (non-fatal)
 * 6. Start the gateway
 *
 * Each step delegates to focused, testable modules.
 */

export {
  buildConfig,
  buildAllowedOrigins,
  redactConfig,
  logEnvironment,
} from "./config-builder";
export type { StartupEnv, OpenClawStartupConfig } from "./config-builder";
export {
  restoreFromR2,
  persistToR2,
  syncFileToR2,
  isRcloneConfigured,
} from "./r2-sync";
export type { R2SyncResult } from "./r2-sync";
export {
  isGatewayRunning,
  checkBinary,
  buildGatewayArgs,
  redactArgs,
  cleanupLockFiles,
  startGateway,
} from "./gateway";
export type { GatewayResult } from "./gateway";
export { log, logError } from "./logger";
