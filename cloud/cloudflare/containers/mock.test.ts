/**
 * @fileoverview Tests for the mock container service.
 *
 * Verifies that makeMockContainerLayer implements the
 * CloudflareContainerService interface correctly.
 *
 * Each test creates a fresh layer via makeMockContainerLayer(), ensuring
 * isolated state without needing reset functions.
 */

import { describe, it, expect } from "@effect/vitest";
import { Effect } from "effect";

import { makeMockContainerLayer } from "@/cloudflare/containers/mock";
import { CloudflareContainerService } from "@/cloudflare/containers/service";
import { CloudflareApiError } from "@/errors";

const TEST_HOSTNAME = "my-claw.my-org.mirascope.com";

describe("MockCloudflareContainerService", () => {
  describe("recreate", () => {
    it.effect("recreates a running container", () => {
      const { layer, seed } = makeMockContainerLayer();
      seed(TEST_HOSTNAME);

      return Effect.gen(function* () {
        const containers = yield* CloudflareContainerService;
        yield* containers.recreate(TEST_HOSTNAME);
        const state = yield* containers.getState(TEST_HOSTNAME);
        expect(state.status).toBe("running");
      }).pipe(Effect.provide(layer));
    });

    it.effect("fails for non-existent container", () => {
      const { layer } = makeMockContainerLayer();

      return Effect.gen(function* () {
        const containers = yield* CloudflareContainerService;
        const error = yield* containers
          .recreate("unknown.host.com")
          .pipe(Effect.flip);
        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain("not found");
      }).pipe(Effect.provide(layer));
    });
  });

  describe("restartGateway", () => {
    it.effect("restarts gateway in a running container", () => {
      const { layer, seed } = makeMockContainerLayer();
      seed(TEST_HOSTNAME);

      return Effect.gen(function* () {
        const containers = yield* CloudflareContainerService;
        yield* containers.restartGateway(TEST_HOSTNAME);
        const state = yield* containers.getState(TEST_HOSTNAME);
        expect(state.status).toBe("running");
      }).pipe(Effect.provide(layer));
    });

    it.effect("fails for non-existent container", () => {
      const { layer } = makeMockContainerLayer();

      return Effect.gen(function* () {
        const containers = yield* CloudflareContainerService;
        const error = yield* containers
          .restartGateway("unknown.host.com")
          .pipe(Effect.flip);
        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain("not found");
      }).pipe(Effect.provide(layer));
    });
  });

  describe("destroy", () => {
    it.effect("destroys a running container", () => {
      const { layer, seed } = makeMockContainerLayer();
      seed(TEST_HOSTNAME);

      return Effect.gen(function* () {
        const containers = yield* CloudflareContainerService;
        yield* containers.destroy(TEST_HOSTNAME);
        const error = yield* containers
          .getState(TEST_HOSTNAME)
          .pipe(Effect.flip);
        expect(error).toBeInstanceOf(CloudflareApiError);
      }).pipe(Effect.provide(layer));
    });

    it.effect("fails for non-existent container", () => {
      const { layer } = makeMockContainerLayer();

      return Effect.gen(function* () {
        const containers = yield* CloudflareContainerService;
        const error = yield* containers
          .destroy("unknown.host.com")
          .pipe(Effect.flip);
        expect(error).toBeInstanceOf(CloudflareApiError);
      }).pipe(Effect.provide(layer));
    });
  });

  describe("getState", () => {
    it.effect("returns state for running container", () => {
      const { layer, seed } = makeMockContainerLayer();
      seed(TEST_HOSTNAME, { status: "healthy", lastChange: 1000 });

      return Effect.gen(function* () {
        const containers = yield* CloudflareContainerService;
        const state = yield* containers.getState(TEST_HOSTNAME);
        expect(state.status).toBe("healthy");
        expect(state.lastChange).toBe(1000);
      }).pipe(Effect.provide(layer));
    });

    it.effect("fails for non-existent container", () => {
      const { layer } = makeMockContainerLayer();

      return Effect.gen(function* () {
        const containers = yield* CloudflareContainerService;
        const error = yield* containers
          .getState("unknown.host.com")
          .pipe(Effect.flip);
        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain("not found");
      }).pipe(Effect.provide(layer));
    });
  });

  describe("warmUp", () => {
    it.effect("initializes a container", () => {
      const { layer } = makeMockContainerLayer();

      return Effect.gen(function* () {
        const containers = yield* CloudflareContainerService;
        yield* containers.warmUp(TEST_HOSTNAME);
        const state = yield* containers.getState(TEST_HOSTNAME);
        expect(state.status).toBe("running");
      }).pipe(Effect.provide(layer));
    });

    it.effect("does not overwrite existing container state", () => {
      const { layer, seed } = makeMockContainerLayer();
      seed(TEST_HOSTNAME, { status: "healthy", lastChange: 1000 });

      return Effect.gen(function* () {
        const containers = yield* CloudflareContainerService;
        yield* containers.warmUp(TEST_HOSTNAME);
        const state = yield* containers.getState(TEST_HOSTNAME);
        expect(state.status).toBe("healthy");
      }).pipe(Effect.provide(layer));
    });
  });

  describe("listInstances", () => {
    it.effect("returns empty list when no containers exist", () => {
      const { layer } = makeMockContainerLayer();

      return Effect.gen(function* () {
        const containers = yield* CloudflareContainerService;
        const instances = yield* containers.listInstances();
        expect(instances).toHaveLength(0);
      }).pipe(Effect.provide(layer));
    });

    it.effect("returns all seeded containers", () => {
      const { layer, seed } = makeMockContainerLayer();
      seed("c1.org.mirascope.com");
      seed("c2.org.mirascope.com");
      seed("c3.org.mirascope.com");

      return Effect.gen(function* () {
        const containers = yield* CloudflareContainerService;
        const instances = yield* containers.listInstances();
        expect(instances).toHaveLength(3);
        expect(instances.every((i) => i.hasStoredData)).toBe(true);
      }).pipe(Effect.provide(layer));
    });
  });

  describe("seed", () => {
    it.effect("seeds container with custom state", () => {
      const { layer, seed } = makeMockContainerLayer();
      seed(TEST_HOSTNAME, {
        status: "stopped",
        lastChange: 5000,
        exitCode: 1,
      });

      return Effect.gen(function* () {
        const containers = yield* CloudflareContainerService;
        const state = yield* containers.getState(TEST_HOSTNAME);
        expect(state.status).toBe("stopped");
        expect(state.exitCode).toBe(1);
      }).pipe(Effect.provide(layer));
    });
  });

  describe("state isolation", () => {
    it.effect("each layer has independent state", () => {
      const mock1 = makeMockContainerLayer();
      const mock2 = makeMockContainerLayer();
      mock1.seed(TEST_HOSTNAME);

      return Effect.gen(function* () {
        // Should exist in layer1
        const state = yield* Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          return yield* containers.getState(TEST_HOSTNAME);
        }).pipe(Effect.provide(mock1.layer));

        expect(state.status).toBe("running");

        // Should not exist in layer2
        const error = yield* Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          return yield* containers.getState(TEST_HOSTNAME);
        }).pipe(Effect.flip, Effect.provide(mock2.layer));

        expect(error).toBeInstanceOf(CloudflareApiError);
      });
    });
  });
});
