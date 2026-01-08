/**
 * @fileoverview Utilities for parsing and extracting usage from streaming responses.
 *
 * Handles Server-Sent Events (SSE) and NDJSON streaming formats from AI providers,
 * extracting usage information while allowing the stream to pass through to the client.
 */

import { Effect, Stream, pipe, Option } from "effect";
import { ProxyError } from "@/errors";
import { getCostCalculator, type ProviderName } from "@/api/router/providers";
import type { TokenUsage } from "@/api/router/pricing";

/**
 * Result of parsing a streaming response.
 */
export interface StreamParseResult {
  /** The original response with a fresh stream for the client */
  response: Response;
  /** Stream of usage data extracted from chunks */
  usageStream: Stream.Stream<TokenUsage, ProxyError>;
}

/**
 * Parses a single Server-Sent Event (SSE) line.
 *
 * SSE format: `data: {...}\n\n`
 *
 * @param line - A single line from the SSE stream
 * @returns Parsed JSON object or null if not parseable
 */
function parseSSELine(line: string): unknown {
  // SSE lines start with "data: "
  if (!line.startsWith("data: ")) {
    return null;
  }

  const data = line.slice(6); // Remove "data: " prefix

  // OpenAI sends "[DONE]" as the final message
  if (data === "[DONE]") {
    return null;
  }

  try {
    return JSON.parse(data);
  } catch {
    return null;
  }
}

/**
 * Parses an NDJSON line.
 *
 * @param line - A single line from the NDJSON stream
 * @returns Parsed JSON object or null if not parseable
 */
function parseNDJSONLine(line: string): unknown {
  try {
    return JSON.parse(line);
  } catch {
    return null;
  }
}

/**
 * Parses a streaming response to extract usage data.
 *
 * This function:
 * 1. Tees the response stream to two consumers
 * 2. One stream goes to the client (returned as Response)
 * 3. The other stream is analyzed to extract usage information via Effect Streams
 * 4. Returns both the client response and a usage stream
 *
 * The original response stream is preserved for the client in real-time.
 * Usage extraction happens via functional stream transformations.
 *
 * @param response - The streaming response from the provider
 * @param format - The streaming format ("sse" or "ndjson")
 * @param provider - The provider name for usage extraction
 * @returns Effect that resolves to StreamParseResult with response and usage stream
 */
export function parseStreamingResponse(
  response: Response,
  format: "sse" | "ndjson",
  provider: ProviderName,
): Effect.Effect<StreamParseResult, ProxyError> {
  return Effect.succeed(
    (() => {
      const originalBody = response.body;
      if (!originalBody) {
        return {
          response,
          usageStream: Stream.empty,
        };
      }

      const costCalculator = getCostCalculator(provider);

      // Tee the stream to allow two consumers
      const [clientReadable, analysisReadable] = originalBody.tee();

      // Transform analysis stream: bytes -> lines -> parsed -> usage
      const usageStream = pipe(
        Stream.fromReadableStream(
          () => analysisReadable,
          /* v8 ignore next 4 */
          (error) =>
            new ProxyError({
              message: "Failed to read stream",
              cause: error,
            }),
        ),
        Stream.decodeText(),
        Stream.splitLines,
        Stream.map((line) =>
          format === "sse" ? parseSSELine(line) : parseNDJSONLine(line),
        ),
        Stream.filterMap((parsed) =>
          parsed
            ? Option.fromNullable(
                costCalculator.extractUsageFromStreamChunk(parsed),
              )
            : Option.none(),
        ),
      );

      // Create response with client stream
      const clientResponse = new Response(clientReadable, {
        status: response.status,
        statusText: response.statusText,
        headers: response.headers,
      });

      return {
        response: clientResponse,
        usageStream,
      };
    })(),
  );
}
