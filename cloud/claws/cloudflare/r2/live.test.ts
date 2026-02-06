/**
 * @fileoverview Tests for the live R2 service implementation.
 *
 * Uses a mock CloudflareHttp to verify the live R2 service
 * makes correct API calls and transforms responses properly.
 *
 * Includes both happy-path wire format tests and error path tests
 * to verify that different HTTP failure modes (404, 409, etc.)
 * propagate with distinguishable error messages.
 */

import { Effect, Layer } from "effect";
import { describe, it, expect, vi, beforeEach } from "vitest";

import type {
  CloudflareHttpClient,
  CloudflareRequestOptions,
} from "@/claws/cloudflare/client";
import type { CloudflareConfig } from "@/claws/cloudflare/config";

import { CloudflareHttp } from "@/claws/cloudflare/client";
import { CloudflareSettings } from "@/claws/cloudflare/config";
import { CloudflareApiError } from "@/errors";
import { LiveCloudflareR2Service } from "@/claws/cloudflare/r2/live";
import { CloudflareR2Service } from "@/claws/cloudflare/r2/service";

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
  return LiveCloudflareR2Service.pipe(
    Layer.provide(Layer.merge(httpLayer, settingsLayer)),
  );
}

describe("LiveCloudflareR2Service", () => {
  let requestSpy: ReturnType<
    typeof vi.fn<(options: CloudflareRequestOptions) => void>
  >;
  let requestHandler: RequestHandler;

  beforeEach(() => {
    requestSpy = vi.fn<(options: CloudflareRequestOptions) => void>();
    requestHandler = (options) => {
      requestSpy(options);
      return Effect.succeed({});
    };
  });

  describe("createBucket", () => {
    it("sends POST to correct endpoint with bucket name", async () => {
      requestHandler = (options) => {
        requestSpy(options);
        return Effect.succeed({
          name: "claw-abc",
          creation_date: "2025-01-15T10:30:00Z",
          location: "WNAM",
        });
      };

      const layer = createTestLayer(requestHandler);

      const result = await Effect.runPromise(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.createBucket("claw-abc");
        }).pipe(Effect.provide(layer)),
      );

      expect(result.name).toBe("claw-abc");
      expect(result.creationDate).toBe("2025-01-15T10:30:00Z");
      expect(result.location).toBe("WNAM");

      const call = requestSpy.mock.calls[0][0] as CloudflareRequestOptions;
      expect(call.method).toBe("POST");
      expect(call.path).toBe("/accounts/test-account-id/r2/buckets");
      expect(call.body).toEqual({ name: "claw-abc" });
    });

    it("propagates 409 conflict error (bucket already exists)", async () => {
      requestHandler = () =>
        Effect.fail(
          new CloudflareApiError({
            message:
              "Cloudflare API error: [10004] A bucket with this name already exists (POST /accounts/test-account-id/r2/buckets)",
          }),
        );

      const layer = createTestLayer(requestHandler);

      const error = await Effect.runPromise(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.createBucket("claw-abc");
        }).pipe(Effect.flip, Effect.provide(layer)),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
      expect((error as CloudflareApiError).message).toContain("already exists");
    });
  });

  describe("deleteBucket", () => {
    it("sends DELETE to correct endpoint", async () => {
      const layer = createTestLayer(requestHandler);

      await Effect.runPromise(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          yield* r2.deleteBucket("claw-abc");
        }).pipe(Effect.provide(layer)),
      );

      const call = requestSpy.mock.calls[0][0] as CloudflareRequestOptions;
      expect(call.method).toBe("DELETE");
      expect(call.path).toBe("/accounts/test-account-id/r2/buckets/claw-abc");
    });

    it("propagates 404 error (bucket not found)", async () => {
      requestHandler = () =>
        Effect.fail(
          new CloudflareApiError({
            message:
              "Cloudflare API error: [10006] The specified bucket does not exist (DELETE /accounts/test-account-id/r2/buckets/claw-abc)",
          }),
        );

      const layer = createTestLayer(requestHandler);

      const error = await Effect.runPromise(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.deleteBucket("claw-abc");
        }).pipe(Effect.flip, Effect.provide(layer)),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
      expect((error as CloudflareApiError).message).toContain("does not exist");
    });
  });

  describe("getBucket", () => {
    it("sends GET and transforms response", async () => {
      requestHandler = (options) => {
        requestSpy(options);
        return Effect.succeed({
          name: "claw-abc",
          creation_date: "2025-01-15T10:30:00Z",
        });
      };

      const layer = createTestLayer(requestHandler);

      const result = await Effect.runPromise(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.getBucket("claw-abc");
        }).pipe(Effect.provide(layer)),
      );

      expect(result.name).toBe("claw-abc");
      expect(result.creationDate).toBe("2025-01-15T10:30:00Z");

      const call = requestSpy.mock.calls[0][0] as CloudflareRequestOptions;
      expect(call.method).toBe("GET");
      expect(call.path).toBe("/accounts/test-account-id/r2/buckets/claw-abc");
    });

    it("propagates 404 error (bucket not found)", async () => {
      requestHandler = () =>
        Effect.fail(
          new CloudflareApiError({
            message:
              "Cloudflare API error: [10006] The specified bucket does not exist (GET /accounts/test-account-id/r2/buckets/claw-abc)",
          }),
        );

      const layer = createTestLayer(requestHandler);

      const error = await Effect.runPromise(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.getBucket("claw-abc");
        }).pipe(Effect.flip, Effect.provide(layer)),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
      expect((error as CloudflareApiError).message).toContain("does not exist");
    });
  });

  describe("listBuckets", () => {
    it("sends GET with per_page param", async () => {
      requestHandler = (options) => {
        requestSpy(options);
        return Effect.succeed({
          buckets: [
            { name: "claw-1", creation_date: "2025-01-01T00:00:00Z" },
            { name: "claw-2", creation_date: "2025-01-02T00:00:00Z" },
          ],
        });
      };

      const layer = createTestLayer(requestHandler);

      const result = await Effect.runPromise(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.listBuckets();
        }).pipe(Effect.provide(layer)),
      );

      expect(result).toHaveLength(2);
      expect(result[0].name).toBe("claw-1");
      expect(result[1].name).toBe("claw-2");

      const call = requestSpy.mock.calls[0][0] as CloudflareRequestOptions;
      expect(call.method).toBe("GET");
      expect(call.path).toContain("per_page=1000");
    });

    it("sends name_contains when prefix is provided", async () => {
      requestHandler = (options) => {
        requestSpy(options);
        return Effect.succeed({ buckets: [] });
      };

      const layer = createTestLayer(requestHandler);

      await Effect.runPromise(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.listBuckets("claw-");
        }).pipe(Effect.provide(layer)),
      );

      const call = requestSpy.mock.calls[0][0] as CloudflareRequestOptions;
      expect(call.path).toContain("name_contains=claw-");
    });
  });

  describe("createScopedCredentials", () => {
    it("sends POST with correct token policy", async () => {
      requestHandler = (options) => {
        requestSpy(options);
        return Effect.succeed({
          id: "token-id-123",
          value: "secret-value-abc",
        });
      };

      const layer = createTestLayer(requestHandler);

      const result = await Effect.runPromise(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.createScopedCredentials("claw-abc");
        }).pipe(Effect.provide(layer)),
      );

      expect(result.tokenId).toBe("token-id-123");
      expect(result.accessKeyId).toBe("token-id-123");
      expect(result.secretAccessKey).toBe("secret-value-abc");

      const call = requestSpy.mock.calls[0][0] as CloudflareRequestOptions;
      expect(call.method).toBe("POST");
      expect(call.path).toBe("/accounts/test-account-id/tokens");

      const body = call.body as {
        name: string;
        policies: {
          effect: string;
          permission_groups: { id: string }[];
          resources: Record<string, string>;
        }[];
      };
      expect(body.name).toBe("r2-scoped-claw-abc");
      expect(body.policies).toHaveLength(1);
      expect(body.policies[0].permission_groups).toEqual([
        { id: "read-perm-id" },
        { id: "write-perm-id" },
      ]);

      const expectedResource = `com.cloudflare.edge.r2.bucket.test-account-id_default_claw-abc`;
      expect(body.policies[0].resources[expectedResource]).toBe("*");
    });
  });

  describe("revokeScopedCredentials", () => {
    it("sends DELETE to correct token endpoint", async () => {
      const layer = createTestLayer(requestHandler);

      await Effect.runPromise(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          yield* r2.revokeScopedCredentials("token-id-123");
        }).pipe(Effect.provide(layer)),
      );

      const call = requestSpy.mock.calls[0][0] as CloudflareRequestOptions;
      expect(call.method).toBe("DELETE");
      expect(call.path).toBe("/accounts/test-account-id/tokens/token-id-123");
    });

    it("propagates 404 error (token not found)", async () => {
      requestHandler = () =>
        Effect.fail(
          new CloudflareApiError({
            message:
              "Cloudflare API error: [1000] Token not found (DELETE /accounts/test-account-id/tokens/bad-id)",
          }),
        );

      const layer = createTestLayer(requestHandler);

      const error = await Effect.runPromise(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.revokeScopedCredentials("bad-id");
        }).pipe(Effect.flip, Effect.provide(layer)),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
      expect((error as CloudflareApiError).message).toContain("not found");
    });
  });

  describe("error propagation", () => {
    it("propagates CloudflareApiError from HTTP client", async () => {
      requestHandler = () =>
        Effect.fail(
          new CloudflareApiError({
            message: "API rate limited",
          }),
        );

      const layer = createTestLayer(requestHandler);

      const error = await Effect.runPromise(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.createBucket("claw-abc");
        }).pipe(Effect.flip, Effect.provide(layer)),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
      expect((error as CloudflareApiError).message).toContain("rate limited");
    });

    it("preserves error messages for distinguishing failure types", async () => {
      const notFoundHandler: RequestHandler = () =>
        Effect.fail(
          new CloudflareApiError({
            message: "Cloudflare API error: [10006] bucket does not exist",
          }),
        );

      const authHandler: RequestHandler = () =>
        Effect.fail(
          new CloudflareApiError({
            message: "Cloudflare API error: [10000] Authentication error",
          }),
        );

      const notFoundLayer = createTestLayer(notFoundHandler);
      const authLayer = createTestLayer(authHandler);

      const notFoundError = await Effect.runPromise(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.getBucket("claw-abc");
        }).pipe(Effect.flip, Effect.provide(notFoundLayer)),
      );

      const authError = await Effect.runPromise(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.getBucket("claw-abc");
        }).pipe(Effect.flip, Effect.provide(authLayer)),
      );

      // Consumers can distinguish error types by message content
      expect((notFoundError as CloudflareApiError).message).toContain(
        "does not exist",
      );
      expect((authError as CloudflareApiError).message).toContain(
        "Authentication error",
      );
    });
  });
});
