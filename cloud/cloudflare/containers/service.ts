/**
 * @fileoverview Cloudflare container service interface for dispatch worker management.
 *
 * Defines the `CloudflareContainerService` Effect interface that abstracts
 * container lifecycle operations via the dispatch worker and Cloudflare REST API.
 *
 * This is a pure Cloudflare infrastructure layer — it knows about hostnames
 * and Durable Objects, not about any specific application. Higher-level
 * orchestration services compose this service for domain-specific workflows.
 *
 * ## Architecture
 *
 * Container management uses TWO mechanisms:
 *
 * 1. **Dispatch worker internal API** — For lifecycle operations (restart, destroy,
 *    get state). The cloud backend sends requests to the dispatch worker which
 *    forwards them to the correct Durable Object / Container instance.
 *
 * 2. **Cloudflare REST API** — For read-only operations (list DO instances).
 *    Used for observability and diagnostics.
 *
 * ```
 * CloudflareContainerService (Context.Tag)
 *   ├── recreate(hostname)        → Evict DO, next request creates fresh container
 *   ├── restartGateway(hostname)  → Restart gateway process inside running container
 *   ├── destroy(hostname)         → Destroy container and clear DO storage
 *   ├── getState(hostname)        → Get container state (via dispatch worker)
 *   ├── warmUp(hostname)          → Send warm-up request to trigger cold start
 *   └── listInstances()           → List DO instances (via Cloudflare API)
 * ```
 *
 * ## Usage
 *
 * ```ts
 * import { CloudflareContainerService } from "@/cloudflare/containers/service";
 *
 * const program = Effect.gen(function* () {
 *   const containers = yield* CloudflareContainerService;
 *
 *   yield* containers.restartGateway("my-app.my-org.example.com");
 *   yield* containers.warmUp("my-app.my-org.example.com");
 * });
 * ```
 */

import { Context, Effect } from "effect";

import type {
  ContainerState,
  DurableObjectInfo,
} from "@/cloudflare/containers/types";

import { CloudflareApiError } from "@/errors";

/**
 * Container service interface.
 *
 * Provides operations for managing containers on Cloudflare via the dispatch
 * worker. All lifecycle operations are keyed by hostname — the dispatch worker
 * resolves the hostname to the correct Durable Object.
 */
export interface CloudflareContainerServiceInterface {
  /**
   * Recreate a container from scratch.
   *
   * Sends a recreate command to the dispatch worker, which throws an uncaught
   * exception in the Durable Object to force eviction. The next request to the
   * hostname triggers a fresh cold start with latest config.
   *
   * Use this for instance type changes or hard recovery from error state.
   */
  readonly recreate: (
    hostname: string,
  ) => Effect.Effect<void, CloudflareApiError>;

  /**
   * Restart the gateway process inside a running container.
   *
   * Kills the OpenClaw gateway process and re-runs the startup script within
   * the same container. The R2 mount and DO state are preserved.
   *
   * Use this for config changes (new secrets, model changes) that don't
   * require a full container recreate.
   */
  readonly restartGateway: (
    hostname: string,
  ) => Effect.Effect<void, CloudflareApiError>;

  /**
   * Destroy a container and clear its DO storage.
   *
   * Sends a destroy command to the dispatch worker which calls
   * Container.destroy() and ctx.storage.deleteAll().
   */
  readonly destroy: (
    hostname: string,
  ) => Effect.Effect<void, CloudflareApiError>;

  /**
   * Get the current state of a container.
   *
   * Queries the dispatch worker's internal state endpoint.
   */
  readonly getState: (
    hostname: string,
  ) => Effect.Effect<ContainerState, CloudflareApiError>;

  /**
   * Send a warm-up request to trigger a cold start.
   *
   * Makes an HTTP request to the hostname which causes the dispatch worker
   * to fetch the bootstrap config and start the container.
   */
  readonly warmUp: (
    hostname: string,
  ) => Effect.Effect<void, CloudflareApiError>;

  /**
   * List all Durable Object instances in the container namespace.
   *
   * Uses the Cloudflare REST API (read-only). Useful for diagnostics
   * and observability.
   */
  readonly listInstances: () => Effect.Effect<
    DurableObjectInfo[],
    CloudflareApiError
  >;
}

/**
 * Cloudflare container service Effect tag.
 *
 * Use `yield* CloudflareContainerService` to access the container service
 * in Effect generators.
 */
export class CloudflareContainerService extends Context.Tag(
  "CloudflareContainerService",
)<CloudflareContainerService, CloudflareContainerServiceInterface>() {}
