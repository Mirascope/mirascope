/**
 * @fileoverview Shared configuration and types for Cloudflare Workers.
 */

import type { CloudflareEnvironment } from "@/settings";
import type { DurableObjectNamespace } from "@cloudflare/workers-types";
import type { RouterMeteringMessage } from "@/workers/routerMeteringQueue";
import type { SpansIngestMessage } from "@/workers/spanIngestQueue";

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
  readonly STRIPE_SECRET_KEY?: string;
  readonly STRIPE_ROUTER_PRICE_ID?: string;
  readonly STRIPE_ROUTER_METER_ID?: string;
}

/**
 * Complete Worker environment with all bindings.
 */
export interface WorkerEnv extends BillingCronTriggerEnv {
  readonly ROUTER_METERING_QUEUE?: {
    send: (message: RouterMeteringMessage) => Promise<void>;
  };
  readonly SPANS_INGEST_QUEUE?: {
    send: (message: SpansIngestMessage) => Promise<void>;
  };
  readonly RECENT_SPANS_DURABLE_OBJECT?: DurableObjectNamespace;
}
