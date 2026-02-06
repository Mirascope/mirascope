/**
 * @fileoverview Mock container service for development and testing.
 *
 * Simulates container lifecycle operations with in-memory state.
 * Each call to `makeMockContainerLayer()` creates an isolated instance
 * with its own state, eliminating cross-test pollution.
 *
 * ## Behavior
 *
 * - `restart` — Resets container state to "running"
 * - `destroy` — Removes container state entirely
 * - `getState` — Returns tracked container state, fails if not found
 * - `warmUp` — Initializes container to "running" state if not present
 * - `listInstances` — Returns all tracked containers as DO instances
 */

import { Effect, Layer } from "effect";

import type { ContainerState } from "@/cloudflare/containers/types";

import { CloudflareContainerService } from "@/cloudflare/containers/service";
import { CloudflareApiError } from "@/errors";

/**
 * Creates a fresh mock container service layer with isolated state.
 *
 * Each invocation gets its own in-memory Map, so parallel tests
 * or multiple test files cannot interfere with each other.
 *
 * Use the returned `seed` function to pre-populate container state
 * before testing restart/destroy/getState.
 *
 * ```ts
 * const { layer, seed } = makeMockContainerLayer();
 * seed("my-claw.org.mirascope.com");
 * await Effect.runPromise(program.pipe(Effect.provide(layer)));
 * ```
 */
export function makeMockContainerLayer() {
  const containers = new Map<string, ContainerState>();

  function seed(
    hostname: string,
    state: ContainerState = { status: "running", lastChange: Date.now() },
  ): void {
    containers.set(hostname, state);
  }

  const layer = Layer.succeed(CloudflareContainerService, {
    restart: (hostname: string) =>
      Effect.gen(function* () {
        if (!containers.has(hostname)) {
          return yield* Effect.fail(
            new CloudflareApiError({
              message: `Container not found for hostname ${hostname}`,
            }),
          );
        }

        containers.set(hostname, {
          status: "running",
          lastChange: Date.now(),
        });
      }),

    destroy: (hostname: string) =>
      Effect.gen(function* () {
        if (!containers.has(hostname)) {
          return yield* Effect.fail(
            new CloudflareApiError({
              message: `Container not found for hostname ${hostname}`,
            }),
          );
        }

        containers.delete(hostname);
      }),

    getState: (hostname: string) =>
      Effect.gen(function* () {
        const state = containers.get(hostname);
        if (!state) {
          return yield* Effect.fail(
            new CloudflareApiError({
              message: `Container not found for hostname ${hostname}`,
            }),
          );
        }
        return state;
      }),

    warmUp: (hostname: string) =>
      Effect.sync(() => {
        if (!containers.has(hostname)) {
          containers.set(hostname, {
            status: "running",
            lastChange: Date.now(),
          });
        }
      }),

    listInstances: () =>
      Effect.sync(() =>
        Array.from(containers.keys()).map((hostname) => ({
          id: hostname,
          hasStoredData: true,
        })),
      ),
  });

  return { layer, seed };
}
