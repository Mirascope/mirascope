/**
 * @fileoverview Tests for the mock container service.
 *
 * Verifies that makeMockContainerLayer implements the
 * CloudflareContainerService interface correctly.
 *
 * Each test creates a fresh layer via makeMockContainerLayer(), ensuring
 * isolated state without needing reset functions.
 */

import { Effect } from "effect";
import { describe, it, expect } from "vitest";

import { makeMockContainerLayer } from "@/claws/cloudflare/containers/mock";
import { CloudflareContainerService } from "@/claws/cloudflare/containers/service";
import { CloudflareApiError } from "@/errors";

const TEST_HOSTNAME = "my-claw.my-org.mirascope.com";

describe("MockCloudflareContainerService", () => {
  describe("recreate", () => {
    it("recreates a running container", async () => {
      const { layer, seed } = makeMockContainerLayer();
      seed(TEST_HOSTNAME);

      const state = await Effect.runPromise(
        Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          yield* containers.recreate(TEST_HOSTNAME);
          return yield* containers.getState(TEST_HOSTNAME);
        }).pipe(Effect.provide(layer)),
      );

      expect(state.status).toBe("running");
    });

    it("fails for non-existent container", async () => {
      const { layer } = makeMockContainerLayer();

      const error = await Effect.runPromise(
        Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          return yield* containers.recreate("unknown.host.com");
        }).pipe(Effect.flip, Effect.provide(layer)),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
      expect((error as CloudflareApiError).message).toContain("not found");
    });
  });

  describe("restartGateway", () => {
    it("restarts gateway in a running container", async () => {
      const { layer, seed } = makeMockContainerLayer();
      seed(TEST_HOSTNAME);

      const state = await Effect.runPromise(
        Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          yield* containers.restartGateway(TEST_HOSTNAME);
          return yield* containers.getState(TEST_HOSTNAME);
        }).pipe(Effect.provide(layer)),
      );

      expect(state.status).toBe("running");
    });

    it("fails for non-existent container", async () => {
      const { layer } = makeMockContainerLayer();

      const error = await Effect.runPromise(
        Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          return yield* containers.restartGateway("unknown.host.com");
        }).pipe(Effect.flip, Effect.provide(layer)),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
      expect((error as CloudflareApiError).message).toContain("not found");
    });
  });

  describe("destroy", () => {
    it("destroys a running container", async () => {
      const { layer, seed } = makeMockContainerLayer();
      seed(TEST_HOSTNAME);

      const error = await Effect.runPromise(
        Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          yield* containers.destroy(TEST_HOSTNAME);
          return yield* containers.getState(TEST_HOSTNAME);
        }).pipe(Effect.flip, Effect.provide(layer)),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
    });

    it("fails for non-existent container", async () => {
      const { layer } = makeMockContainerLayer();

      const error = await Effect.runPromise(
        Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          return yield* containers.destroy("unknown.host.com");
        }).pipe(Effect.flip, Effect.provide(layer)),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
    });
  });

  describe("getState", () => {
    it("returns state for running container", async () => {
      const { layer, seed } = makeMockContainerLayer();
      seed(TEST_HOSTNAME, { status: "healthy", lastChange: 1000 });

      const state = await Effect.runPromise(
        Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          return yield* containers.getState(TEST_HOSTNAME);
        }).pipe(Effect.provide(layer)),
      );

      expect(state.status).toBe("healthy");
      expect(state.lastChange).toBe(1000);
    });

    it("fails for non-existent container", async () => {
      const { layer } = makeMockContainerLayer();

      const error = await Effect.runPromise(
        Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          return yield* containers.getState("unknown.host.com");
        }).pipe(Effect.flip, Effect.provide(layer)),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
      expect((error as CloudflareApiError).message).toContain("not found");
    });
  });

  describe("warmUp", () => {
    it("initializes a container", async () => {
      const { layer } = makeMockContainerLayer();

      const state = await Effect.runPromise(
        Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          yield* containers.warmUp(TEST_HOSTNAME);
          return yield* containers.getState(TEST_HOSTNAME);
        }).pipe(Effect.provide(layer)),
      );

      expect(state.status).toBe("running");
    });

    it("does not overwrite existing container state", async () => {
      const { layer, seed } = makeMockContainerLayer();
      seed(TEST_HOSTNAME, { status: "healthy", lastChange: 1000 });

      const state = await Effect.runPromise(
        Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          yield* containers.warmUp(TEST_HOSTNAME);
          return yield* containers.getState(TEST_HOSTNAME);
        }).pipe(Effect.provide(layer)),
      );

      expect(state.status).toBe("healthy");
    });
  });

  describe("listInstances", () => {
    it("returns empty list when no containers exist", async () => {
      const { layer } = makeMockContainerLayer();

      const instances = await Effect.runPromise(
        Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          return yield* containers.listInstances();
        }).pipe(Effect.provide(layer)),
      );

      expect(instances).toHaveLength(0);
    });

    it("returns all seeded containers", async () => {
      const { layer, seed } = makeMockContainerLayer();
      seed("c1.org.mirascope.com");
      seed("c2.org.mirascope.com");
      seed("c3.org.mirascope.com");

      const instances = await Effect.runPromise(
        Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          return yield* containers.listInstances();
        }).pipe(Effect.provide(layer)),
      );

      expect(instances).toHaveLength(3);
      expect(instances.every((i) => i.hasStoredData)).toBe(true);
    });
  });

  describe("seed", () => {
    it("seeds container with custom state", async () => {
      const { layer, seed } = makeMockContainerLayer();
      seed(TEST_HOSTNAME, {
        status: "stopped",
        lastChange: 5000,
        exitCode: 1,
      });

      const state = await Effect.runPromise(
        Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          return yield* containers.getState(TEST_HOSTNAME);
        }).pipe(Effect.provide(layer)),
      );

      expect(state.status).toBe("stopped");
      expect(state.exitCode).toBe(1);
    });
  });

  describe("state isolation", () => {
    it("each layer has independent state", async () => {
      const mock1 = makeMockContainerLayer();
      const mock2 = makeMockContainerLayer();
      mock1.seed(TEST_HOSTNAME);

      // Should exist in layer1
      const state = await Effect.runPromise(
        Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          return yield* containers.getState(TEST_HOSTNAME);
        }).pipe(Effect.provide(mock1.layer)),
      );

      expect(state.status).toBe("running");

      // Should not exist in layer2
      const error = await Effect.runPromise(
        Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          return yield* containers.getState(TEST_HOSTNAME);
        }).pipe(Effect.flip, Effect.provide(mock2.layer)),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
    });
  });
});
