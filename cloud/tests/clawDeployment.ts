import { Effect, Layer } from "effect";

import type { ClawDeploymentServiceInterface } from "@/claws/deployment/service";

import { ClawDeploymentError } from "@/claws/deployment/errors";
import { ClawDeploymentService } from "@/claws/deployment/service";

// ============================================================================
// Mock ClawDeploymentService for handler-level tests
// ============================================================================

/**
 * Synchronous mock deployment service for handler-level tests.
 *
 * Unlike `MockDeploymentService` (from `claws/deployment/mock.ts`) which uses
 * `Effect.sleep` for realistic simulation, this mock is fully synchronous.
 * This avoids timeout issues when tests provide mocked outer layers that
 * interfere with the Effect runtime's clock.
 *
 * Use this in handler-level tests that mock `Database`, `DrizzleORM`, etc.
 * and only need to verify that the handler calls the deployment service
 * correctly.
 *
 * @example
 * ```ts
 * import { MockClawDeployment } from "@/tests/deployment";
 *
 * // Default layer (provision returns mock credentials)
 * const layer = MockClawDeployment.layer();
 *
 * // Custom overrides
 * const failingLayer = MockClawDeployment.layer({
 *   provision: () => Effect.fail(new ClawDeploymentError({ message: "boom" })),
 * });
 * ```
 */
export const MockClawDeployment = {
  /**
   * Creates a `ClawDeploymentService` layer with optional overrides.
   *
   * The default implementation:
   * - `provision` — succeeds with mock bucket name and R2 credentials
   * - `deprovision` — succeeds (void)
   * - `warmUp` — succeeds (void)
   * - `getStatus`, `restart`, `update` — fail with "not implemented"
   */
  layer: (
    overrides?: Partial<ClawDeploymentServiceInterface>,
  ): Layer.Layer<ClawDeploymentService> =>
    Layer.succeed(ClawDeploymentService, {
      provision: (config) =>
        Effect.succeed({
          status: "active" as const,
          startedAt: new Date(),
          bucketName: `claw-${config.clawId}`,
          r2Credentials: {
            tokenId: `mock-token-${config.clawId}`,
            accessKeyId: `mock-access-${config.clawId}`,
            secretAccessKey: `mock-secret-${config.clawId}`,
          },
        }),
      deprovision: () => Effect.void,
      getStatus: () =>
        Effect.fail(new ClawDeploymentError({ message: "not implemented" })),
      restart: () =>
        Effect.fail(new ClawDeploymentError({ message: "not implemented" })),
      update: () =>
        Effect.fail(new ClawDeploymentError({ message: "not implemented" })),
      warmUp: () => Effect.void,
      ...overrides,
    }),
};
