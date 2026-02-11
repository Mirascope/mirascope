/**
 * @fileoverview Low-level Cloudflare API HTTP client.
 *
 * Provides an Effect-native HTTP client for the Cloudflare REST API v4.
 * Handles the standard Cloudflare response envelope, authentication,
 * and error conversion.
 *
 * ## Cloudflare API v4 Response Envelope
 *
 * All Cloudflare API responses follow this format:
 * ```json
 * {
 *   "success": boolean,
 *   "errors": [{ "code": number, "message": string }],
 *   "messages": [string],
 *   "result": T
 * }
 * ```
 *
 * This client unwraps the envelope and returns just `result` on success,
 * or fails with `CloudflareApiError` on failure.
 */

import { Context, Effect, Layer } from "effect";

import { CloudflareApiError } from "@/errors";

const CLOUDFLARE_API_BASE = "https://api.cloudflare.com/client/v4";

/**
 * Cloudflare API v4 error entry.
 */
interface CloudflareApiErrorEntry {
  code: number;
  message: string;
}

/**
 * Cloudflare API v4 standard response envelope.
 */
interface CloudflareApiResponse<T> {
  success: boolean;
  errors: CloudflareApiErrorEntry[];
  messages: string[];
  result: T;
}

/**
 * Options for a Cloudflare API request.
 */
export interface CloudflareRequestOptions {
  method: "GET" | "POST" | "PUT" | "DELETE";
  path: string;
  body?: unknown;
  headers?: Record<string, string>;
}

/**
 * Low-level HTTP client interface for the Cloudflare API.
 *
 * Handles authentication, request construction, response envelope unwrapping,
 * and error conversion. All Cloudflare services use this to make API calls.
 */
export interface CloudflareHttpClient {
  /**
   * Make an authenticated request to the Cloudflare API.
   *
   * @param options - Request method, path (relative to /client/v4), and optional body
   * @returns The unwrapped `result` from the Cloudflare response envelope
   */
  readonly request: <T>(
    options: CloudflareRequestOptions,
  ) => Effect.Effect<T, CloudflareApiError>;
}

/**
 * Cloudflare HTTP client service tag.
 *
 * Use `yield* CloudflareHttp` to access the HTTP client in Effect generators.
 */
export class CloudflareHttp extends Context.Tag("CloudflareHttp")<
  CloudflareHttp,
  CloudflareHttpClient
>() {
  /**
   * Creates a live layer backed by the global `fetch` function.
   *
   * @param apiToken - Cloudflare API token for Bearer auth
   */
  static Live = (apiToken: string) =>
    Layer.succeed(CloudflareHttp, {
      request: <T>(options: CloudflareRequestOptions) =>
        Effect.gen(function* () {
          const url = `${CLOUDFLARE_API_BASE}${options.path}`;

          const headers: Record<string, string> = {
            Authorization: `Bearer ${apiToken}`,
            "Content-Type": "application/json",
            ...options.headers,
          };

          const response = yield* Effect.tryPromise({
            try: () =>
              fetch(url, {
                method: options.method,
                headers,
                body: options.body ? JSON.stringify(options.body) : undefined,
              }),
            catch: (error) =>
              new CloudflareApiError({
                message: `Cloudflare API request failed: ${options.method} ${options.path}`,
                cause: error,
              }),
          });

          const json = yield* Effect.tryPromise({
            try: () => response.json() as Promise<CloudflareApiResponse<T>>,
            catch: (error) =>
              new CloudflareApiError({
                message: `Failed to parse Cloudflare API response: ${options.method} ${options.path}`,
                cause: error,
              }),
          });

          if (!json.success) {
            const errorMessages = json.errors
              .map((e) => `[${e.code}] ${e.message}`)
              .join("; ");

            return yield* Effect.fail(
              new CloudflareApiError({
                message: `Cloudflare API error: ${errorMessages || "Unknown error"} (${options.method} ${options.path})`,
              }),
            );
          }

          return json.result;
        }),
    });
}
