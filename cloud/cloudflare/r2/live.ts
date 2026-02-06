/**
 * @fileoverview Live implementation of CloudflareR2Service backed by the Cloudflare REST API.
 *
 * Makes real HTTP calls to Cloudflare's API v4 for R2 bucket management
 * and scoped token creation.
 *
 * ## Cloudflare API Endpoints Used
 *
 * - `POST   /accounts/{account_id}/r2/buckets` — Create bucket
 * - `DELETE  /accounts/{account_id}/r2/buckets/{name}` — Delete bucket
 * - `GET     /accounts/{account_id}/r2/buckets/{name}` — Get bucket
 * - `GET     /accounts/{account_id}/r2/buckets` — List buckets
 * - `POST    /accounts/{account_id}/tokens` — Create scoped API token
 * - `DELETE  /accounts/{account_id}/tokens/{token_id}` — Delete API token
 */

import { Effect, Layer } from "effect";

import type { CloudflareHttpClient } from "@/cloudflare/client";
import type { CloudflareConfig } from "@/cloudflare/config";
import type { R2BucketInfo, R2ScopedCredentials } from "@/cloudflare/r2/types";

import { CloudflareHttp } from "@/cloudflare/client";
import { CloudflareSettings } from "@/cloudflare/config";
import { CloudflareR2Service } from "@/cloudflare/r2/service";

/**
 * Raw Cloudflare API response shape for an R2 bucket.
 */
interface CloudflareBucketResult {
  name: string;
  creation_date: string;
  location?: string;
}

/**
 * Raw Cloudflare API response shape for listing buckets.
 */
interface CloudflareListBucketsResult {
  buckets: CloudflareBucketResult[];
}

/**
 * Raw Cloudflare API response for token creation.
 */
interface CloudflareTokenResult {
  id: string;
  value: string;
}

function toBucketInfo(raw: CloudflareBucketResult): R2BucketInfo {
  return {
    name: raw.name,
    creationDate: raw.creation_date,
    location: raw.location,
  };
}

function makeR2Service(http: CloudflareHttpClient, config: CloudflareConfig) {
  const accountPath = `/accounts/${config.accountId}`;

  return {
    createBucket: (name: string) =>
      Effect.gen(function* () {
        const raw = yield* http.request<CloudflareBucketResult>({
          method: "POST",
          path: `${accountPath}/r2/buckets`,
          body: { name },
        });
        return toBucketInfo(raw);
      }),

    deleteBucket: (name: string) =>
      Effect.gen(function* () {
        yield* http.request<Record<string, never>>({
          method: "DELETE",
          path: `${accountPath}/r2/buckets/${name}`,
        });
      }),

    getBucket: (name: string) =>
      Effect.gen(function* () {
        const raw = yield* http.request<CloudflareBucketResult>({
          method: "GET",
          path: `${accountPath}/r2/buckets/${name}`,
        });
        return toBucketInfo(raw);
      }),

    listBuckets: (prefix?: string) =>
      Effect.gen(function* () {
        const params = new URLSearchParams({ per_page: "1000" });
        if (prefix) {
          params.set("name_contains", prefix);
        }
        const raw = yield* http.request<CloudflareListBucketsResult>({
          method: "GET",
          path: `${accountPath}/r2/buckets?${params.toString()}`,
        });
        return raw.buckets.map(toBucketInfo);
      }),

    createScopedCredentials: (bucketName: string) =>
      Effect.gen(function* () {
        const resourceKey = `com.cloudflare.edge.r2.bucket.${config.accountId}_default_${bucketName}`;

        const raw = yield* http.request<CloudflareTokenResult>({
          method: "POST",
          path: `${accountPath}/tokens`,
          body: {
            name: `r2-scoped-${bucketName}`,
            policies: [
              {
                effect: "allow",
                permission_groups: [
                  { id: config.r2BucketItemReadPermissionGroupId },
                  { id: config.r2BucketItemWritePermissionGroupId },
                ],
                resources: {
                  [resourceKey]: "*",
                },
              },
            ],
          },
        });

        const credentials: R2ScopedCredentials = {
          tokenId: raw.id,
          accessKeyId: raw.id,
          secretAccessKey: raw.value,
        };

        return credentials;
      }),

    revokeScopedCredentials: (tokenId: string) =>
      Effect.gen(function* () {
        yield* http.request<Record<string, never>>({
          method: "DELETE",
          path: `${accountPath}/tokens/${tokenId}`,
        });
      }),
  };
}

/**
 * Live implementation of CloudflareR2Service.
 *
 * Requires CloudflareHttp and CloudflareSettings layers to be provided.
 */
export const LiveCloudflareR2Service = Layer.effect(
  CloudflareR2Service,
  Effect.gen(function* () {
    const http = yield* CloudflareHttp;
    const config = yield* CloudflareSettings;
    return makeR2Service(http, config);
  }),
);
