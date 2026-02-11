/**
 * @fileoverview Contract tests for the R2 service against the real Cloudflare API.
 *
 * These tests verify that the live R2 service works correctly against the
 * real Cloudflare API. They are gated behind the CF_INTEGRATION env var
 * and intended to run nightly or on-demand, not in CI.
 *
 * ## Running
 *
 * ```bash
 * CF_INTEGRATION=1 CF_ACCOUNT_ID=xxx CF_API_TOKEN=xxx bun run vitest run cloudflare/r2/contract.test.ts
 * ```
 *
 * ## Requirements
 *
 * The following env vars must be set:
 * - CF_INTEGRATION — Set to any truthy value to enable
 * - CF_ACCOUNT_ID — Cloudflare account ID
 * - CF_API_TOKEN — API token with R2 admin permissions
 * - CF_R2_READ_PERM_ID — R2 bucket item read permission group ID
 * - CF_R2_WRITE_PERM_ID — R2 bucket item write permission group ID
 */

import { describe, it, expect } from "@effect/vitest";
import { Effect, Layer } from "effect";
import { afterAll } from "vitest";

import { CloudflareHttp } from "@/cloudflare/client";
import { CloudflareSettings } from "@/cloudflare/config";
import { LiveCloudflareR2Service } from "@/cloudflare/r2/live";
import { CloudflareR2Service } from "@/cloudflare/r2/service";

const TEST_BUCKET_PREFIX = "contract-test-";

function makeTestBucketName() {
  return `${TEST_BUCKET_PREFIX}${Date.now()}`;
}

describe.runIf(process.env.CF_INTEGRATION)("R2 contract tests", () => {
  const createdBuckets: string[] = [];

  const layer = LiveCloudflareR2Service.pipe(
    Layer.provide(
      Layer.merge(
        CloudflareHttp.Live(process.env.CF_API_TOKEN ?? ""),
        CloudflareSettings.layer({
          accountId: process.env.CF_ACCOUNT_ID ?? "",
          apiToken: process.env.CF_API_TOKEN ?? "",
          r2BucketItemReadPermissionGroupId:
            process.env.CF_R2_READ_PERM_ID ?? "",
          r2BucketItemWritePermissionGroupId:
            process.env.CF_R2_WRITE_PERM_ID ?? "",
          durableObjectNamespaceId: "",
          dispatchWorkerBaseUrl: "",
        }),
      ),
    ),
  );

  afterAll(async () => {
    // Clean up any test buckets that were created
    for (const name of createdBuckets) {
      await Effect.runPromise(
        Effect.gen(function* () {
          const r2 = yield* CloudflareR2Service;
          yield* r2.deleteBucket(name);
        }).pipe(Effect.provide(layer), Effect.ignore),
      );
    }
  });

  it.effect("createBucket → getBucket → deleteBucket lifecycle", () => {
    const bucketName = makeTestBucketName();
    createdBuckets.push(bucketName);

    return Effect.gen(function* () {
      const r2 = yield* CloudflareR2Service;

      // Create
      const created = yield* r2.createBucket(bucketName);
      expect(created.name).toBe(bucketName);

      // Get
      const fetched = yield* r2.getBucket(bucketName);
      expect(fetched.name).toBe(bucketName);
      expect(fetched.creationDate).toBeDefined();

      // Delete
      yield* r2.deleteBucket(bucketName);
    }).pipe(Effect.provide(layer));
  });

  it.effect("listBuckets returns created buckets", () => {
    const bucketName = makeTestBucketName();
    createdBuckets.push(bucketName);

    return Effect.gen(function* () {
      const r2 = yield* CloudflareR2Service;
      yield* r2.createBucket(bucketName);
      const buckets = yield* r2.listBuckets(TEST_BUCKET_PREFIX);
      expect(buckets.some((b) => b.name === bucketName)).toBe(true);
    }).pipe(Effect.provide(layer));
  });
});
