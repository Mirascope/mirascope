/**
 * @fileoverview Tests for the mock deployment service.
 *
 * Verifies that MockDeploymentService implements the DeploymentService
 * interface correctly and all operations behave as expected.
 */

import { Effect } from "effect";
import { describe, it, expect, beforeEach } from "vitest";

import type { DeploymentConfig } from "@/deployment/service";

import { DeploymentError } from "@/deployment/errors";
import {
  MockDeploymentService,
  resetMockDeploymentState,
} from "@/deployment/mock";
import { DeploymentService } from "@/deployment/service";

const testConfig: DeploymentConfig = {
  clawId: "claw-test-123",
  clawSlug: "my-claw",
  organizationSlug: "my-org",
  instanceType: "basic",
  routerApiKey: "key_abc123",
};

const run = <A, E>(effect: Effect.Effect<A, E, DeploymentService>) =>
  Effect.runPromise(effect.pipe(Effect.provide(MockDeploymentService)));

const runFail = <A, E>(effect: Effect.Effect<A, E, DeploymentService>) =>
  Effect.runPromise(
    effect.pipe(Effect.flip, Effect.provide(MockDeploymentService)),
  );

describe("DeploymentError", () => {
  it("has correct tag and status", () => {
    const error = new DeploymentError({ message: "test error" });
    expect(error._tag).toBe("DeploymentError");
    expect(DeploymentError.status).toBe(500);
    expect(error.message).toBe("test error");
  });

  it("supports optional cause", () => {
    const cause = new Error("underlying");
    const error = new DeploymentError({
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
    it("returns active status with URL", async () => {
      const status = await run(
        Effect.gen(function* () {
          const deployment = yield* DeploymentService;
          return yield* deployment.provision(testConfig);
        }),
      );

      expect(status.status).toBe("active");
      expect(status.url).toBe("my-claw.my-org.mirascope.com");
      expect(status.startedAt).toBeInstanceOf(Date);
      expect(status.errorMessage).toBeUndefined();
    });
  });

  describe("deprovision", () => {
    it("removes deployment state", async () => {
      await run(
        Effect.gen(function* () {
          const deployment = yield* DeploymentService;
          yield* deployment.provision(testConfig);
          yield* deployment.deprovision(testConfig.clawId);
        }),
      );

      // getStatus should fail after deprovision
      const error = await runFail(
        Effect.gen(function* () {
          const deployment = yield* DeploymentService;
          return yield* deployment.getStatus(testConfig.clawId);
        }),
      );

      expect(error).toBeInstanceOf(DeploymentError);
    });
  });

  describe("getStatus", () => {
    it("returns status for provisioned claw", async () => {
      const status = await run(
        Effect.gen(function* () {
          const deployment = yield* DeploymentService;
          yield* deployment.provision(testConfig);
          return yield* deployment.getStatus(testConfig.clawId);
        }),
      );

      expect(status.status).toBe("active");
      expect(status.url).toBe("my-claw.my-org.mirascope.com");
    });

    it("fails for unknown claw", async () => {
      const error = await runFail(
        Effect.gen(function* () {
          const deployment = yield* DeploymentService;
          return yield* deployment.getStatus("unknown-claw");
        }),
      );

      expect(error).toBeInstanceOf(DeploymentError);
      expect((error as DeploymentError).message).toContain(
        "No deployment found",
      );
    });
  });

  describe("restart", () => {
    it("returns active status with new startedAt", async () => {
      const { before, after } = await run(
        Effect.gen(function* () {
          const deployment = yield* DeploymentService;
          const before = yield* deployment.provision(testConfig);
          yield* Effect.sleep("10 millis");
          const after = yield* deployment.restart(testConfig.clawId);
          return { before, after };
        }),
      );

      expect(after.status).toBe("active");
      expect(after.startedAt).toBeInstanceOf(Date);
      expect(after.startedAt!.getTime()).toBeGreaterThanOrEqual(
        before.startedAt!.getTime(),
      );
    });

    it("fails for unknown claw", async () => {
      const error = await runFail(
        Effect.gen(function* () {
          const deployment = yield* DeploymentService;
          return yield* deployment.restart("unknown-claw");
        }),
      );

      expect(error).toBeInstanceOf(DeploymentError);
    });
  });

  describe("updateConfig", () => {
    it("returns active status", async () => {
      const status = await run(
        Effect.gen(function* () {
          const deployment = yield* DeploymentService;
          yield* deployment.provision(testConfig);
          return yield* deployment.updateConfig(testConfig.clawId, {
            routerApiKey: "new_key",
          });
        }),
      );

      expect(status.status).toBe("active");
    });

    it("fails for unknown claw", async () => {
      const error = await runFail(
        Effect.gen(function* () {
          const deployment = yield* DeploymentService;
          return yield* deployment.updateConfig("unknown-claw", {});
        }),
      );

      expect(error).toBeInstanceOf(DeploymentError);
    });
  });

  describe("resize", () => {
    it("returns active status", async () => {
      const status = await run(
        Effect.gen(function* () {
          const deployment = yield* DeploymentService;
          yield* deployment.provision(testConfig);
          return yield* deployment.resize(testConfig.clawId, "standard-2");
        }),
      );

      expect(status.status).toBe("active");
    });

    it("fails for unknown claw", async () => {
      const error = await runFail(
        Effect.gen(function* () {
          const deployment = yield* DeploymentService;
          return yield* deployment.resize("unknown-claw", "standard-2");
        }),
      );

      expect(error).toBeInstanceOf(DeploymentError);
    });
  });

  describe("storage operations", () => {
    it("putStorage and getStorage round-trip", async () => {
      const data = await run(
        Effect.gen(function* () {
          const deployment = yield* DeploymentService;
          yield* deployment.provision(testConfig);

          const testData = new Uint8Array([1, 2, 3, 4, 5]);
          yield* deployment.putStorage(
            testConfig.clawId,
            "config.json",
            testData,
          );
          return yield* deployment.getStorage(testConfig.clawId, "config.json");
        }),
      );

      expect(data).toEqual(new Uint8Array([1, 2, 3, 4, 5]));
    });

    it("getStorage fails for missing file", async () => {
      const error = await runFail(
        Effect.gen(function* () {
          const deployment = yield* DeploymentService;
          yield* deployment.provision(testConfig);
          return yield* deployment.getStorage(
            testConfig.clawId,
            "nonexistent.json",
          );
        }),
      );

      expect(error).toBeInstanceOf(DeploymentError);
      expect((error as DeploymentError).message).toContain("File not found");
    });

    it("deleteStorage removes file", async () => {
      const error = await runFail(
        Effect.gen(function* () {
          const deployment = yield* DeploymentService;
          yield* deployment.provision(testConfig);

          const testData = new Uint8Array([1, 2, 3]);
          yield* deployment.putStorage(
            testConfig.clawId,
            "temp.json",
            testData,
          );
          yield* deployment.deleteStorage(testConfig.clawId, "temp.json");

          // Should fail after deletion
          return yield* deployment.getStorage(testConfig.clawId, "temp.json");
        }),
      );

      expect(error).toBeInstanceOf(DeploymentError);
      expect((error as DeploymentError).message).toContain("File not found");
    });

    it("getStorage fails for unprovisioned claw", async () => {
      const error = await runFail(
        Effect.gen(function* () {
          const deployment = yield* DeploymentService;
          return yield* deployment.getStorage("unknown-claw", "file.json");
        }),
      );

      expect(error).toBeInstanceOf(DeploymentError);
      expect((error as DeploymentError).message).toContain(
        "No deployment found",
      );
    });

    it("putStorage fails for unprovisioned claw", async () => {
      const error = await runFail(
        Effect.gen(function* () {
          const deployment = yield* DeploymentService;
          return yield* deployment.putStorage(
            "unknown-claw",
            "file.json",
            new Uint8Array([1]),
          );
        }),
      );

      expect(error).toBeInstanceOf(DeploymentError);
    });

    it("deleteStorage fails for unprovisioned claw", async () => {
      const error = await runFail(
        Effect.gen(function* () {
          const deployment = yield* DeploymentService;
          return yield* deployment.deleteStorage("unknown-claw", "file.json");
        }),
      );

      expect(error).toBeInstanceOf(DeploymentError);
    });
  });

  describe("resetMockDeploymentState", () => {
    it("clears all mock state", async () => {
      // Provision a claw
      await run(
        Effect.gen(function* () {
          const deployment = yield* DeploymentService;
          yield* deployment.provision(testConfig);
          yield* deployment.putStorage(
            testConfig.clawId,
            "test.json",
            new Uint8Array([1]),
          );
        }),
      );

      // Reset state
      resetMockDeploymentState();

      // Should fail since state was cleared
      const error = await runFail(
        Effect.gen(function* () {
          const deployment = yield* DeploymentService;
          return yield* deployment.getStatus(testConfig.clawId);
        }),
      );

      expect(error).toBeInstanceOf(DeploymentError);
    });
  });
});
