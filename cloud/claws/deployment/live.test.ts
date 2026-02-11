/**
 * @fileoverview Tests for the live deployment service.
 *
 * Verifies that LiveDeploymentService correctly orchestrates
 * CloudflareR2Service and CloudflareContainerService to provision,
 * deprovision, restart, update, and query claw deployments.
 */

import { describe, it, expect } from "@effect/vitest";
import { Effect, Layer } from "effect";

import type { ProvisionClawConfig } from "@/claws/deployment/types";

import { ClawDeploymentError } from "@/claws/deployment/errors";
import { LiveDeploymentService } from "@/claws/deployment/live";
import { ClawDeploymentService } from "@/claws/deployment/service";
import { makeMockContainerLayer } from "@/cloudflare/containers/mock";
import { makeMockR2Layer } from "@/cloudflare/r2/mock";

const testConfig: ProvisionClawConfig = {
  clawId: "claw-test-123",
  instanceType: "basic",
};

/** Internal routing hostname — matches clawHostname(clawId) in live.ts. */
const INTERNAL_HOSTNAME = `${testConfig.clawId}.claws.mirascope.com`;

function createTestLayer() {
  const r2Layer = makeMockR2Layer();
  const { layer: containerLayer, seed } = makeMockContainerLayer();
  const liveLayer = LiveDeploymentService.pipe(
    Layer.provide(Layer.merge(r2Layer, containerLayer)),
  );
  return { layer: liveLayer, seedContainer: seed };
}

const run = <A, E>(effect: Effect.Effect<A, E, ClawDeploymentService>) => {
  const { layer } = createTestLayer();
  return Effect.runPromise(effect.pipe(Effect.provide(layer)));
};

const runFail = <A, E>(effect: Effect.Effect<A, E, ClawDeploymentService>) => {
  const { layer } = createTestLayer();
  return Effect.runPromise(effect.pipe(Effect.flip, Effect.provide(layer)));
};

describe("LiveDeploymentService", () => {
  describe("provision", () => {
    it("creates R2 bucket and credentials without warming up", async () => {
      const status = await run(
        Effect.gen(function* () {
          const deployment = yield* ClawDeploymentService;
          return yield* deployment.provision(testConfig);
        }),
      );

      expect(status.status).toBe("provisioning");
      expect(status.startedAt).toBeInstanceOf(Date);
      expect(status.bucketName).toBe(`claw-${testConfig.clawId}`);
      expect(status.r2Credentials).toBeDefined();
      expect(status.r2Credentials!.tokenId).toBeDefined();
      expect(status.r2Credentials!.accessKeyId).toBeDefined();
      expect(status.r2Credentials!.secretAccessKey).toBeDefined();
    });

    it("fails when R2 bucket already exists", async () => {
      const error = await runFail(
        Effect.gen(function* () {
          const deployment = yield* ClawDeploymentService;
          // Provision once
          yield* deployment.provision(testConfig);
          // Provision again — bucket already exists
          return yield* deployment.provision(testConfig);
        }),
      );

      expect(error).toBeInstanceOf(ClawDeploymentError);
      expect((error as ClawDeploymentError).message).toContain(
        "Failed to create R2 bucket",
      );
    });
  });

  describe("deprovision", () => {
    it("destroys container and deletes R2 bucket", async () => {
      await run(
        Effect.gen(function* () {
          const deployment = yield* ClawDeploymentService;
          yield* deployment.provision(testConfig);
          yield* deployment.deprovision(testConfig.clawId);
        }),
      );
    });

    it("succeeds even if container is already gone", async () => {
      // Deprovision without provisioning first — should not throw
      await run(
        Effect.gen(function* () {
          const deployment = yield* ClawDeploymentService;
          yield* deployment.deprovision("nonexistent-claw");
        }),
      );
    });
  });

  describe("getStatus", () => {
    it.effect("returns active for running container", () => {
      const { layer, seedContainer } = createTestLayer();
      seedContainer(INTERNAL_HOSTNAME, {
        status: "running",
        lastChange: 1700000000000,
      });

      return Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        const status = yield* deployment.getStatus(testConfig.clawId);

        expect(status.status).toBe("active");
        expect(status.startedAt).toEqual(new Date(1700000000000));
      }).pipe(Effect.provide(layer));
    });

    it.effect("returns active for healthy container", () => {
      const { layer, seedContainer } = createTestLayer();
      seedContainer(INTERNAL_HOSTNAME, { status: "healthy", lastChange: 1000 });

      return Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        const status = yield* deployment.getStatus(testConfig.clawId);

        expect(status.status).toBe("active");
      }).pipe(Effect.provide(layer));
    });

    it.effect("returns paused for stopped container", () => {
      const { layer, seedContainer } = createTestLayer();
      seedContainer(INTERNAL_HOSTNAME, {
        status: "stopped",
        lastChange: 1000,
        exitCode: 0,
      });

      return Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        const status = yield* deployment.getStatus(testConfig.clawId);

        expect(status.status).toBe("paused");
      }).pipe(Effect.provide(layer));
    });

    it.effect("returns paused for stopping container", () => {
      const { layer, seedContainer } = createTestLayer();
      seedContainer(INTERNAL_HOSTNAME, { status: "stopping" });

      return Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        const status = yield* deployment.getStatus(testConfig.clawId);

        expect(status.status).toBe("paused");
      }).pipe(Effect.provide(layer));
    });

    it.effect("returns error for unknown status", () => {
      const { layer, seedContainer } = createTestLayer();
      seedContainer(INTERNAL_HOSTNAME, { status: "unknown" });

      return Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        const status = yield* deployment.getStatus(testConfig.clawId);

        expect(status.status).toBe("error");
      }).pipe(Effect.provide(layer));
    });

    it.effect("returns undefined startedAt when lastChange is missing", () => {
      const { layer, seedContainer } = createTestLayer();
      seedContainer(INTERNAL_HOSTNAME, { status: "running" });

      return Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        const status = yield* deployment.getStatus(testConfig.clawId);

        expect(status.status).toBe("active");
        expect(status.startedAt).toBeUndefined();
      }).pipe(Effect.provide(layer));
    });

    it("fails for non-existent container", async () => {
      const error = await runFail(
        Effect.gen(function* () {
          const deployment = yield* ClawDeploymentService;
          return yield* deployment.getStatus("nonexistent");
        }),
      );

      expect(error).toBeInstanceOf(ClawDeploymentError);
      expect((error as ClawDeploymentError).message).toContain(
        "Failed to get container state",
      );
    });
  });

  describe("restart", () => {
    it.effect("restarts gateway and returns provisioning status", () => {
      const { layer, seedContainer } = createTestLayer();
      seedContainer(INTERNAL_HOSTNAME);

      return Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        const status = yield* deployment.restart(testConfig.clawId);

        expect(status.status).toBe("provisioning");
        expect(status.startedAt).toBeInstanceOf(Date);
      }).pipe(Effect.provide(layer));
    });

    it("fails for non-existent container", async () => {
      const error = await runFail(
        Effect.gen(function* () {
          const deployment = yield* ClawDeploymentService;
          return yield* deployment.restart("nonexistent");
        }),
      );

      expect(error).toBeInstanceOf(ClawDeploymentError);
      expect((error as ClawDeploymentError).message).toContain(
        "Failed to restart gateway",
      );
    });
  });

  describe("update", () => {
    it.effect("restarts gateway for non-instance-type config update", () => {
      const { layer, seedContainer } = createTestLayer();
      seedContainer(INTERNAL_HOSTNAME);

      return Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        const status = yield* deployment.update(testConfig.clawId, {
          containerEnv: {
            MIRASCOPE_API_KEY: "key_abc123",
            ANTHROPIC_API_KEY: "key_abc123",
            ANTHROPIC_BASE_URL: "https://router.mirascope.com/v1",
            OPENCLAW_GATEWAY_TOKEN: "gw_token_xyz",
            TELEGRAM_BOT_TOKEN: "new-token",
          },
        });

        expect(status.status).toBe("provisioning");
        expect(status.startedAt).toBeInstanceOf(Date);
      }).pipe(Effect.provide(layer));
    });

    it.effect("recreates container when instance type changes", () => {
      const { layer, seedContainer } = createTestLayer();
      seedContainer(INTERNAL_HOSTNAME);

      return Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        const status = yield* deployment.update(testConfig.clawId, {
          instanceType: "standard-2",
        });

        expect(status.status).toBe("provisioning");
        expect(status.startedAt).toBeInstanceOf(Date);
      }).pipe(Effect.provide(layer));
    });

    it("fails for non-existent container on gateway restart", async () => {
      const error = await runFail(
        Effect.gen(function* () {
          const deployment = yield* ClawDeploymentService;
          return yield* deployment.update("nonexistent", {});
        }),
      );

      expect(error).toBeInstanceOf(ClawDeploymentError);
      expect((error as ClawDeploymentError).message).toContain(
        "Failed to restart gateway for config update",
      );
    });

    it("fails for non-existent container on instance type change", async () => {
      const error = await runFail(
        Effect.gen(function* () {
          const deployment = yield* ClawDeploymentService;
          return yield* deployment.update("nonexistent", {
            instanceType: "standard-3",
          });
        }),
      );

      expect(error).toBeInstanceOf(ClawDeploymentError);
      expect((error as ClawDeploymentError).message).toContain(
        "Failed to recreate container for instance type change",
      );
    });
  });

  describe("warmUp", () => {
    it.effect("sends warm-up request to dispatch worker", () => {
      const { layer, seedContainer } = createTestLayer();
      seedContainer(INTERNAL_HOSTNAME);

      return Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        yield* deployment.warmUp(testConfig.clawId);
      }).pipe(Effect.provide(layer));
    });

    it("triggers cold start for new container", async () => {
      // warmUp succeeds even without pre-existing state — it triggers
      // a cold start on the dispatch worker which creates the container.
      await run(
        Effect.gen(function* () {
          const deployment = yield* ClawDeploymentService;
          yield* deployment.warmUp(testConfig.clawId);
        }),
      );
    });
  });
});
