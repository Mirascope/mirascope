/**
 * @fileoverview Proxy utility for forwarding requests to AI provider APIs.
 *
 * Provides utilities for proxying HTTP requests to external AI providers
 * (OpenAI, Anthropic, Google AI) while swapping authentication from user's
 * Mirascope API key to internal provider keys.
 */

import { Effect, Stream } from "effect";
import { ProxyError } from "@/errors";
import type { ProxyConfig, ProviderName } from "@/api/router/providers";
import { parseStreamingResponse } from "./streaming";
import type { TokenUsage } from "@/api/router/pricing";

/**
 * Extracts the path suffix after the provider prefix.
 *
 * @param pathname - The request pathname
 * @param provider - The provider name (e.g., "openai")
 * @returns The path to forward to the provider
 *
 * @example
 * extractProviderPath("/router/v0/openai/v1/chat/completions", "openai")
 * // Returns: "v1/chat/completions"
 */
export function extractProviderPath(
  pathname: string,
  provider: string,
): string {
  const prefix = `/router/v0/${provider}/`;
  if (pathname.startsWith(prefix)) {
    return pathname.slice(prefix.length);
  }

  return pathname;
}

/**
 * Result of proxying a request to a provider.
 */
export interface ProxyResult {
  /** The provider's response */
  response: Response;
  /**
   * Parsed JSON body if available, null otherwise.
   * For non-streaming: Contains the full response body (type varies by provider/endpoint).
   * For streaming: null (usage available via usageStream).
   */
  body: unknown;
  /**
   * For streaming responses only: Stream of usage data extracted from chunks.
   */
  usageStream?: Stream.Stream<TokenUsage, ProxyError>;
}

/**
 * Proxies an HTTP request to an AI provider.
 *
 * This function:
 * 1. Extracts the path to forward
 * 2. Copies request headers (excluding user auth and host)
 * 3. Sets provider authentication
 * 4. Forwards the request to the provider
 * 5. Clones and parses the response body for usage extraction
 * 6. Returns both the response and parsed body
 *
 * @param request - The incoming HTTP request
 * @param config - Provider configuration including API key
 * @param providerName - Name of the provider (for path extraction and errors)
 * @returns Effect that resolves to ProxyResult with response and parsed body
 *
 * @example
 * ```ts
 * const result = yield* proxyToProvider(request, {
 *   ...PROVIDER_CONFIGS.openai,
 *   apiKey: process.env.OPENAI_API_KEY!,
 * }, "openai");
 * ```
 */
export function proxyToProvider(
  request: Request,
  config: ProxyConfig & { apiKey: string },
  providerName: ProviderName,
): Effect.Effect<ProxyResult, ProxyError> {
  return Effect.gen(function* () {
    // Validate API key is configured
    if (!config.apiKey) {
      return yield* Effect.fail(
        new ProxyError({
          message: `${providerName} API key not configured`,
        }),
      );
    }

    // Extract the path to forward
    const url = new URL(request.url);
    const path = extractProviderPath(url.pathname, providerName);
    const targetUrl = `${config.baseUrl}/${path}${url.search}`;

    // Copy request headers, excluding user auth and host
    const headers = new Headers(
      Array.from(request.headers.entries()).filter(
        ([key]) => !["authorization", "host"].includes(key.toLowerCase()),
      ),
    );

    // Set provider authentication
    headers.set(config.authHeader, config.authFormat(config.apiKey));

    // Forward the request to the provider
    const response = yield* Effect.tryPromise({
      try: () =>
        fetch(targetUrl.toString(), {
          method: request.method,
          headers,
          body: request.body,
          // @ts-expect-error - duplex is needed for streaming but not in types
          duplex: "half",
        }),
      catch: (error) =>
        new ProxyError({
          message: `Failed to proxy request to ${providerName}: ${
            error instanceof Error
              ? error.message
              : /* v8 ignore next */ String(error)
          }`,
          cause: error,
        }),
    });

    // Check if response is streaming
    const contentType = response.headers.get("content-type") || "";
    const isSSE = contentType.includes("text/event-stream");
    const isNDJSON = contentType.includes("application/x-ndjson");
    const isStreaming = isSSE || isNDJSON;

    // Parse streaming responses to extract usage
    if (isStreaming) {
      const format = isSSE ? "sse" : /* v8 ignore next */ "ndjson";
      const streamResult = yield* parseStreamingResponse(
        response,
        format,
        providerName,
      );
      return {
        response: streamResult.response,
        body: null, // Body will be available via usageStream
        usageStream: streamResult.usageStream,
      };
    }

    // For non-streaming responses, parse the body normally
    const responseClone = response.clone();
    const bodyResult = yield* Effect.tryPromise({
      try: () => responseClone.text(),
      catch: (error) =>
        new ProxyError({
          message: `Failed to read response body: ${
            error instanceof Error
              ? error.message
              : /* v8 ignore next */ String(error)
          }`,
          cause: error,
        }),
    }).pipe(Effect.catchAll(() => Effect.succeed(null as string | null)));

    let parsedBody: unknown = null;

    if (bodyResult) {
      try {
        parsedBody = JSON.parse(bodyResult);
      } catch {
        // Not JSON, that's ok
      }
    }

    return {
      response,
      body: parsedBody,
    };
  });
}
