/**
 * @fileoverview Shared configuration and types for Cloudflare Cron Triggers.
 */

import type { CloudflareEnvironment } from "@/settings";

/**
 * Cloudflare Scheduled Event type.
 */
export interface ScheduledEvent {
  readonly scheduledTime: number;
  readonly cron: string;
}

/**
 * Base Cloudflare environment bindings for Cron Triggers.
 */
export interface CronTriggerEnv extends CloudflareEnvironment {
  readonly HYPERDRIVE?: {
    readonly connectionString: string;
  };
  readonly DATABASE_URL?: string;
}

/**
 * Extended environment for billing-related cron triggers.
 */
export interface BillingCronTriggerEnv extends CronTriggerEnv {
  readonly STRIPE_API_KEY?: string;
  readonly STRIPE_ROUTER_PRICE_ID?: string;
  readonly STRIPE_ROUTER_METER_ID?: string;
}
