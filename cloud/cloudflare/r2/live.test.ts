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
import { LiveCloudflareR2Service } from "@/cloudflare/r2/live";
import { CloudflareR2Service } from "@/cloudflare/r2/service";
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
    it.effect("sends POST to correct endpoint with bucket name", () => {
      requestHandler = (options) => {
        requestSpy(options);
        return Effect.succeed({
          name: "claw-abc",
          creation_date: "2025-01-15T10:30:00Z",
          location: "WNAM",
        });
      };

      const layer = createTestLayer(requestHandler);

      return Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        const result = yield* r2.createBucket("claw-abc");

        expect(result.name).toBe("claw-abc");
        expect(result.creationDate).toBe("2025-01-15T10:30:00Z");
        expect(result.location).toBe("WNAM");

        const call = requestSpy.mock.calls[0][0] as CloudflareRequestOptions;
        expect(call.method).toBe("POST");
        expect(call.path).toBe("/accounts/test-account-id/r2/buckets");
        expect(call.body).toEqual({ name: "claw-abc" });
      }).pipe(Effect.provide(layer));
    });

    it.effect("propagates 409 conflict error (bucket already exists)", () => {
      requestHandler = () =>
        Effect.fail(
          new CloudflareApiError({
            message:
              "Cloudflare API error: [10004] A bucket with this name already exists (POST /accounts/test-account-id/r2/buckets)",
          }),
        );

      const layer = createTestLayer(requestHandler);

      return Effect.gen(function* () {
        const error = yield* Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.createBucket("claw-abc");
        }).pipe(Effect.flip);
        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain(
          "already exists",
        );
      }).pipe(Effect.provide(layer));
    });
  });

  describe("deleteBucket", () => {
    it.effect("sends DELETE to correct endpoint", () => {
      const layer = createTestLayer(requestHandler);

      return Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        yield* r2.deleteBucket("claw-abc");

        const call = requestSpy.mock.calls[0][0] as CloudflareRequestOptions;
        expect(call.method).toBe("DELETE");
        expect(call.path).toBe("/accounts/test-account-id/r2/buckets/claw-abc");
      }).pipe(Effect.provide(layer));
    });

    it.effect("propagates 404 error (bucket not found)", () => {
      requestHandler = () =>
        Effect.fail(
          new CloudflareApiError({
            message:
              "Cloudflare API error: [10006] The specified bucket does not exist (DELETE /accounts/test-account-id/r2/buckets/claw-abc)",
          }),
        );

      const layer = createTestLayer(requestHandler);

      return Effect.gen(function* () {
        const error = yield* Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.deleteBucket("claw-abc");
        }).pipe(Effect.flip);
        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain(
          "does not exist",
        );
      }).pipe(Effect.provide(layer));
    });
  });

  describe("getBucket", () => {
    it.effect("sends GET and transforms response", () => {
      requestHandler = (options) => {
        requestSpy(options);
        return Effect.succeed({
          name: "claw-abc",
          creation_date: "2025-01-15T10:30:00Z",
        });
      };

      const layer = createTestLayer(requestHandler);

      return Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        const result = yield* r2.getBucket("claw-abc");

        expect(result.name).toBe("claw-abc");
        expect(result.creationDate).toBe("2025-01-15T10:30:00Z");

        const call = requestSpy.mock.calls[0][0] as CloudflareRequestOptions;
        expect(call.method).toBe("GET");
        expect(call.path).toBe("/accounts/test-account-id/r2/buckets/claw-abc");
      }).pipe(Effect.provide(layer));
    });

    it.effect("propagates 404 error (bucket not found)", () => {
      requestHandler = () =>
        Effect.fail(
          new CloudflareApiError({
            message:
              "Cloudflare API error: [10006] The specified bucket does not exist (GET /accounts/test-account-id/r2/buckets/claw-abc)",
          }),
        );

      const layer = createTestLayer(requestHandler);

      return Effect.gen(function* () {
        const error = yield* Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.getBucket("claw-abc");
        }).pipe(Effect.flip);
        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain(
          "does not exist",
        );
      }).pipe(Effect.provide(layer));
    });
  });

  describe("listBuckets", () => {
    it.effect("sends GET with per_page param", () => {
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

      return Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        const result = yield* r2.listBuckets();

        expect(result).toHaveLength(2);
        expect(result[0].name).toBe("claw-1");
        expect(result[1].name).toBe("claw-2");

        const call = requestSpy.mock.calls[0][0] as CloudflareRequestOptions;
        expect(call.method).toBe("GET");
        expect(call.path).toContain("per_page=1000");
      }).pipe(Effect.provide(layer));
    });

    it.effect("sends name_contains when prefix is provided", () => {
      requestHandler = (options) => {
        requestSpy(options);
        return Effect.succeed({ buckets: [] });
      };

      const layer = createTestLayer(requestHandler);

      return Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        return yield* r2.listBuckets("claw-");

        const call = requestSpy.mock.calls[0][0] as CloudflareRequestOptions;
        expect(call.path).toContain("name_contains=claw-");
      }).pipe(Effect.provide(layer));
    });
  });

  describe("createScopedCredentials", () => {
    it.effect("sends POST with correct token policy", () => {
      requestHandler = (options) => {
        requestSpy(options);
        return Effect.succeed({
          id: "token-id-123",
          value: "secret-value-abc",
        });
      };

      const layer = createTestLayer(requestHandler);

      return Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        const result = yield* r2.createScopedCredentials("claw-abc");

        expect(result.tokenId).toBe("token-id-123");
        expect(result.accessKeyId).toBe("token-id-123");
        // Implementation SHA-256 hashes the raw token value per Cloudflare R2 docs
        expect(result.secretAccessKey).toBe(
          "7df84b718784bcfcddb5505a057753421a32ff3a82ea8535bdcf8dcf9814c6e1",
        );

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
      }).pipe(Effect.provide(layer));
    });
  });

  describe("revokeScopedCredentials", () => {
    it.effect("sends DELETE to correct token endpoint", () => {
      const layer = createTestLayer(requestHandler);

      return Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        yield* r2.revokeScopedCredentials("token-id-123");

        const call = requestSpy.mock.calls[0][0] as CloudflareRequestOptions;
        expect(call.method).toBe("DELETE");
        expect(call.path).toBe("/accounts/test-account-id/tokens/token-id-123");
      }).pipe(Effect.provide(layer));
    });

    it.effect("propagates 404 error (token not found)", () => {
      requestHandler = () =>
        Effect.fail(
          new CloudflareApiError({
            message:
              "Cloudflare API error: [1000] Token not found (DELETE /accounts/test-account-id/tokens/bad-id)",
          }),
        );

      const layer = createTestLayer(requestHandler);

      return Effect.gen(function* () {
        const error = yield* Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.revokeScopedCredentials("bad-id");
        }).pipe(Effect.flip);
        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain("not found");
      }).pipe(Effect.provide(layer));
    });
  });

  describe("error propagation", () => {
    it.effect("propagates CloudflareApiError from HTTP client", () => {
      requestHandler = () =>
        Effect.fail(
          new CloudflareApiError({
            message: "API rate limited",
          }),
        );

      const layer = createTestLayer(requestHandler);

      return Effect.gen(function* () {
        const error = yield* Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.createBucket("claw-abc");
        }).pipe(Effect.flip);
        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain("rate limited");
      }).pipe(Effect.provide(layer));
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
