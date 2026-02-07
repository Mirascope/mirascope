/**
 * @fileoverview Mock deployment service for development and testing.
 *
 * Simulates claw provisioning and management operations with `Effect.sleep`
 * delays. This is the initial implementation used until Dandelion provides
 * the real Moltworker-backed deployment service.
 *
 * ## Behavior
 *
 * - `provision` — Returns "active" status after a short delay
 * - `deprovision` — Removes tracked state with delay
 * - `getStatus` — Returns tracked status
 * - `restart` — Returns "active" after delay
 * - `update` — Returns "active" after delay
 */

import { Effect, Layer } from "effect";

import type { DeploymentStatus } from "@/claws/deployment/service";
import type { OpenClawConfig } from "@/claws/deployment/types";

import { DeploymentError } from "@/claws/deployment/errors";
import { DeploymentService } from "@/claws/deployment/service";
import { getClawUrl } from "@/claws/deployment/types";

/**
 * In-memory deployment status tracking.
 * Maps clawId → DeploymentStatus.
 */
const mockStatuses = new Map<string, DeploymentStatus>();

/**
 * Mock deployment service layer for development and testing.
 *
 * Provides a fully functional but simulated deployment service:
 * - Provisioning sets status to "active" with a generated URL
 * - All operations include simulated delays
 */
export const MockDeploymentService = Layer.succeed(DeploymentService, {
  provision: (config: OpenClawConfig) =>
    Effect.gen(function* () {
      yield* Effect.sleep("100 millis");

      const status: DeploymentStatus = {
        status: "active",
        url: getClawUrl(config.organizationSlug, config.clawSlug),
        startedAt: new Date(),
        bucketName: `claw-${config.clawId}`,
        r2Credentials: {
          tokenId: `mock-token-${config.clawId}`,
          accessKeyId: `mock-access-${config.clawId}`,
          secretAccessKey: `mock-secret-${config.clawId}`,
        },
      };

      mockStatuses.set(config.clawId, status);

      return status;
    }),

  deprovision: (clawId: string) =>
    Effect.gen(function* () {
      yield* Effect.sleep("50 millis");
      mockStatuses.delete(clawId);
    }),

  getStatus: (clawId: string) =>
    Effect.gen(function* () {
      const status = mockStatuses.get(clawId);
      if (!status) {
        return yield* Effect.fail(
          new DeploymentError({
            message: `No deployment found for claw ${clawId}`,
          }),
        );
      }
      return status;
    }),

  restart: (clawId: string) =>
    Effect.gen(function* () {
      yield* Effect.sleep("100 millis");

      const existing = mockStatuses.get(clawId);
      if (!existing) {
        return yield* Effect.fail(
          new DeploymentError({
            message: `No deployment found for claw ${clawId}`,
          }),
        );
      }

      const status: DeploymentStatus = {
        ...existing,
        status: "active",
        startedAt: new Date(),
      };
      mockStatuses.set(clawId, status);
      return status;
    }),

  update: (clawId: string, _config: Partial<OpenClawConfig>) =>
    Effect.gen(function* () {
      yield* Effect.sleep("50 millis");

      const existing = mockStatuses.get(clawId);
      if (!existing) {
        return yield* Effect.fail(
          new DeploymentError({
            message: `No deployment found for claw ${clawId}`,
          }),
        );
      }

      const status: DeploymentStatus = {
        ...existing,
        status: "active",
      };
      mockStatuses.set(clawId, status);
      return status;
    }),

  warmUp: (_clawId: string) =>
    Effect.gen(function* () {
      yield* Effect.sleep("50 millis");
    }),
});

/**
 * Resets all mock deployment state. Call in test `beforeEach` or `afterEach`.
 */
export function resetMockDeploymentState(): void {
  mockStatuses.clear();
}
