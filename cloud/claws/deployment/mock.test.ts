/**
 * @fileoverview Tests for the mock deployment service.
 *
 * Verifies that MockDeploymentService implements the DeploymentService
 * interface correctly and all operations behave as expected.
 */

import { describe, it, expect } from "@effect/vitest";
import { Effect } from "effect";
import { beforeEach } from "vitest";

import type { ProvisionClawConfig } from "@/claws/deployment/types";

import { ClawDeploymentError } from "@/claws/deployment/errors";
import {
  MockDeploymentService,
  resetMockDeploymentState,
} from "@/claws/deployment/mock";
import { ClawDeploymentService } from "@/claws/deployment/service";
import { getClawUrl } from "@/claws/deployment/types";

const testConfig: ProvisionClawConfig = {
  clawId: "claw-test-123",
  instanceType: "basic",
};

describe("DeploymentError", () => {
  it("has correct tag and status", () => {
    const error = new ClawDeploymentError({ message: "test error" });
    expect(error._tag).toBe("DeploymentError");
    expect(ClawDeploymentError.status).toBe(500);
    expect(error.message).toBe("test error");
  });

  it("supports optional cause", () => {
    const cause = new Error("underlying");
    const error = new ClawDeploymentError({
      message: "test error",
      cause,
    });
    expect(error.cause).toBe(cause);
  });
});

describe("MockDeploymentService", () => {
  beforeEach(() => {
    resetMockDeploymentState();
  });

  describe("provision", () => {
    it.live("returns active status with URL", () =>
      Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        const status = yield* deployment.provision(testConfig);

        expect(status.status).toBe("active");
        expect(status.startedAt).toBeInstanceOf(Date);
        expect(status.errorMessage).toBeUndefined();
        expect(status.miniId).toBe(`mock-mini-${testConfig.clawId}`);
        expect(status.miniPort).toBe(18789);
        expect(status.tunnelHostname).toBe(
          `claw-${testConfig.clawId}.claws.mirascope.dev`,
        );
        expect(status.macUsername).toBe(`claw-${testConfig.clawId}`);
      }).pipe(Effect.provide(MockDeploymentService)),
    );
  });

  describe("deprovision", () => {
    it.live("removes deployment state", () =>
      Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        yield* deployment.provision(testConfig);
        yield* deployment.deprovision(testConfig.clawId);

        // getStatus should fail after deprovision
        const error = yield* deployment
          .getStatus(testConfig.clawId)
          .pipe(Effect.flip);
        expect(error).toBeInstanceOf(ClawDeploymentError);
      }).pipe(Effect.provide(MockDeploymentService)),
    );
  });

  describe("getStatus", () => {
    it.live("returns status for provisioned claw", () =>
      Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        yield* deployment.provision(testConfig);
        const status = yield* deployment.getStatus(testConfig.clawId);

        expect(status.status).toBe("active");
      }).pipe(Effect.provide(MockDeploymentService)),
    );

    it.live("fails for unknown claw", () =>
      Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        const error = yield* deployment
          .getStatus("unknown-claw")
          .pipe(Effect.flip);

        expect(error).toBeInstanceOf(ClawDeploymentError);
        expect((error as ClawDeploymentError).message).toContain(
          "No deployment found",
        );
      }).pipe(Effect.provide(MockDeploymentService)),
    );
  });

  describe("restart", () => {
    it.live("returns active status with new startedAt", () =>
      Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        const before = yield* deployment.provision(testConfig);
        yield* Effect.sleep("10 millis");
        const after = yield* deployment.restart(testConfig.clawId);

        expect(after.status).toBe("active");
        expect(after.startedAt).toBeInstanceOf(Date);
        expect(after.startedAt!.getTime()).toBeGreaterThanOrEqual(
          before.startedAt!.getTime(),
        );
      }).pipe(Effect.provide(MockDeploymentService)),
    );

    it.live("fails for unknown claw", () =>
      Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        const error = yield* deployment
          .restart("unknown-claw")
          .pipe(Effect.flip);

        expect(error).toBeInstanceOf(ClawDeploymentError);
      }).pipe(Effect.provide(MockDeploymentService)),
    );
  });

  describe("update", () => {
    it.live("returns active status", () =>
      Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        yield* deployment.provision(testConfig);
        const status = yield* deployment.update(testConfig.clawId, {
          instanceType: "standard-2",
        });

        expect(status.status).toBe("active");
      }).pipe(Effect.provide(MockDeploymentService)),
    );

    it.live("fails for unknown claw", () =>
      Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        const error = yield* deployment
          .update("unknown-claw", {})
          .pipe(Effect.flip);

        expect(error).toBeInstanceOf(ClawDeploymentError);
      }).pipe(Effect.provide(MockDeploymentService)),
    );
  });

  describe("warmUp", () => {
    it.live("completes without error", () =>
      Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        yield* deployment.warmUp("any-claw-id");
      }).pipe(Effect.provide(MockDeploymentService)),
    );
  });

  describe("resetMockDeploymentState", () => {
    it.live("clears all mock state", () =>
      Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        yield* deployment.provision(testConfig);

        // Reset state
        resetMockDeploymentState();

        // Should fail since state was cleared
        const error = yield* deployment
          .getStatus(testConfig.clawId)
          .pipe(Effect.flip);
        expect(error).toBeInstanceOf(ClawDeploymentError);
      }).pipe(Effect.provide(MockDeploymentService)),
    );
  });
});

describe("getClawUrl", () => {
  it("returns the correct URL", () => {
    expect(getClawUrl("my-org", "my-claw")).toBe(
      "https://my-claw.my-org.mirascope.com",
    );
  });
});
