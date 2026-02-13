/**
 * Claw Deployment Types
 *
 * These types define the contract between Mirascope Cloud and the dispatch worker
 * that manages claw containers on Cloudflare.
 */

/**
 * Container instance types available for claws.
 * Maps to Cloudflare container configurations.
 */
export type ClawInstanceType =
  | "lite" // 1/16 vCPU, 256 MiB RAM, 2 GB disk - Testing only
  | "basic" // 1/4 vCPU, 1 GiB RAM - Free tier
  | "standard-1" // 1/2 vCPU, 2 GiB RAM
  | "standard-2" // 1 vCPU, 6 GiB RAM - Pro tier (default)
  | "standard-3" // 2 vCPU, 8 GiB RAM - Team tier
  | "standard-4"; // 4 vCPU, 12 GiB RAM - Power users

/**
 * Claw deployment status.
 */
export type ClawStatus =
  | "pending" // Created but not yet provisioned
  | "provisioning" // Container is being created
  | "active" // Running and healthy
  | "paused" // Stopped (can be restarted)
  | "error"; // Failed, see errorMessage

/**
 * R2 storage configuration for a claw.
 *
 * Each claw gets its own R2 bucket with credentials scoped to that bucket only.
 * Used by dispatch worker for:
 * - Mounting persistent storage in the container
 * - Versioning operations (snapshot/rollback of .openclaw/ directory)
 */
export interface ClawR2Config {
  /** R2 bucket name for this claw's persistent storage */
  bucketName: string;

  /**
   * SECRET: Do not store unencrypted. Only passed at runtime.
   */
  accessKeyId: string;

  /**
   * SECRET: Do not store unencrypted. Only passed at runtime.
   */
  secretAccessKey: string;
}

/**
 * Minimal config needed to provision infrastructure for a claw.
 *
 * Used by `ClawDeploymentService.provision()` — only the claw ID and instance
 * type are needed since R2 bucket/credentials are *created* during provisioning
 * and the internal hostname is derived from the clawId.
 */
export interface ProvisionClawConfig {
  /** Unique identifier for the claw */
  clawId: string;

  /** Container instance type determining resources */
  instanceType: ClawInstanceType;
}

/**
 * Configuration for running an OpenClaw container.
 *
 * This is the "live" config passed to the dispatch worker at runtime, NOT the
 * DB representation. Secrets are decrypted by Mirascope before being included here.
 *
 * The dispatch worker fetches this when it needs to start or configure a claw's
 * container.
 *
 * @endpoint GET /api/internal/claws/:clawId/bootstrap
 */
export interface OpenClawDeployConfig extends ProvisionClawConfig {
  /** URL-safe slug for the claw (used in hostname) */
  clawSlug: string;

  /** Organization that owns this claw */
  organizationId: string;

  /** URL-safe slug for the organization (used in hostname) */
  organizationSlug: string;

  /** R2 storage configuration (includes credentials) */
  r2: ClawR2Config;

  /**
   * Environment variables to pass to the OpenClaw container.
   *
   * SECRET: These contain sensitive values. Do not log or store unencrypted.
   */
  containerEnv: OpenClawContainerEnv;
}

/**
 * Environment variables for the OpenClaw container.
 *
 * Required keys are always present; optional keys are for integrations.
 * Additional user-defined keys can be included via the index signature.
 */
export interface OpenClawContainerEnv {
  /** API key for LLM routing via Mirascope router */
  MIRASCOPE_API_KEY: string;

  /** Also set to MIRASCOPE_API_KEY so Anthropic SDK picks it up */
  ANTHROPIC_API_KEY: string;

  /** Base URL for Anthropic API (via Mirascope router) */
  ANTHROPIC_BASE_URL: string;

  /** Auth token for the OpenClaw gateway */
  OPENCLAW_GATEWAY_TOKEN: string;

  /** Telegram bot token (optional) */
  TELEGRAM_BOT_TOKEN?: string;

  /** Discord bot token (optional) */
  DISCORD_BOT_TOKEN?: string;

  /** Slack bot token (optional) */
  SLACK_BOT_TOKEN?: string;

  /** Slack app-level token (optional) */
  SLACK_APP_TOKEN?: string;

  /** Additional user-defined environment variables */
  [key: string]: string | undefined;
}

/**
 * Status report sent from dispatch worker to Mirascope.
 *
 * @endpoint POST /api/internal/claws/:clawId/status
 */
export interface ClawStatusReport {
  /** Current status of the claw */
  status: ClawStatus;

  /** Error message if status is "error" */
  errorMessage?: string;

  /** ISO timestamp when container started (if running) */
  startedAt?: string;
}

/**
 * The deployed URL for a claw.
 */
export function getClawUrl(orgSlug: string, clawSlug: string): string {
  return `https://${clawSlug}.${orgSlug}.mirascope.com`;
}
