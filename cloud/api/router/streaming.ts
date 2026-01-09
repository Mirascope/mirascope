/**
 * @fileoverview Utilities for parsing and extracting usage from streaming responses using Effect Streams.
 *
 * Handles Server-Sent Events (SSE) and NDJSON streaming formats from AI providers,
 * extracting usage information and performing metering using pure Effect Stream composition.
 */

import { Effect, Stream, pipe, Ref } from "effect";
import { ProxyError } from "@/errors";
import { getCostCalculator, type ProviderName } from "@/api/router/providers";
import type { TokenUsage } from "@/api/router/pricing";
import { Database } from "@/db";
import { Payments } from "@/payments";
import type { ProxyResult } from "@/api/router/proxy";
import {
  type RouterRequestIdentifiers,
  type RouterRequestContext,
  type ValidatedRouterRequest,
  handleRouterRequestFailure,
} from "@/api/router/utils";

/**
 * Result of parsing a streaming response.
 */
export interface StreamParseResult {
  /** Effect that yields a Response with ReadableStream for the client */
  responseEffect: Effect.Effect<Response, ProxyError>;
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
 *
 * **Important**: The databaseUrl and stripe config are required because the Stream.ensuring
 * finalizer runs after the outer Effect scope has completed and disposed its services.
 * We need to create a fresh Database.Live layer with independent service lifecycle to
 * perform metering operations after the stream has been fully consumed by the client.
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
  /** Database connection string for creating fresh DB connection in ensuring */
  databaseUrl: string;
  /** Stripe API key for payments */
  stripeApiKey: string;
  /** Stripe router price ID */
  routerPriceId: string;
  /** Stripe router meter ID */
  routerMeterId: string;
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
 * Core metering logic for streaming responses.
 *
 * **Exported for testing**: This function is exported to allow unit tests to verify
 * the metering logic with mocked Database and Payments layers.
 *
 * @param usage - Final usage data extracted from stream, or null if none found
 * @param meteringContext - Context with all necessary IDs and config
 * @returns Effect that performs metering operations (requires Database and Payments services)
 */
export function performStreamMetering(
  usage: TokenUsage | null,
  meteringContext: StreamMeteringContext,
): Effect.Effect<void, never, Database | Payments> {
  return Effect.gen(function* () {
    const db = yield* Database;
    const payments = yield* Payments;
    const costCalculator = getCostCalculator(meteringContext.provider);

    if (!usage) {
      yield* handleRouterRequestFailure(
        meteringContext.request.routerRequestId,
        meteringContext.reservationId,
        meteringContext.request,
        "No usage data from stream",
      );
      return;
    }

    // Calculate cost
    const costResult = yield* costCalculator.calculate(
      meteringContext.modelId,
      usage,
    );

    if (!costResult || costResult.totalCost <= 0) {
      yield* handleRouterRequestFailure(
        meteringContext.request.routerRequestId,
        meteringContext.reservationId,
        meteringContext.request,
        "Cost calculation failed",
      );
      return;
    }

    // Update router request with usage and cost
    yield* db.organizations.projects.environments.apiKeys.routerRequests.update(
      {
        userId: meteringContext.request.userId,
        organizationId: meteringContext.request.organizationId,
        projectId: meteringContext.request.projectId,
        environmentId: meteringContext.request.environmentId,
        apiKeyId: meteringContext.request.apiKeyId,
        routerRequestId: meteringContext.request.routerRequestId,
        data: {
          inputTokens: usage.inputTokens ? BigInt(usage.inputTokens) : null,
          outputTokens: usage.outputTokens ? BigInt(usage.outputTokens) : null,
          cacheReadTokens: usage.cacheReadTokens
            ? BigInt(usage.cacheReadTokens)
            : null,
          cacheWriteTokens: usage.cacheWriteTokens
            ? BigInt(usage.cacheWriteTokens)
            : null,
          cacheWriteBreakdown: usage.cacheWriteBreakdown || null,
          costCenticents: costResult.totalCost,
          status: "success",
          completedAt: new Date(),
        },
      },
    );

    // Settle funds (releases reservation and charges meter)
    yield* payments.products.router.settleFunds(
      meteringContext.reservationId,
      costResult.totalCost,
    );
  }).pipe(
    Effect.catchAll((error) => {
      console.error(
        `[performStreamMetering] Error updating request ${meteringContext.request.routerRequestId} or settling reservation ${meteringContext.reservationId}:`,
        error,
      );
      return Effect.succeed(undefined);
    }),
  );
}

/**
 * Settles metering for a streaming response after stream completes.
 *
 * This function:
 * 1. Calculates cost from usage data
 * 2. Updates router request in database with usage and cost
 * 3. Settles fund reservation and charges the meter
 * 4. Handles failure cases by releasing funds
 *
 * **Note**: This runs in Stream.ensuring, which executes after the stream completes.
 * It creates a fresh Database.Live layer because the outer Effect scope has already
 * disposed its services by the time the stream finishes.
 *
 * @param usage - Final usage data extracted from stream, or null if none found
 * @param meteringContext - Context with all necessary IDs and config
 * @returns Effect that completes when metering is finished (always succeeds)
 */
export function settleMeteringForStream(
  usage: TokenUsage | null,
  meteringContext: StreamMeteringContext,
): Effect.Effect<void, never> {
  return performStreamMetering(usage, meteringContext).pipe(
    // Provide fresh Database and Payments services with their own connection pool
    Effect.provide(
      Database.Live({
        database: { connectionString: meteringContext.databaseUrl },
        payments: {
          apiKey: meteringContext.stripeApiKey,
          routerPriceId: meteringContext.routerPriceId,
          routerMeterId: meteringContext.routerMeterId,
        },
      }),
    ),
    // Catch any errors from layer construction to ensure infallible Effect
    Effect.catchAll((error) => {
      console.error(
        "[Stream.ensuring] Failed to create Database layer for metering:",
        error,
      );
      return Effect.succeed(undefined);
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
 * waiting for DB updates and Stripe metering to complete before finishing the stream.
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
): Effect.Effect<StreamParseResult, ProxyError> {
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

    // Wrap in Response
    const responseEffect = pipe(
      readableStreamEffect,
      Effect.map(
        (readableStream) =>
          new Response(readableStream, {
            status: meteringContext.response.status,
            statusText: meteringContext.response.statusText,
            headers: meteringContext.response.headers,
          }),
      ),
    );

    return {
      responseEffect,
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
 * @param databaseUrl - Database URL for metering
 * @param stripeConfig - Stripe configuration for metering
 * @returns Final response for the client
 */
export function handleStreamingResponse(
  proxyResult: ProxyResult,
  context: RouterRequestContext,
  validated: ValidatedRouterRequest,
  responseMetadata: ResponseMetadata,
  databaseUrl: string,
  stripeConfig: {
    apiKey: string;
    routerPriceId: string;
    routerMeterId: string;
  },
): Effect.Effect<Response, ProxyError> {
  return Effect.gen(function* () {
    const meteringContext: StreamMeteringContext = {
      provider: validated.provider,
      modelId: validated.modelId,
      reservationId: context.reservationId,
      request: context.request,
      response: responseMetadata,
      databaseUrl,
      stripeApiKey: stripeConfig.apiKey,
      routerPriceId: stripeConfig.routerPriceId,
      routerMeterId: stripeConfig.routerMeterId,
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
