/**
 * @fileoverview Tests for the live container service implementation.
 *
 * Uses a mock CloudflareHttpClient and mocked fetch to verify the live
 * container service makes correct API calls and transforms responses properly.
 */

import { describe, it, expect } from "@effect/vitest";
import { Effect, Layer } from "effect";
import { vi, beforeEach } from "vitest";

import type {
  CloudflareHttpClient,
  CloudflareRequestOptions,
} from "@/cloudflare/client";
import type { CloudflareConfig } from "@/cloudflare/config";

import { CloudflareHttp } from "@/cloudflare/client";
import { CloudflareSettings } from "@/cloudflare/config";
import { LiveCloudflareContainerService } from "@/cloudflare/containers/live";
import { CloudflareContainerService } from "@/cloudflare/containers/service";
import { CloudflareApiError } from "@/errors";

const TEST_CONFIG: CloudflareConfig = {
  accountId: "test-account-id",
  apiToken: "test-api-token",
  r2BucketItemReadPermissionGroupId: "read-perm-id",
  r2BucketItemWritePermissionGroupId: "write-perm-id",
  durableObjectNamespaceId: "test-namespace-id",
  dispatchWorkerBaseUrl: "https://dispatch.test.workers.dev",
};

type RequestHandler = (
  options: CloudflareRequestOptions,
) => Effect.Effect<unknown, CloudflareApiError>;

function createMockHttpClient(handler: RequestHandler): CloudflareHttpClient {
  return {
    request: <T>(options: CloudflareRequestOptions) =>
      handler(options) as Effect.Effect<T, CloudflareApiError>,
  };
}

function createTestLayer(handler: RequestHandler) {
  const httpLayer = Layer.succeed(
    CloudflareHttp,
    createMockHttpClient(handler),
  );
  const settingsLayer = CloudflareSettings.layer(TEST_CONFIG);
  return LiveCloudflareContainerService.pipe(
    Layer.provide(Layer.merge(httpLayer, settingsLayer)),
  );
}

const TEST_HOSTNAME = "my-claw.my-org.mirascope.com";

describe("LiveCloudflareContainerService", () => {
  let fetchSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    vi.restoreAllMocks();
    // Default fetch mock for dispatch worker calls
    fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(
        new Response(JSON.stringify({ status: "ok" }), { status: 200 }),
      );
  });

  describe("recreate", () => {
    it.effect("sends POST to dispatch worker /_internal/recreate", () => {
      const handler: RequestHandler = () => Effect.succeed({});
      const layer = createTestLayer(handler);

      return Effect.gen(function* () {
        const containers = yield* CloudflareContainerService;
        yield* containers.recreate(TEST_HOSTNAME);

        expect(fetchSpy).toHaveBeenCalledWith(
          "https://dispatch.test.workers.dev/_internal/recreate",
          expect.objectContaining({
            method: "POST",
            headers: expect.objectContaining({
              Host: TEST_HOSTNAME,
              "X-Claw-Id": "my-claw",
            }),
          }),
        );
      }).pipe(Effect.provide(layer));
    });

    it.effect("fails when dispatch worker returns error", () => {
      fetchSpy.mockResolvedValue(
        new Response("Internal Server Error", {
          status: 500,
          statusText: "Internal Server Error",
        }),
      );

      const handler: RequestHandler = () => Effect.succeed({});
      const layer = createTestLayer(handler);

      return Effect.gen(function* () {
        const error = yield* Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          return yield* containers.recreate(TEST_HOSTNAME);
        }).pipe(Effect.flip);
        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain(
          "Recreate failed",
        );
        expect((error as CloudflareApiError).message).toContain("500");
      }).pipe(Effect.provide(layer));
    });
  });

  describe("restartGateway", () => {
    it.effect(
      "sends POST to dispatch worker /_internal/restart-gateway",
      () => {
        const handler: RequestHandler = () => Effect.succeed({});
        const layer = createTestLayer(handler);

        return Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          yield* containers.restartGateway(TEST_HOSTNAME);

          expect(fetchSpy).toHaveBeenCalledWith(
            "https://dispatch.test.workers.dev/_internal/restart-gateway",
            expect.objectContaining({
              method: "POST",
              headers: expect.objectContaining({
                Host: TEST_HOSTNAME,
                "X-Claw-Id": "my-claw",
              }),
            }),
          );
        }).pipe(Effect.provide(layer));
      },
    );

    it.effect("fails when dispatch worker returns error", () => {
      fetchSpy.mockResolvedValue(
        new Response("Internal Server Error", {
          status: 500,
          statusText: "Internal Server Error",
        }),
      );

      const handler: RequestHandler = () => Effect.succeed({});
      const layer = createTestLayer(handler);

      return Effect.gen(function* () {
        const error = yield* Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          return yield* containers.restartGateway(TEST_HOSTNAME);
        }).pipe(Effect.flip);
        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain(
          "Restart gateway failed",
        );
        expect((error as CloudflareApiError).message).toContain("500");
      }).pipe(Effect.provide(layer));
    });
  });

  describe("destroy", () => {
    it.effect("sends POST to dispatch worker /_internal/destroy", () => {
      const handler: RequestHandler = () => Effect.succeed({});
      const layer = createTestLayer(handler);

      return Effect.gen(function* () {
        const containers = yield* CloudflareContainerService;
        yield* containers.destroy(TEST_HOSTNAME);

        expect(fetchSpy).toHaveBeenCalledWith(
          "https://dispatch.test.workers.dev/_internal/destroy",
          expect.objectContaining({
            method: "POST",
          }),
        );
      }).pipe(Effect.provide(layer));
    });

    it.effect("fails when dispatch worker returns error", () => {
      fetchSpy.mockResolvedValue(
        new Response("Not Found", { status: 404, statusText: "Not Found" }),
      );

      const handler: RequestHandler = () => Effect.succeed({});
      const layer = createTestLayer(handler);

      return Effect.gen(function* () {
        const error = yield* Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          return yield* containers.destroy(TEST_HOSTNAME);
        }).pipe(Effect.flip);
        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain(
          "Destroy failed",
        );
      }).pipe(Effect.provide(layer));
    });
  });

  describe("getState", () => {
    it.effect("sends GET to dispatch worker /_internal/state", () => {
      fetchSpy.mockResolvedValue(
        new Response(
          JSON.stringify({
            status: "running",
            lastChange: 1705300200000,
          }),
          { status: 200 },
        ),
      );

      const handler: RequestHandler = () => Effect.succeed({});
      const layer = createTestLayer(handler);

      return Effect.gen(function* () {
        const containers = yield* CloudflareContainerService;
        const state = yield* containers.getState(TEST_HOSTNAME);

        expect(state.status).toBe("running");
        expect(state.lastChange).toBe(1705300200000);

        expect(fetchSpy).toHaveBeenCalledWith(
          "https://dispatch.test.workers.dev/_internal/state",
          expect.objectContaining({
            method: "GET",
            headers: expect.objectContaining({
              Host: TEST_HOSTNAME,
              "X-Claw-Id": "my-claw",
            }),
          }),
        );
      }).pipe(Effect.provide(layer));
    });

    it.effect("fails when dispatch worker returns error", () => {
      fetchSpy.mockResolvedValue(
        new Response("Not Found", { status: 404, statusText: "Not Found" }),
      );

      const handler: RequestHandler = () => Effect.succeed({});
      const layer = createTestLayer(handler);

      return Effect.gen(function* () {
        const error = yield* Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          return yield* containers.getState(TEST_HOSTNAME);
        }).pipe(Effect.flip);
        expect(error).toBeInstanceOf(CloudflareApiError);
      }).pipe(Effect.provide(layer));
    });

    it.effect("fails when response JSON is invalid", () => {
      fetchSpy.mockResolvedValue(new Response("not json", { status: 200 }));

      const handler: RequestHandler = () => Effect.succeed({});
      const layer = createTestLayer(handler);

      return Effect.gen(function* () {
        const error = yield* Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          return yield* containers.getState(TEST_HOSTNAME);
        }).pipe(Effect.flip);
        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain(
          "Failed to parse",
        );
      }).pipe(Effect.provide(layer));
    });
  });

  describe("warmUp", () => {
    it.effect("sends POST to dispatch worker /_internal/warm-up", () => {
      const handler: RequestHandler = () => Effect.succeed({});
      const layer = createTestLayer(handler);

      return Effect.gen(function* () {
        const containers = yield* CloudflareContainerService;
        yield* containers.warmUp(TEST_HOSTNAME);

        expect(fetchSpy).toHaveBeenCalledWith(
          "https://dispatch.test.workers.dev/_internal/warm-up",
          expect.objectContaining({
            method: "POST",
            headers: expect.objectContaining({
              Host: TEST_HOSTNAME,
            }),
          }),
        );
      }).pipe(Effect.provide(layer));
    });

    it.effect("fails when dispatch worker returns error", () => {
      fetchSpy.mockResolvedValue(
        new Response("Bad Gateway", {
          status: 502,
          statusText: "Bad Gateway",
        }),
      );

      const handler: RequestHandler = () => Effect.succeed({});
      const layer = createTestLayer(handler);

      return Effect.gen(function* () {
        const error = yield* Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          return yield* containers.warmUp(TEST_HOSTNAME);
        }).pipe(Effect.flip);
        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain(
          "Warm-up failed",
        );
        expect((error as CloudflareApiError).message).toContain("502");
      }).pipe(Effect.provide(layer));
    });

    it.effect("fails on network error", () => {
      fetchSpy.mockRejectedValue(new Error("Connection refused"));

      const handler: RequestHandler = () => Effect.succeed({});
      const layer = createTestLayer(handler);

      return Effect.gen(function* () {
        const error = yield* Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          return yield* containers.warmUp(TEST_HOSTNAME);
        }).pipe(Effect.flip);
        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain(
          "Dispatch worker request failed",
        );
      }).pipe(Effect.provide(layer));
    });
  });

  describe("listInstances", () => {
    it.effect("sends GET to Cloudflare API and returns instances", () => {
      const requestSpy = vi.fn();
      const handler: RequestHandler = (options) => {
        requestSpy(options);
        return Effect.succeed([
          { id: "aabbccdd", hasStoredData: true },
          { id: "eeff0011", hasStoredData: false },
        ]);
      };

      const layer = createTestLayer(handler);

      return Effect.gen(function* () {
        const containers = yield* CloudflareContainerService;
        const instances = yield* containers.listInstances();

        expect(instances).toHaveLength(2);
        expect(instances[0]).toEqual({ id: "aabbccdd", hasStoredData: true });
        expect(instances[1]).toEqual({ id: "eeff0011", hasStoredData: false });

        const call = requestSpy.mock.calls[0][0] as CloudflareRequestOptions;
        expect(call.method).toBe("GET");
        expect(call.path).toContain(
          "/accounts/test-account-id/workers/durable_objects/namespaces/test-namespace-id/objects",
        );
      }).pipe(Effect.provide(layer));
    });

    it.effect("propagates API errors", () => {
      const handler: RequestHandler = () =>
        Effect.fail(
          new CloudflareApiError({
            message: "Namespace not found",
          }),
        );

      const layer = createTestLayer(handler);

      return Effect.gen(function* () {
        const error = yield* Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          return yield* containers.listInstances();
        }).pipe(Effect.flip);
        expect(error).toBeInstanceOf(CloudflareApiError);
      }).pipe(Effect.provide(layer));
    });
  });

  describe("dispatch worker network errors", () => {
    it.effect("wraps fetch errors in CloudflareApiError", () => {
      fetchSpy.mockRejectedValue(new Error("DNS resolution failed"));

      const handler: RequestHandler = () => Effect.succeed({});
      const layer = createTestLayer(handler);

      return Effect.gen(function* () {
        const error = yield* Effect.gen(function* () {
          const containers = yield* CloudflareContainerService;
          return yield* containers.recreate(TEST_HOSTNAME);
        }).pipe(Effect.flip);
        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain(
          "Dispatch worker request failed",
        );
      }).pipe(Effect.provide(layer));
    });
  });
});
