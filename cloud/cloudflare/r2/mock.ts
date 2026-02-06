/**
 * @fileoverview Mock R2 service for development and testing.
 *
 * Simulates R2 bucket lifecycle operations with in-memory state.
 * Each call to `makeMockR2Layer()` creates an isolated instance with
 * its own state, eliminating cross-test pollution.
 *
 * ## Behavior
 *
 * - `createBucket` — Tracks bucket in memory, fails if already exists
 * - `deleteBucket` — Removes from memory, fails if not found
 * - `getBucket` — Returns info from memory, fails if not found
 * - `listBuckets` — Returns all tracked buckets, optionally filtered by substring (matches `name_contains`)
 * - `createScopedCredentials` — Returns fake credentials, fails if bucket not found
 * - `revokeScopedCredentials` — Removes tracked credentials, fails if not found
 */

import { Effect, Layer } from "effect";

import type { R2BucketInfo, R2ScopedCredentials } from "@/cloudflare/r2/types";

import { CloudflareR2Service } from "@/cloudflare/r2/service";
import { CloudflareApiError } from "@/errors";

/**
 * Creates a fresh mock R2 service layer with isolated state.
 *
 * Each invocation gets its own in-memory Maps, so parallel tests
 * or multiple test files cannot interfere with each other.
 *
 * ```ts
 * const layer = makeMockR2Layer();
 * await Effect.runPromise(program.pipe(Effect.provide(layer)));
 * ```
 */
export function makeMockR2Layer() {
  const buckets = new Map<string, R2BucketInfo>();
  const tokens = new Map<string, { bucketName: string }>();
  let tokenCounter = 0;

  return Layer.succeed(CloudflareR2Service, {
    createBucket: (name: string) =>
      Effect.gen(function* () {
        if (buckets.has(name)) {
          return yield* Effect.fail(
            new CloudflareApiError({
              message: `Bucket already exists: ${name}`,
            }),
          );
        }

        const info: R2BucketInfo = {
          name,
          creationDate: new Date().toISOString(),
          location: "WNAM",
        };

        buckets.set(name, info);
        return info;
      }),

    deleteBucket: (name: string) =>
      Effect.gen(function* () {
        if (!buckets.has(name)) {
          return yield* Effect.fail(
            new CloudflareApiError({
              message: `Bucket not found: ${name}`,
            }),
          );
        }

        buckets.delete(name);
      }),

    getBucket: (name: string) =>
      Effect.gen(function* () {
        const info = buckets.get(name);
        if (!info) {
          return yield* Effect.fail(
            new CloudflareApiError({
              message: `Bucket not found: ${name}`,
            }),
          );
        }
        return info;
      }),

    listBuckets: (prefix?: string) =>
      Effect.sync(() => {
        const all = Array.from(buckets.values());
        if (prefix) {
          return all.filter((b) => b.name.includes(prefix));
        }
        return all;
      }),

    createScopedCredentials: (bucketName: string) =>
      Effect.gen(function* () {
        if (!buckets.has(bucketName)) {
          return yield* Effect.fail(
            new CloudflareApiError({
              message: `Cannot create credentials: bucket not found: ${bucketName}`,
            }),
          );
        }

        tokenCounter++;
        const tokenId = `mock-token-${tokenCounter}`;

        tokens.set(tokenId, { bucketName });

        const credentials: R2ScopedCredentials = {
          tokenId,
          accessKeyId: tokenId,
          secretAccessKey: `mock-secret-${tokenCounter}`,
        };

        return credentials;
      }),

    revokeScopedCredentials: (tokenId: string) =>
      Effect.gen(function* () {
        if (!tokens.has(tokenId)) {
          return yield* Effect.fail(
            new CloudflareApiError({
              message: `Token not found: ${tokenId}`,
            }),
          );
        }

        tokens.delete(tokenId);
      }),
  });
}
