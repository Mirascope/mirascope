/**
 * @fileoverview Shared test utilities for Cloudflare service tests.
 *
 * Provides a lightweight VCR/cassette system for CloudflareHttp that
 * records and replays HTTP interactions. Use this to:
 *
 * 1. Build mock HTTP clients from recorded API responses
 * 2. Assert that services make the expected API calls
 * 3. Snapshot real API interactions and replay them deterministically
 *
 * ## Usage
 *
 * ```ts
 * const recorder = makeHttpRecorder();
 *
 * // Record expected interactions
 * recorder.on("GET", "/accounts/abc/r2/buckets/my-bucket", {
 *   name: "my-bucket",
 *   creation_date: "2025-01-15T00:00:00Z",
 * });
 *
 * // Use as a CloudflareHttp layer
 * const layer = MyLiveService.pipe(
 *   Layer.provide(Layer.merge(recorder.layer, settingsLayer)),
 * );
 *
 * // After test, inspect recorded calls
 * expect(recorder.calls).toHaveLength(1);
 * expect(recorder.calls[0].method).toBe("GET");
 * ```
 */

import { Effect, Layer } from "effect";

import type { CloudflareRequestOptions } from "@/claws/cloudflare/client";

import { CloudflareHttp } from "@/claws/cloudflare/client";
import { CloudflareApiError } from "@/errors";

/**
 * A recorded HTTP interaction.
 */
export interface RecordedCall {
  method: string;
  path: string;
  body?: unknown;
}

/**
 * A canned response for a specific method + path pattern.
 */
interface CannedResponse {
  method: string;
  pathPattern: string;
  response: unknown;
  error?: CloudflareApiError;
}

/**
 * Creates a recording HTTP client for testing Cloudflare service layers.
 *
 * Records all requests and allows canning responses by method + path.
 * Unmatched requests fail with a descriptive error.
 */
export function makeHttpRecorder() {
  const calls: RecordedCall[] = [];
  const responses: CannedResponse[] = [];

  /**
   * Register a canned success response for a method + path pattern.
   *
   * The path is matched as a substring, so `/r2/buckets` will match
   * `/accounts/abc/r2/buckets?per_page=1000`.
   */
  function on(method: string, pathPattern: string, response: unknown): void {
    responses.push({ method, pathPattern, response });
  }

  /**
   * Register a canned error response for a method + path pattern.
   */
  function onError(
    method: string,
    pathPattern: string,
    error: CloudflareApiError,
  ): void {
    responses.push({ method, pathPattern, response: null, error });
  }

  const layer = Layer.succeed(CloudflareHttp, {
    request: <T>(options: CloudflareRequestOptions) => {
      calls.push({
        method: options.method,
        path: options.path,
        body: options.body,
      });

      const match = responses.find(
        (r) =>
          r.method === options.method && options.path.includes(r.pathPattern),
      );

      if (!match) {
        return Effect.fail(
          new CloudflareApiError({
            message: `No canned response for ${options.method} ${options.path}`,
          }),
        ) as Effect.Effect<T, CloudflareApiError>;
      }

      if (match.error) {
        return Effect.fail(match.error) as Effect.Effect<T, CloudflareApiError>;
      }

      return Effect.succeed(match.response as T);
    },
  });

  return { calls, on, onError, layer };
}
