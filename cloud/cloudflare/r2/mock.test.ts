/**
 * @fileoverview Tests for the mock R2 service.
 *
 * Verifies that makeMockR2Layer implements the CloudflareR2Service
 * interface correctly and all operations behave as expected.
 *
 * Each test creates a fresh layer via makeMockR2Layer(), ensuring
 * isolated state without needing reset functions.
 */

import { Effect } from "effect";
import { describe, it, expect } from "vitest";

import { makeMockR2Layer } from "@/cloudflare/r2/mock";
import { CloudflareR2Service } from "@/cloudflare/r2/service";
import { CloudflareApiError } from "@/errors";

function run<A, E>(effect: Effect.Effect<A, E, CloudflareR2Service>) {
  const layer = makeMockR2Layer();
  return Effect.runPromise(effect.pipe(Effect.provide(layer)));
}

function runFail<A, E>(effect: Effect.Effect<A, E, CloudflareR2Service>) {
  const layer = makeMockR2Layer();
  return Effect.runPromise(effect.pipe(Effect.flip, Effect.provide(layer)));
}

describe("CloudflareApiError", () => {
  it("has correct tag and status", () => {
    const error = new CloudflareApiError({ message: "test error" });
    expect(error._tag).toBe("CloudflareApiError");
    expect(CloudflareApiError.status).toBe(502);
    expect(error.message).toBe("test error");
  });

  it("supports optional cause", () => {
    const cause = new Error("underlying");
    const error = new CloudflareApiError({
      message: "test error",
      cause,
    });
    expect(error.cause).toBe(cause);
  });
});

describe("MockCloudflareR2Service", () => {
  describe("createBucket", () => {
    it("creates a bucket and returns info", async () => {
      const info = await run(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.createBucket("claw-test-123");
        }),
      );

      expect(info.name).toBe("claw-test-123");
      expect(info.creationDate).toBeDefined();
      expect(info.location).toBe("WNAM");
    });

    it("fails if bucket already exists", async () => {
      const error = await runFail(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          yield* r2.createBucket("claw-test-123");
          return yield* r2.createBucket("claw-test-123");
        }),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
      expect((error as CloudflareApiError).message).toContain("already exists");
    });
  });

  describe("deleteBucket", () => {
    it("deletes a bucket", async () => {
      const error = await runFail(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          yield* r2.createBucket("claw-test-123");
          yield* r2.deleteBucket("claw-test-123");
          // getBucket should fail after deletion
          return yield* r2.getBucket("claw-test-123");
        }),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
    });

    it("fails for non-existent bucket", async () => {
      const error = await runFail(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.deleteBucket("does-not-exist");
        }),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
      expect((error as CloudflareApiError).message).toContain("not found");
    });

    it("allows re-creation after deletion", async () => {
      const info = await run(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          yield* r2.createBucket("claw-test-123");
          yield* r2.deleteBucket("claw-test-123");
          return yield* r2.createBucket("claw-test-123");
        }),
      );

      expect(info.name).toBe("claw-test-123");
    });
  });

  describe("getBucket", () => {
    it("returns info for existing bucket", async () => {
      const info = await run(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          yield* r2.createBucket("claw-test-123");
          return yield* r2.getBucket("claw-test-123");
        }),
      );

      expect(info.name).toBe("claw-test-123");
    });

    it("fails for non-existent bucket", async () => {
      const error = await runFail(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.getBucket("does-not-exist");
        }),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
      expect((error as CloudflareApiError).message).toContain("not found");
    });
  });

  describe("listBuckets", () => {
    it("returns all buckets", async () => {
      const buckets = await run(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          yield* r2.createBucket("claw-aaa");
          yield* r2.createBucket("claw-bbb");
          yield* r2.createBucket("other-bucket");
          return yield* r2.listBuckets();
        }),
      );

      expect(buckets).toHaveLength(3);
    });

    it("filters by substring using includes (matches name_contains)", async () => {
      const buckets = await run(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          yield* r2.createBucket("claw-aaa");
          yield* r2.createBucket("claw-bbb");
          yield* r2.createBucket("other-bucket");
          return yield* r2.listBuckets("claw-");
        }),
      );

      expect(buckets).toHaveLength(2);
      expect(buckets.every((b) => b.name.includes("claw-"))).toBe(true);
    });

    it("matches substring anywhere in bucket name", async () => {
      const buckets = await run(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          yield* r2.createBucket("claw-aaa");
          yield* r2.createBucket("not-claw-bbb");
          yield* r2.createBucket("other-claw-ccc");
          return yield* r2.listBuckets("claw-");
        }),
      );

      expect(buckets).toHaveLength(3);
    });

    it("returns empty array when no buckets exist", async () => {
      const buckets = await run(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.listBuckets();
        }),
      );

      expect(buckets).toHaveLength(0);
    });
  });

  describe("createScopedCredentials", () => {
    it("returns credentials for an existing bucket", async () => {
      const creds = await run(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          yield* r2.createBucket("claw-test-123");
          return yield* r2.createScopedCredentials("claw-test-123");
        }),
      );

      expect(creds.tokenId).toBeDefined();
      expect(creds.accessKeyId).toBeDefined();
      expect(creds.secretAccessKey).toBeDefined();
    });

    it("fails if bucket does not exist", async () => {
      const error = await runFail(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.createScopedCredentials("does-not-exist");
        }),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
      expect((error as CloudflareApiError).message).toContain(
        "bucket not found",
      );
    });

    it("generates unique credentials for each call", async () => {
      const { creds1, creds2 } = await run(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          yield* r2.createBucket("claw-test-123");
          const creds1 = yield* r2.createScopedCredentials("claw-test-123");
          const creds2 = yield* r2.createScopedCredentials("claw-test-123");
          return { creds1, creds2 };
        }),
      );

      expect(creds1.tokenId).not.toBe(creds2.tokenId);
      expect(creds1.secretAccessKey).not.toBe(creds2.secretAccessKey);
    });

    it("fails after bucket is deleted", async () => {
      const error = await runFail(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          yield* r2.createBucket("claw-test-123");
          yield* r2.deleteBucket("claw-test-123");
          return yield* r2.createScopedCredentials("claw-test-123");
        }),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
      expect((error as CloudflareApiError).message).toContain(
        "bucket not found",
      );
    });
  });

  describe("revokeScopedCredentials", () => {
    it("revokes existing credentials", async () => {
      await run(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          yield* r2.createBucket("claw-test-123");
          const creds = yield* r2.createScopedCredentials("claw-test-123");
          yield* r2.revokeScopedCredentials(creds.tokenId);
        }),
      );
    });

    it("fails for non-existent token", async () => {
      const error = await runFail(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.revokeScopedCredentials("fake-token-id");
        }),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
      expect((error as CloudflareApiError).message).toContain(
        "Token not found",
      );
    });

    it("prevents double-revoke", async () => {
      const error = await runFail(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          yield* r2.createBucket("claw-test-123");
          const creds = yield* r2.createScopedCredentials("claw-test-123");
          yield* r2.revokeScopedCredentials(creds.tokenId);
          return yield* r2.revokeScopedCredentials(creds.tokenId);
        }),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
    });
  });

  describe("state isolation", () => {
    it("each layer has independent state", async () => {
      const layer1 = makeMockR2Layer();
      const layer2 = makeMockR2Layer();

      // Create bucket in layer1
      await Effect.runPromise(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          yield* r2.createBucket("isolated-bucket");
        }).pipe(Effect.provide(layer1)),
      );

      // Should not exist in layer2
      const error = await Effect.runPromise(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.getBucket("isolated-bucket");
        }).pipe(Effect.flip, Effect.provide(layer2)),
      );

      expect(error).toBeInstanceOf(CloudflareApiError);
    });
  });
});
