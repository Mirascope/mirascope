/**
 * @fileoverview Tests for the shared Cloudflare test HTTP recorder utility.
 *
 * Verifies that makeHttpRecorder correctly records calls, matches canned
 * responses, and reports errors for unmatched requests.
 */

import { describe, it, expect } from "@effect/vitest";
import { Effect, Layer } from "effect";

import type { CloudflareConfig } from "@/cloudflare/config";

import { CloudflareSettings } from "@/cloudflare/config";
import { LiveCloudflareR2Service } from "@/cloudflare/r2/live";
import { CloudflareR2Service } from "@/cloudflare/r2/service";
import { makeHttpRecorder } from "@/cloudflare/testing";
import { CloudflareApiError } from "@/errors";

const TEST_CONFIG: CloudflareConfig = {
  accountId: "test-account-id",
  apiToken: "test-api-token",
  r2BucketItemReadPermissionGroupId: "read-perm-id",
  r2BucketItemWritePermissionGroupId: "write-perm-id",
  durableObjectNamespaceId: "test-namespace-id",
  dispatchWorkerBaseUrl: "https://dispatch.test.workers.dev",
};

describe("makeHttpRecorder", () => {
  it.effect("records calls and returns canned responses", () => {
    const recorder = makeHttpRecorder();
    recorder.on("GET", "/r2/buckets/my-bucket", {
      name: "my-bucket",
      creation_date: "2025-01-15T00:00:00Z",
      location: "WNAM",
    });

    const settingsLayer = CloudflareSettings.layer(TEST_CONFIG);
    const layer = LiveCloudflareR2Service.pipe(
      Layer.provide(Layer.merge(recorder.layer, settingsLayer)),
    );

    return Effect.gen(function* () {
      const r2 = yield* CloudflareR2Service;
      const result = yield* r2.getBucket("my-bucket");

      expect(result.name).toBe("my-bucket");
      expect(recorder.calls).toHaveLength(1);
      expect(recorder.calls[0].method).toBe("GET");
      expect(recorder.calls[0].path).toContain("/r2/buckets/my-bucket");
    }).pipe(Effect.provide(layer));
  });

  it.effect("fails with descriptive error for unmatched requests", () => {
    const recorder = makeHttpRecorder();

    const settingsLayer = CloudflareSettings.layer(TEST_CONFIG);
    const layer = LiveCloudflareR2Service.pipe(
      Layer.provide(Layer.merge(recorder.layer, settingsLayer)),
    );

    return Effect.gen(function* () {
      const r2 = yield* CloudflareR2Service;
      const error = yield* r2.getBucket("missing-bucket").pipe(Effect.flip);

      expect(error).toBeInstanceOf(CloudflareApiError);
      expect((error as CloudflareApiError).message).toContain(
        "No canned response",
      );
    }).pipe(Effect.provide(layer));
  });

  it.effect("supports canned error responses via onError", () => {
    const recorder = makeHttpRecorder();
    recorder.onError(
      "GET",
      "/r2/buckets/bad-bucket",
      new CloudflareApiError({
        message: "Cloudflare API error: [10006] bucket does not exist",
      }),
    );

    const settingsLayer = CloudflareSettings.layer(TEST_CONFIG);
    const layer = LiveCloudflareR2Service.pipe(
      Layer.provide(Layer.merge(recorder.layer, settingsLayer)),
    );

    return Effect.gen(function* () {
      const r2 = yield* CloudflareR2Service;
      const error = yield* r2.getBucket("bad-bucket").pipe(Effect.flip);

      expect(error).toBeInstanceOf(CloudflareApiError);
      expect((error as CloudflareApiError).message).toContain("does not exist");
    }).pipe(Effect.provide(layer));
  });

  it.effect("records request bodies", () => {
    const recorder = makeHttpRecorder();
    recorder.on("POST", "/r2/buckets", {
      name: "new-bucket",
      creation_date: "2025-01-15T00:00:00Z",
    });

    const settingsLayer = CloudflareSettings.layer(TEST_CONFIG);
    const layer = LiveCloudflareR2Service.pipe(
      Layer.provide(Layer.merge(recorder.layer, settingsLayer)),
    );

    return Effect.gen(function* () {
      const r2 = yield* CloudflareR2Service;
      yield* r2.createBucket("new-bucket");

      expect(recorder.calls).toHaveLength(1);
      expect(recorder.calls[0].body).toEqual({ name: "new-bucket" });
    }).pipe(Effect.provide(layer));
  });
});
