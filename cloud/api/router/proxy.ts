/**
 * @fileoverview Proxy utility for forwarding requests to AI provider APIs.
 *
 * Provides utilities for proxying HTTP requests to external AI providers
 * (OpenAI, Anthropic, Google AI) while swapping authentication from user's
 * Mirascope API key to internal provider keys.
 */

import { Effect } from "effect";
import { ProxyError } from "@/errors";
import type { ProxyConfig, ProviderName } from "@/api/router/providers";

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
 * Parses response body as JSON.
 *
 * Reads the response body and attempts to parse it as JSON.
 * Returns null if body cannot be read or parsed.
 *
 * @param response - The response to parse (will be cloned)
 * @returns Effect that resolves to parsed JSON or null
 */
function parseResponseBody(
  response: Response,
): Effect.Effect<unknown, ProxyError> {
  return Effect.gen(function* () {
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

    if (!bodyResult) {
      return null;
    }

    try {
      return JSON.parse(bodyResult) as unknown;
    } catch {
      // Not JSON, that's ok
      return null;
    }
  });
}

/**
 * Result of proxying a request to a provider.
 */
export interface ProxyResult {
  /** The provider's response (may be streaming or non-streaming) */
  response: Response;
  /**
   * Parsed JSON body if available (non-streaming only), null otherwise.
   */
  body: unknown;
  /** Whether the response is streaming (SSE or NDJSON) */
  isStreaming: boolean;
  /** The streaming format if isStreaming is true */
  streamFormat?: "sse" | "ndjson";
}

/**
 * Proxies an HTTP request to an AI provider.
 *
 * This function:
 * 1. Extracts the path to forward
 * 2. Copies request headers (excluding user auth and host)
 * 3. Sets provider authentication
 * 4. Forwards the request to the provider
 * 5. For non-streaming: Clones and parses the response body
 * 6. Returns the response with metadata
 *
 * @param request - The incoming HTTP request
 * @param config - Provider configuration including API key
 * @param providerName - Name of the provider (for path extraction and errors)
 * @returns Effect that resolves to ProxyResult with response and metadata
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

    // For streaming responses, return immediately (caller handles metering)
    if (isStreaming) {
      return {
        response,
        body: null,
        isStreaming: true,
        streamFormat: isSSE ? "sse" : "ndjson",
      };
    }

    // For non-streaming responses, parse the body
    const parsedBody = yield* parseResponseBody(response);

    return {
      response,
      body: parsedBody,
      isStreaming: false,
    };
  });
}
