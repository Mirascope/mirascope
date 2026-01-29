/**
 * @fileoverview Utilities for parsing and extracting usage from streaming responses using Effect Streams.
 *
 * Handles Server-Sent Events (SSE) and NDJSON streaming formats from AI providers,
 * extracting usage information and performing metering using pure Effect Stream composition.
 */

import { Effect, Stream, pipe, Ref } from "effect";

import type { TokenUsage } from "@/api/router/pricing";
import type { ProxyResult } from "@/api/router/proxy";

import { getCostCalculator, type ProviderName } from "@/api/router/providers";
import {
  type RouterRequestIdentifiers,
  type RouterRequestContext,
  type ValidatedRouterRequest,
  enqueueRouterMetering,
} from "@/api/router/utils";
import { ProxyError } from "@/errors";
import { RouterMeteringQueueService } from "@/workers/routerMeteringQueue";

/**
 * Result of parsing a streaming response.
 */
export interface StreamParseResult {
  /** Effect that yields a Response with ReadableStream for the client */
  responseEffect: Effect.Effect<
    Response,
    ProxyError,
    RouterMeteringQueueService
  >;
}

/**
 * Original response metadata to preserve in the final response.
 */
export interface ResponseMetadata {
  /** Original response status */
  status: number;
  /** Original response statusText */
  statusText: string;
  /** Original response headers */
  headers: Headers;
}

/**
 * Metering context for streaming responses.
 *
 * Provides the necessary information to perform metering when usage data is extracted.
 */
export interface StreamMeteringContext {
  /** Provider name (e.g., "openai", "anthropic", "google") */
  provider: ProviderName;
  /** Model ID for cost calculation */
  modelId: string;
  /** Reservation ID for fund settlement */
  reservationId: string;
  /** Router request identifiers for database operations */
  request: RouterRequestIdentifiers;
  /** Original response metadata */
  response: ResponseMetadata;
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
 * Processes remaining buffer content at end of stream.
 *
 * @param buffer - The remaining buffer content
 * @param format - The streaming format (sse or ndjson)
 * @param costCalculator - The cost calculator for the provider
 * @returns TokenUsage if found, null otherwise
 */
function processRemainingBuffer(
  buffer: string,
  format: "sse" | "ndjson",
  costCalculator: ReturnType<typeof getCostCalculator>,
): TokenUsage | null {
  if (!buffer.trim()) {
    return null;
  }

  const parsed =
    format === "sse" ? parseSSELine(buffer) : parseNDJSONLine(buffer);
  if (!parsed) {
    return null;
  }

  return costCalculator.extractUsageFromStreamChunk(parsed);
}

/**
 * Settles metering for a streaming response after stream completes.
 *
 * Calculates cost from usage data and enqueues to the router metering queue
 * for asynchronous processing.
 *
 * **Note**: This runs in Stream.ensuring, which executes after the stream completes.
 * The queue service must be provided in the outer scope.
 *
 * @param usage - Final usage data extracted from stream, or null if none found
 * @param meteringContext - Context with all necessary IDs and config
 * @returns Effect that completes when metering is enqueued (always succeeds)
 */
export function settleMeteringForStream(
  usage: TokenUsage | null,
  meteringContext: StreamMeteringContext,
): Effect.Effect<void, never, RouterMeteringQueueService> {
  return Effect.gen(function* () {
    if (!usage) {
      console.warn(
        `[settleMeteringForStream] No usage data from stream for request ${meteringContext.request.routerRequestId}`,
      );
      return;
    }

    // Calculate cost
    const costCalculator = getCostCalculator(meteringContext.provider);
    const costResult = yield* costCalculator.calculate(
      meteringContext.modelId,
      usage,
    );

    if (!costResult || costResult.totalCost <= 0) {
      console.warn(
        `[settleMeteringForStream] Cost calculation failed for request ${meteringContext.request.routerRequestId}`,
      );
      return;
    }

    // Enqueue metering for async processing
    yield* enqueueRouterMetering(
      meteringContext.request.routerRequestId,
      meteringContext.reservationId,
      meteringContext.request,
      usage,
      Number(costResult.totalCost),
    );
  }).pipe(
    Effect.catchAll((error) => {
      console.error(
        `[settleMeteringForStream] Failed to enqueue metering for request ${meteringContext.request.routerRequestId}:`,
        error,
      );
      // Log error but don't fail - queue has retry + DLQ
      return Effect.void;
    }),
  );
}

/**
 * Parses a streaming response using Effect Streams.
 *
 * This function:
 * 1. Wraps the response body in an Effect Stream
 * 2. Uses Stream.tap to parse chunks as side effect while preserving original bytes
 * 3. Extracts usage data from chunks
 * 4. Performs metering when stream completes using Stream.ensuring
 * 5. Converts back to a native ReadableStream for the client
 *
 * The Effect Stream pipeline properly handles async work in the ensuring finalizer,
 * waiting for queue enqueueing to complete before finishing the stream.
 *
 * @param response - The streaming response from the provider
 * @param format - The streaming format ("sse" or "ndjson")
 * @param meteringContext - Context for automatic cost calculation and fund settlement
 * @returns Effect that resolves to StreamParseResult
 */
export function parseStreamingResponse(
  response: Response,
  format: "sse" | "ndjson",
  meteringContext: StreamMeteringContext,
): Effect.Effect<StreamParseResult, ProxyError, RouterMeteringQueueService> {
  return Effect.gen(function* () {
    const originalBody = response.body;
    if (!originalBody) {
      // No body, return response as-is
      return {
        responseEffect: Effect.succeed(response),
      };
    }

    const costCalculator = getCostCalculator(meteringContext.provider);

    // Create Refs to track parsing state
    const usageRef: Ref.Ref<TokenUsage | null> =
      yield* Ref.make<TokenUsage | null>(null);
    const bufferRef: Ref.Ref<string> = yield* Ref.make<string>("");

    // Build the Effect Stream pipeline
    const effectStream = pipe(
      // 1. Wrap the native ReadableStream in an Effect Stream
      Stream.fromReadableStream(
        () => originalBody,
        (error) =>
          new ProxyError({
            message: "Failed to read stream",
            cause: error,
          }),
      ),

      // 2. Parse chunks as side effect while preserving original bytes
      Stream.tap((chunk: Uint8Array) =>
        Effect.gen(function* () {
          // Decode chunk to text
          const text = new TextDecoder().decode(chunk);

          // Get current buffer
          let buffer = yield* Ref.get(bufferRef);
          buffer += text;

          // Process complete lines
          const lines = buffer.split("\n");
          buffer = lines.pop() || ""; // Keep incomplete line in buffer

          // Update buffer
          yield* Ref.set(bufferRef, buffer);

          // Parse each complete line
          for (const line of lines) {
            const parsed =
              format === "sse" ? parseSSELine(line) : parseNDJSONLine(line);
            if (parsed) {
              const usage = costCalculator.extractUsageFromStreamChunk(parsed);
              if (usage) {
                // Always keep the last usage chunk. Provider semantics:
                // - OpenAI: sends usage only once at the end
                // - Anthropic: sends accumulating usage chunks throughout the stream
                // - Google: sends accumulating usage chunks throughout the stream
                // Since Anthropic and Google provide accumulating totals, we can
                // always use the last chunk for final metering.
                yield* Ref.set(usageRef, usage);
              }
            }
          }
        }),
      ),

      // 3. Perform metering when stream ends (finalization)
      Stream.ensuring(
        Effect.gen(function* () {
          // Process any remaining buffer
          const remainingBuffer = yield* Ref.get(bufferRef);
          const bufferUsage = processRemainingBuffer(
            remainingBuffer,
            format,
            costCalculator,
          );
          if (bufferUsage) {
            yield* Ref.set(usageRef, bufferUsage);
          }

          // Get final usage and perform metering
          const finalUsage = yield* Ref.get(usageRef);
          yield* settleMeteringForStream(finalUsage, meteringContext);
        }),
      ),
    );

    // Convert Effect Stream back to ReadableStream (preserves original Uint8Array chunks)
    const readableStreamEffect = Stream.toReadableStreamEffect(effectStream);

    return {
      responseEffect: readableStreamEffect.pipe(
        Effect.map(
          (readableStream) =>
            new Response(readableStream, {
              status: meteringContext.response.status,
              statusText: meteringContext.response.statusText,
              headers: meteringContext.response.headers,
            }),
        ),
      ),
    };
  });
}

/**
 * Handles a streaming response.
 *
 * Parses the streaming response with Effect Streams, performing metering
 * in the stream finalizer.
 *
 * @param proxyResult - Result from proxying to provider
 * @param context - Router request context
 * @param validated - Validated request information
 * @param responseMetadata - Original response metadata
 * @returns Final response for the client
 */
export function handleStreamingResponse(
  proxyResult: ProxyResult,
  context: RouterRequestContext,
  validated: ValidatedRouterRequest,
  responseMetadata: ResponseMetadata,
): Effect.Effect<Response, ProxyError, RouterMeteringQueueService> {
  return Effect.gen(function* () {
    const meteringContext: StreamMeteringContext = {
      provider: validated.provider,
      modelId: validated.modelId,
      reservationId: context.reservationId,
      request: context.request,
      response: responseMetadata,
    };

    const streamParseResult = yield* parseStreamingResponse(
      proxyResult.response,
      proxyResult.streamFormat!,
      meteringContext,
    );

    const finalResponse = yield* streamParseResult.responseEffect;
    return finalResponse;
  });
}
