/* v8 ignore file -- service interface (Context.Tag), no testable logic */
/**
 * @fileoverview Cloudflare R2 service interface for bucket lifecycle management.
 *
 * Defines the `CloudflareR2Service` Effect interface that abstracts R2 bucket
 * operations: create/delete/get/list buckets and manage bucket-scoped
 * API tokens for S3-compatible access.
 *
 * ## Architecture
 *
 * ```
 * CloudflareR2Service (Context.Tag)
 *   ├── createBucket(name)              → Create an R2 bucket
 *   ├── deleteBucket(name)              → Delete an R2 bucket
 *   ├── getBucket(name)                 → Get bucket info
 *   ├── listBuckets(nameContains?)       → List buckets (optionally filtered)
 *   └── createScopedCredentials(bucket) → Create bucket-scoped API token
 * ```
 *
 * ## Usage
 *
 * ```ts
 * import { CloudflareR2Service } from "@/cloudflare/r2/service";
 *
 * const program = Effect.gen(function* () {
 *   const r2 = yield* CloudflareR2Service;
 *
 *   const bucket = yield* r2.createBucket("my-bucket");
 *   const creds = yield* r2.createScopedCredentials("my-bucket");
 * });
 * ```
 */

import { Context, Effect } from "effect";

import type { R2BucketInfo, R2ScopedCredentials } from "@/cloudflare/r2/types";

import { CloudflareApiError } from "@/errors";

/**
 * R2 service interface.
 *
 * Provides operations for managing R2 buckets and bucket-scoped credentials.
 */
export interface CloudflareR2ServiceInterface {
  /** Create an R2 bucket. */
  readonly createBucket: (
    name: string,
  ) => Effect.Effect<R2BucketInfo, CloudflareApiError>;

  /** Delete an R2 bucket. Bucket must be empty. */
  readonly deleteBucket: (
    name: string,
  ) => Effect.Effect<void, CloudflareApiError>;

  /** Get info for a specific bucket. */
  readonly getBucket: (
    name: string,
  ) => Effect.Effect<R2BucketInfo, CloudflareApiError>;

  /** List buckets, optionally filtered by substring match (`name_contains`). */
  readonly listBuckets: (
    prefix?: string,
  ) => Effect.Effect<R2BucketInfo[], CloudflareApiError>;

  /**
   * Create a scoped API token with read+write access to a specific bucket.
   *
   * The returned credentials are S3-compatible and can be used by the
   * dispatch worker to mount the bucket in the container.
   *
   * IMPORTANT: The secretAccessKey is only returned at creation time.
   */
  readonly createScopedCredentials: (
    bucketName: string,
  ) => Effect.Effect<R2ScopedCredentials, CloudflareApiError>;

  /**
   * Revoke (delete) a scoped API token.
   *
   * Used during deprovisioning to clean up bucket credentials.
   */
  readonly revokeScopedCredentials: (
    tokenId: string,
  ) => Effect.Effect<void, CloudflareApiError>;
}

/**
 * Cloudflare R2 service Effect tag.
 *
 * Use `yield* CloudflareR2Service` to access the R2 service in Effect generators.
 */
export class CloudflareR2Service extends Context.Tag("CloudflareR2Service")<
  CloudflareR2Service,
  CloudflareR2ServiceInterface
>() {}
