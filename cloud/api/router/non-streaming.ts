/**
 * @fileoverview Handler for non-streaming router responses.
 *
 * Processes non-streaming responses from AI providers, extracting usage
 * information and performing metering asynchronously via queue.
 */

import { Effect } from "effect";

import type { ProxyResult } from "@/api/router/proxy";

import { getCostCalculator } from "@/api/router/providers";
import {
  type RouterRequestContext,
  type ValidatedRouterRequest,
  enqueueRouterMetering,
} from "@/api/router/utils";
import { RouterMeteringQueueService } from "@/workers/routerMeteringQueue";

/**
 * Handles a non-streaming response.
 *
 * Extracts usage from response body, calculates cost, and enqueues
 * metering data for asynchronous processing.
 *
 * @param proxyResult - Result from proxying to provider
 * @param context - Router request context
 * @param validated - Validated request information
 * @returns Final response for the client
 */
export function handleNonStreamingResponse(
  proxyResult: ProxyResult,
  context: RouterRequestContext,
  validated: ValidatedRouterRequest,
): Effect.Effect<Response, Error, RouterMeteringQueueService> {
  return Effect.gen(function* () {
    const costCalculator = getCostCalculator(validated.provider);

    // Extract usage from response body
    const usage = proxyResult.body
      ? costCalculator.extractUsage(proxyResult.body)
      : null;

    const costResult = usage
      ? yield* costCalculator.calculate(
          validated.modelId,
          usage,
          context.modelPricing,
        )
      : null;

    if (usage && costResult && costResult.totalCost > 0) {
      // Enqueue metering for async processing
      yield* enqueueRouterMetering(
        context.routerRequestId,
        context.reservationId,
        context.request,
        usage,
        Number(costResult.tokenCost),
        /* v8 ignore next 1 - toolCost always defined in tests */
        costResult.toolCost ? Number(costResult.toolCost) : undefined,
      ).pipe(
        Effect.catchAll((error) => {
          console.error(
            `[handleNonStreamingResponse] Failed to enqueue metering for request ${context.routerRequestId}:`,
            error,
          );
          // Log error but don't fail the response - queue has retry + DLQ
          return Effect.void;
        }),
      );
    } else if (!usage) {
      console.warn(
        `[handleNonStreamingResponse] No usage data for request ${context.routerRequestId}`,
      );
    } else {
      console.warn(
        `[handleNonStreamingResponse] Zero cost calculated for request ${context.routerRequestId}`,
      );
    }

    return proxyResult.response;
  });
}
