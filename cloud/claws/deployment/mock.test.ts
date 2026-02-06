/**
 * @fileoverview Tests for the mock deployment service.
 *
 * Verifies that MockDeploymentService implements the DeploymentService
 * interface correctly and all operations behave as expected.
 */

import { Effect } from "effect";
import { describe, it, expect, beforeEach } from "vitest";

import type { OpenClawConfig } from "@/claws/deployment/types";

import { DeploymentError } from "@/claws/deployment/errors";
import {
  MockDeploymentService,
  resetMockDeploymentState,
} from "@/claws/deployment/mock";
import { DeploymentService } from "@/claws/deployment/service";
import { getClawUrl } from "@/claws/deployment/types";

const testConfig: OpenClawConfig = {
  clawId: "claw-test-123",
  clawSlug: "my-claw",
  organizationId: "org-456",
  organizationSlug: "my-org",
  instanceType: "basic",
  r2: {
    bucketName: "claw-claw-test-123",
    accessKeyId: "test-access-key",
    secretAccessKey: "test-secret-key",
  },
  containerEnv: {
    MIRASCOPE_API_KEY: "key_abc123",
    ANTHROPIC_API_KEY: "key_abc123",
    ANTHROPIC_BASE_URL: "https://router.mirascope.com/v1",
    OPENCLAW_GATEWAY_TOKEN: "gw_token_xyz",
  },
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
      expect(status.url).toBe(
        getClawUrl(testConfig.organizationSlug, testConfig.clawSlug),
      );
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
      expect(status.url).toBe(
        getClawUrl(testConfig.organizationSlug, testConfig.clawSlug),
      );
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

  describe("update", () => {
    it("returns active status", async () => {
      const status = await run(
        Effect.gen(function* () {
          const deployment = yield* DeploymentService;
          yield* deployment.provision(testConfig);
          return yield* deployment.update(testConfig.clawId, {
            instanceType: "standard-2",
          });
        }),
      );

      expect(status.status).toBe("active");
    });

    it("fails for unknown claw", async () => {
      const error = await runFail(
        Effect.gen(function* () {
          const deployment = yield* DeploymentService;
          return yield* deployment.update("unknown-claw", {});
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

describe("getClawUrl", () => {
  it("returns the correct URL", () => {
    expect(getClawUrl("my-org", "my-claw")).toBe(
      "https://my-claw.my-org.mirascope.com",
    );
  });
});
