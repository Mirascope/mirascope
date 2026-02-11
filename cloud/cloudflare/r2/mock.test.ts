/**
 * @fileoverview Tests for the mock R2 service.
 *
 * Verifies that makeMockR2Layer implements the CloudflareR2Service
 * interface correctly and all operations behave as expected.
 *
 * Each test creates a fresh layer via makeMockR2Layer(), ensuring
 * isolated state without needing reset functions.
 */

import { describe, it, expect } from "@effect/vitest";
import { Effect } from "effect";

import { makeMockR2Layer } from "@/cloudflare/r2/mock";
import { CloudflareR2Service } from "@/cloudflare/r2/service";
import { CloudflareApiError } from "@/errors";

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
    it.effect("creates a bucket and returns info", () =>
      Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        const info = yield* r2.createBucket("claw-test-123");

        expect(info.name).toBe("claw-test-123");
        expect(info.creationDate).toBeDefined();
        expect(info.location).toBe("WNAM");
      }).pipe(Effect.provide(makeMockR2Layer())),
    );

    it.effect("fails if bucket already exists", () =>
      Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        yield* r2.createBucket("claw-test-123");
        const error = yield* r2.createBucket("claw-test-123").pipe(Effect.flip);

        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain(
          "already exists",
        );
      }).pipe(Effect.provide(makeMockR2Layer())),
    );
  });

  describe("deleteBucket", () => {
    it.effect("deletes a bucket", () =>
      Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        yield* r2.createBucket("claw-test-123");
        yield* r2.deleteBucket("claw-test-123");
        // getBucket should fail after deletion
        const error = yield* r2.getBucket("claw-test-123").pipe(Effect.flip);

        expect(error).toBeInstanceOf(CloudflareApiError);
      }).pipe(Effect.provide(makeMockR2Layer())),
    );

    it.effect("fails for non-existent bucket", () =>
      Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        const error = yield* r2
          .deleteBucket("does-not-exist")
          .pipe(Effect.flip);

        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain("not found");
      }).pipe(Effect.provide(makeMockR2Layer())),
    );

    it.effect("allows re-creation after deletion", () =>
      Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        yield* r2.createBucket("claw-test-123");
        yield* r2.deleteBucket("claw-test-123");
        const info = yield* r2.createBucket("claw-test-123");

        expect(info.name).toBe("claw-test-123");
      }).pipe(Effect.provide(makeMockR2Layer())),
    );
  });

  describe("getBucket", () => {
    it.effect("returns info for existing bucket", () =>
      Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        yield* r2.createBucket("claw-test-123");
        const info = yield* r2.getBucket("claw-test-123");

        expect(info.name).toBe("claw-test-123");
      }).pipe(Effect.provide(makeMockR2Layer())),
    );

    it.effect("fails for non-existent bucket", () =>
      Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        const error = yield* r2.getBucket("does-not-exist").pipe(Effect.flip);

        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain("not found");
      }).pipe(Effect.provide(makeMockR2Layer())),
    );
  });

  describe("listBuckets", () => {
    it.effect("returns all buckets", () =>
      Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        yield* r2.createBucket("claw-aaa");
        yield* r2.createBucket("claw-bbb");
        yield* r2.createBucket("other-bucket");
        const buckets = yield* r2.listBuckets();

        expect(buckets).toHaveLength(3);
      }).pipe(Effect.provide(makeMockR2Layer())),
    );

    it.effect(
      "filters by substring using includes (matches name_contains)",
      () =>
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          yield* r2.createBucket("claw-aaa");
          yield* r2.createBucket("claw-bbb");
          yield* r2.createBucket("other-bucket");
          const buckets = yield* r2.listBuckets("claw-");

          expect(buckets).toHaveLength(2);
          expect(buckets.every((b) => b.name.includes("claw-"))).toBe(true);
        }).pipe(Effect.provide(makeMockR2Layer())),
    );

    it.effect("matches substring anywhere in bucket name", () =>
      Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        yield* r2.createBucket("claw-aaa");
        yield* r2.createBucket("not-claw-bbb");
        yield* r2.createBucket("other-claw-ccc");
        const buckets = yield* r2.listBuckets("claw-");

        expect(buckets).toHaveLength(3);
      }).pipe(Effect.provide(makeMockR2Layer())),
    );

    it.effect("returns empty array when no buckets exist", () =>
      Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        const buckets = yield* r2.listBuckets();

        expect(buckets).toHaveLength(0);
      }).pipe(Effect.provide(makeMockR2Layer())),
    );
  });

  describe("createScopedCredentials", () => {
    it.effect("returns credentials for an existing bucket", () =>
      Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        yield* r2.createBucket("claw-test-123");
        const creds = yield* r2.createScopedCredentials("claw-test-123");

        expect(creds.tokenId).toBeDefined();
        expect(creds.accessKeyId).toBeDefined();
        expect(creds.secretAccessKey).toBeDefined();
      }).pipe(Effect.provide(makeMockR2Layer())),
    );

    it.effect("fails if bucket does not exist", () =>
      Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        const error = yield* r2
          .createScopedCredentials("does-not-exist")
          .pipe(Effect.flip);

        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain(
          "bucket not found",
        );
      }).pipe(Effect.provide(makeMockR2Layer())),
    );

    it.effect("generates unique credentials for each call", () =>
      Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        yield* r2.createBucket("claw-test-123");
        const creds1 = yield* r2.createScopedCredentials("claw-test-123");
        const creds2 = yield* r2.createScopedCredentials("claw-test-123");

        expect(creds1.tokenId).not.toBe(creds2.tokenId);
        expect(creds1.secretAccessKey).not.toBe(creds2.secretAccessKey);
      }).pipe(Effect.provide(makeMockR2Layer())),
    );

    it.effect("fails after bucket is deleted", () =>
      Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        yield* r2.createBucket("claw-test-123");
        yield* r2.deleteBucket("claw-test-123");
        const error = yield* r2
          .createScopedCredentials("claw-test-123")
          .pipe(Effect.flip);

        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain(
          "bucket not found",
        );
      }).pipe(Effect.provide(makeMockR2Layer())),
    );
  });

  describe("revokeScopedCredentials", () => {
    it.effect("revokes existing credentials", () =>
      Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        yield* r2.createBucket("claw-test-123");
        const creds = yield* r2.createScopedCredentials("claw-test-123");
        yield* r2.revokeScopedCredentials(creds.tokenId);
      }).pipe(Effect.provide(makeMockR2Layer())),
    );

    it.effect("fails for non-existent token", () =>
      Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        const error = yield* r2
          .revokeScopedCredentials("fake-token-id")
          .pipe(Effect.flip);

        expect(error).toBeInstanceOf(CloudflareApiError);
        expect((error as CloudflareApiError).message).toContain(
          "Token not found",
        );
      }).pipe(Effect.provide(makeMockR2Layer())),
    );

    it.effect("prevents double-revoke", () =>
      Effect.gen(function* () {
        const r2 = yield* CloudflareR2Service;
        yield* r2.createBucket("claw-test-123");
        const creds = yield* r2.createScopedCredentials("claw-test-123");
        yield* r2.revokeScopedCredentials(creds.tokenId);
        const error = yield* r2
          .revokeScopedCredentials(creds.tokenId)
          .pipe(Effect.flip);

        expect(error).toBeInstanceOf(CloudflareApiError);
      }).pipe(Effect.provide(makeMockR2Layer())),
    );
  });

  describe("state isolation", () => {
    it.effect("each layer has independent state", () => {
      const layer1 = makeMockR2Layer();
      const layer2 = makeMockR2Layer();

      return Effect.gen(function* () {
        // Create bucket in layer1
        yield* Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          yield* r2.createBucket("isolated-bucket");
        }).pipe(Effect.provide(layer1));

        // Should not exist in layer2
        const error = yield* Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          return yield* r2.getBucket("isolated-bucket");
        }).pipe(Effect.flip, Effect.provide(layer2));

        expect(error).toBeInstanceOf(CloudflareApiError);
      });
    });
  });
});
