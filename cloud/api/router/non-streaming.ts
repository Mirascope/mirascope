/**
 * @fileoverview Handler for non-streaming router responses.
 *
 * Processes non-streaming responses from AI providers, extracting usage
 * information and performing metering.
 */

import { Effect } from "effect";
import { Database } from "@/db";
import { Payments } from "@/payments";
import { DatabaseError, NotFoundError, PermissionDeniedError } from "@/errors";
import { getCostCalculator } from "@/api/router/providers";
import type { ProxyResult } from "@/api/router/proxy";
import {
  type RouterRequestContext,
  type ValidatedRouterRequest,
  handleRouterRequestFailure,
} from "@/api/router/utils";

/**
 * Handles a non-streaming response.
 *
 * Extracts usage from response body, calculates cost, updates database,
 * and settles fund reservation.
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
): Effect.Effect<
  Response,
  DatabaseError | NotFoundError | PermissionDeniedError,
  Database | Payments
> {
  return Effect.gen(function* () {
    const db = yield* Database;
    const payments = yield* Payments;

    const costCalculator = getCostCalculator(validated.provider);

    // Extract usage from response body
    const usage = proxyResult.body
      ? costCalculator.extractUsage(proxyResult.body)
      : null;

    const costResult = usage
      ? yield* costCalculator.calculate(validated.modelId, usage)
      : null;

    if (costResult && costResult.totalCost > 0) {
      // Update router request and settle reservation (errors swallowed, cron will reconcile)
      yield* Effect.gen(function* () {
        yield* db.organizations.projects.environments.apiKeys.routerRequests.update(
          {
            userId: context.request.userId,
            organizationId: context.request.organizationId,
            projectId: context.request.projectId,
            environmentId: context.request.environmentId,
            apiKeyId: context.request.apiKeyId,
            routerRequestId: context.routerRequestId,
            data: {
              inputTokens: usage!.inputTokens
                ? BigInt(usage!.inputTokens)
                : null,
              outputTokens: usage!.outputTokens
                ? BigInt(usage!.outputTokens)
                : null,
              cacheReadTokens: usage!.cacheReadTokens
                ? BigInt(usage!.cacheReadTokens)
                : null,
              cacheWriteTokens: usage!.cacheWriteTokens
                ? BigInt(usage!.cacheWriteTokens)
                : null,
              cacheWriteBreakdown: usage!.cacheWriteBreakdown || null,
              costCenticents: costResult.totalCost,
              status: "success",
              completedAt: new Date(),
            },
          },
        );

        // Settle reservation - this updates DB and charges the meter
        yield* payments.products.router.settleFunds(
          context.reservationId,
          costResult.totalCost,
        );
      }).pipe(
        Effect.catchAll((error) => {
          console.error(
            `[handleNonStreamingResponse] Error updating request ${context.routerRequestId} or settling reservation ${context.reservationId}:`,
            error,
          );
          return Effect.succeed(undefined);
        }),
      );
    } else {
      // No usage or cost calculation failed, update request and release funds
      yield* handleRouterRequestFailure(
        context.routerRequestId,
        context.reservationId,
        context.request,
        "No usage data or cost calculation failed",
      );
    }

    return proxyResult.response;
  });
}
