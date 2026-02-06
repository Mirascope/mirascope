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
 * - `deprovision` — No-op with delay
 * - `getStatus` — Always returns "active"
 * - `restart` — Returns "active" after delay
 * - `updateConfig` — Returns "active" after delay
 * - `resize` — Returns "active" after delay
 * - Storage operations — In-memory map, no persistence
 */

import { Effect, Layer } from "effect";

import type { DeploymentConfig, DeploymentStatus } from "@/deployment/service";

import { DeploymentError } from "@/deployment/errors";
import { DeploymentService } from "@/deployment/service";

/**
 * In-memory storage for mock deployment state.
 * Maps clawId → Map<path, data>.
 */
const mockStorage = new Map<string, Map<string, Uint8Array>>();

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
 * - Storage uses an in-memory map
 * - All operations include simulated delays
 */
export const MockDeploymentService = Layer.succeed(DeploymentService, {
  provision: (config: DeploymentConfig) =>
    Effect.gen(function* () {
      yield* Effect.sleep("100 millis");

      const status: DeploymentStatus = {
        status: "active",
        url: `${config.clawSlug}.${config.organizationSlug}.mirascope.com`,
        startedAt: new Date(),
      };

      mockStatuses.set(config.clawId, status);
      mockStorage.set(config.clawId, new Map());

      return status;
    }),

  deprovision: (clawId: string) =>
    Effect.gen(function* () {
      yield* Effect.sleep("50 millis");
      mockStatuses.delete(clawId);
      mockStorage.delete(clawId);
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

  updateConfig: (clawId: string, _config: Partial<DeploymentConfig>) =>
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

  resize: (clawId: string, _instanceType: DeploymentConfig["instanceType"]) =>
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

  getStorage: (clawId: string, path: string) =>
    Effect.gen(function* () {
      const clawStorage = mockStorage.get(clawId);
      if (!clawStorage) {
        return yield* Effect.fail(
          new DeploymentError({
            message: `No deployment found for claw ${clawId}`,
          }),
        );
      }

      const data = clawStorage.get(path);
      if (!data) {
        return yield* Effect.fail(
          new DeploymentError({
            message: `File not found: ${path}`,
          }),
        );
      }

      return data;
    }),

  putStorage: (clawId: string, path: string, data: Uint8Array) =>
    Effect.gen(function* () {
      let clawStorage = mockStorage.get(clawId);
      if (!clawStorage) {
        return yield* Effect.fail(
          new DeploymentError({
            message: `No deployment found for claw ${clawId}`,
          }),
        );
      }

      clawStorage.set(path, data);
    }),

  deleteStorage: (clawId: string, path: string) =>
    Effect.gen(function* () {
      const clawStorage = mockStorage.get(clawId);
      if (!clawStorage) {
        return yield* Effect.fail(
          new DeploymentError({
            message: `No deployment found for claw ${clawId}`,
          }),
        );
      }

      clawStorage.delete(path);
    }),
});

/**
 * Resets all mock deployment state. Call in test `beforeEach` or `afterEach`.
 */
export function resetMockDeploymentState(): void {
  mockStatuses.clear();
  mockStorage.clear();
}
