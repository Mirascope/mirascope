/**
 * @fileoverview Live implementation of CloudflareContainerService.
 *
 * Uses TWO communication channels:
 *
 * 1. **Dispatch worker internal API** — For lifecycle operations. The dispatch
 *    worker exposes `/_internal/restart`, `/_internal/destroy`, and
 *    `/_internal/state` endpoints that proxy commands to the Durable Object.
 *
 * 2. **Cloudflare REST API** — For listing DO instances (read-only).
 *
 * ## Dispatch Worker Internal Endpoints
 *
 * These routes are handled by the dispatch worker and routed to the correct
 * Durable Object by hostname:
 *
 * - `POST /_internal/restart` (Host: {hostname}) — Force restart
 * - `POST /_internal/destroy` (Host: {hostname}) — Force destroy
 * - `GET  /_internal/state`   (Host: {hostname}) — Get container state
 *
 * ## Cloudflare REST API Endpoints
 *
 * - `GET /accounts/{account_id}/workers/durable_objects/namespaces/{ns}/objects`
 */

import { Effect, Layer } from "effect";

import type { CloudflareHttpClient } from "@/cloudflare/client";
import type { CloudflareConfig } from "@/cloudflare/config";
import type { CloudflareContainerServiceInterface } from "@/cloudflare/containers/service";
import type { ContainerState } from "@/cloudflare/containers/types";

import { CloudflareHttp } from "@/cloudflare/client";
import { CloudflareSettings } from "@/cloudflare/config";
import { CloudflareContainerService } from "@/cloudflare/containers/service";
import { CloudflareApiError } from "@/errors";

/**
 * Raw Cloudflare API response for listing DO instances.
 */
interface CloudflareListObjectsResult {
  id: string;
  hasStoredData: boolean;
}

function makeContainerService(
  http: CloudflareHttpClient,
  config: CloudflareConfig,
): CloudflareContainerServiceInterface {
  const dispatchFetch = (
    hostname: string,
    path: string,
    method: "GET" | "POST",
  ) =>
    Effect.tryPromise({
      try: () =>
        fetch(`${config.dispatchWorkerBaseUrl}${path}`, {
          method,
          headers: {
            Host: hostname,
            "Content-Type": "application/json",
          },
        }),
      catch: (error) =>
        new CloudflareApiError({
          message: `Dispatch worker request failed: ${method} ${path} (host: ${hostname})`,
          cause: error,
        }),
    });

  return {
    restart: (hostname: string) =>
      Effect.gen(function* () {
        const response = yield* dispatchFetch(
          hostname,
          "/_internal/restart",
          "POST",
        );
        if (!response.ok) {
          return yield* Effect.fail(
            new CloudflareApiError({
              message: `Restart failed for ${hostname}: ${response.status} ${response.statusText}`,
            }),
          );
        }
      }),

    destroy: (hostname: string) =>
      Effect.gen(function* () {
        const response = yield* dispatchFetch(
          hostname,
          "/_internal/destroy",
          "POST",
        );
        if (!response.ok) {
          return yield* Effect.fail(
            new CloudflareApiError({
              message: `Destroy failed for ${hostname}: ${response.status} ${response.statusText}`,
            }),
          );
        }
      }),

    getState: (hostname: string) =>
      Effect.gen(function* () {
        const response = yield* dispatchFetch(
          hostname,
          "/_internal/state",
          "GET",
        );
        if (!response.ok) {
          return yield* Effect.fail(
            new CloudflareApiError({
              message: `Get state failed for ${hostname}: ${response.status} ${response.statusText}`,
            }),
          );
        }

        const state = yield* Effect.tryPromise({
          try: () => response.json() as Promise<ContainerState>,
          catch: (error) =>
            new CloudflareApiError({
              message: `Failed to parse container state for ${hostname}`,
              cause: error,
            }),
        });

        return state;
      }),

    warmUp: (hostname: string) =>
      Effect.gen(function* () {
        const response = yield* Effect.tryPromise({
          try: () =>
            fetch(`https://${hostname}/`, {
              method: "GET",
              signal: AbortSignal.timeout(30_000),
            }),
          catch: (error) =>
            new CloudflareApiError({
              message: `Warm-up request failed for ${hostname}`,
              cause: error,
            }),
        });
        if (!response.ok) {
          return yield* Effect.fail(
            new CloudflareApiError({
              message: `Warm-up failed for ${hostname}: ${response.status} ${response.statusText}`,
            }),
          );
        }
      }),

    listInstances: () =>
      Effect.gen(function* () {
        const instancesPath = `/accounts/${config.accountId}/workers/durable_objects/namespaces/${config.durableObjectNamespaceId}/objects`;

        // Request max page size. Pagination would require parsing result_info
        // from the response envelope, which the HTTP client doesn't surface.
        // For now, a single page of 10000 is sufficient for diagnostics.
        const raw = yield* http.request<CloudflareListObjectsResult[]>({
          method: "GET",
          path: `${instancesPath}?limit=10000`,
        });

        return raw.map((obj: CloudflareListObjectsResult) => ({
          id: obj.id,
          hasStoredData: obj.hasStoredData,
        }));
      }),
  };
}

/**
 * Live implementation of CloudflareContainerService.
 *
 * Requires CloudflareHttpClient and CloudflareSettings layers to be provided.
 */
export const LiveCloudflareContainerService = Layer.effect(
  CloudflareContainerService,
  Effect.gen(function* () {
    const http = yield* CloudflareHttp;
    const config = yield* CloudflareSettings;
    return makeContainerService(http, config);
  }),
);
