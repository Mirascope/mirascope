/* v8 ignore file -- pure type definitions */
/**
 * @fileoverview Types for Cloudflare R2 bucket management.
 *
 * These types model the Cloudflare REST API responses for R2 operations.
 */

/**
 * R2 bucket info as returned by the Cloudflare API.
 */
export interface R2BucketInfo {
  /** Bucket name */
  name: string;

  /** ISO timestamp of when the bucket was created */
  creationDate: string;

  /** Location hint (e.g., "WNAM", "ENAM", "WEUR") */
  location?: string;
}

/**
 * Scoped credentials for accessing a specific R2 bucket.
 *
 * These are S3-compatible credentials created via the Cloudflare API,
 * scoped to a single bucket with read+write permissions.
 *
 * IMPORTANT: The secretAccessKey is only available at creation time
 * and cannot be retrieved again.
 */
export interface R2ScopedCredentials {
  /** Token ID (also serves as the S3-compatible access key ID) */
  tokenId: string;

  /** S3-compatible access key ID */
  accessKeyId: string;

  /** S3-compatible secret access key (only returned at creation time) */
  secretAccessKey: string;

  /** Expiration date (ISO timestamp) if the token has an expiry */
  expiresOn?: string;
}
