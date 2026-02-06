/**
 * @fileoverview Cloudflare API configuration and settings.
 *
 * Defines the configuration needed to authenticate with the Cloudflare REST API
 * and target the correct account. Used by all Cloudflare services (R2, Containers).
 */

import { Context, Layer } from "effect";

/**
 * Configuration for authenticating with the Cloudflare REST API.
 */
export type CloudflareConfig = {
  /** Cloudflare account ID */
  readonly accountId: string;

  /** API token with appropriate scopes for R2 + Durable Objects management */
  readonly apiToken: string;

  /**
   * Permission group IDs for R2 bucket-scoped token creation.
   * Discovered via GET /user/tokens/permission_groups and cached here.
   */
  readonly r2BucketItemReadPermissionGroupId: string;
  readonly r2BucketItemWritePermissionGroupId: string;

  /** Durable Object namespace ID for container management */
  readonly durableObjectNamespaceId: string;

  /** Base URL for the dispatch worker (for warm-up requests) */
  readonly dispatchWorkerBaseUrl: string;
};

/**
 * Cloudflare settings service providing validated API configuration.
 *
 * Use `yield* CloudflareSettings` to access configuration in Effect generators.
 */
export class CloudflareSettings extends Context.Tag("CloudflareSettings")<
  CloudflareSettings,
  CloudflareConfig
>() {
  static layer = (config: CloudflareConfig) =>
    Layer.succeed(CloudflareSettings, config);
}
