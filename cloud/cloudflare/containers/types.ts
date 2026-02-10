/* v8 ignore file -- pure type definitions */
/**
 * @fileoverview Types for Cloudflare container/Durable Object management.
 *
 * These types model the Cloudflare REST API responses for Durable Object
 * operations and the dispatch worker's internal management endpoints.
 *
 * ## Important Architecture Notes
 *
 * Cloudflare does NOT provide a REST API to delete/restart individual Durable
 * Object instances or container sandboxes. Management happens through:
 *
 * 1. **Dispatch worker endpoints** — The dispatch worker exposes internal
 *    management routes that the cloud backend calls to control containers
 *    (restart via throwing uncaught exception, destroy via Container.destroy()).
 *
 * 2. **Cloudflare REST API** — Only provides read-only listing of DO namespaces
 *    and instances. Used for observability, not lifecycle management.
 */

/**
 * Durable Object instance info as returned by the Cloudflare API.
 */
export interface DurableObjectInfo {
  /** Hex-encoded Durable Object ID */
  id: string;

  /** Whether the instance has any stored data */
  hasStoredData: boolean;
}

/**
 * Container state as reported by the dispatch worker.
 */
export type ContainerStatus =
  | "running"
  | "stopping"
  | "stopped"
  | "healthy"
  | "unknown";

/**
 * Container state report from the dispatch worker.
 */
export interface ContainerState {
  /** Container status */
  status: ContainerStatus;

  /** Epoch timestamp of last state change */
  lastChange?: number;

  /** Exit code if status is "stopped" */
  exitCode?: number;
}
