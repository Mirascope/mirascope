/**
 * @fileoverview Helper functions for router request handling.
 *
 * Provides reusable utilities for processing router requests including
 * authentication, validation, fund reservation, and response handling.
 */

import { Effect } from "effect";
import type { PublicUser, ApiKeyInfo } from "@/db/schema";
import { authenticate } from "@/auth";
import { Database } from "@/db";
import { Payments } from "@/payments";
import {
  InternalError,
  UnauthorizedError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
  ProxyError,
} from "@/errors";
import {
  isValidProvider,
  extractModelId,
  getCostCalculator,
  type ProviderName,
} from "@/api/router/providers";
import { estimateCost } from "@/api/router/cost-estimator";
import type { ProxyResult } from "@/api/router/proxy";
import {
  parseStreamingResponse,
  type StreamMeteringContext,
  type RouterRequestIdentifiers,
  type ResponseMetadata,
} from "@/api/router/streaming";

/**
 * Result of router request validation.
 */
export interface ValidatedRouterRequest {
  user: PublicUser;
  apiKeyInfo: ApiKeyInfo;
  provider: ProviderName;
  modelId: string;
  parsedRequestBody: unknown;
}

/**
 * Context for router request processing.
 */
export interface RouterRequestContext {
  routerRequestId: string;
  reservationId: string;
  request: RouterRequestIdentifiers;
}

/**
 * Validates and authenticates a router request.
 *
 * This function:
 * 1. Validates the provider is supported
 * 2. Authenticates the user via Mirascope API key
 * 3. Parses the request body
 * 4. Extracts the model ID
 *
 * @param request - The incoming HTTP request
 * @param provider - The provider name from URL params
 * @returns Validated request information
 * @throws InternalError if provider is unsupported or model ID extraction fails
 * @throws UnauthorizedError if API key is missing or invalid
 */
export function validateRouterRequest(
  request: Request,
  provider: string,
): Effect.Effect<
  ValidatedRouterRequest,
  InternalError | UnauthorizedError,
  Database
> {
  return Effect.gen(function* () {
    // Validate provider
    if (!isValidProvider(provider)) {
      return yield* new InternalError({
        message: `Unsupported provider: ${provider}`,
      });
    }

    // Authenticate user via Mirascope API key
    const { user, apiKeyInfo } = yield* authenticate(request);

    if (!apiKeyInfo) {
      return yield* new UnauthorizedError({
        message: "API key required for router access",
      });
    }

    // Parse request body
    const requestBodyText = yield* Effect.tryPromise({
      try: () => request.clone().text(),
      catch: (error) =>
        new InternalError({
          message: `Failed to read request body: ${error instanceof Error ? error.message : /* v8 ignore next 1 */ String(error)}`,
        }),
    }).pipe(Effect.catchAll(() => Effect.succeed(null as string | null)));

    let parsedRequestBody: unknown = null;
    if (requestBodyText) {
      try {
        parsedRequestBody = JSON.parse(requestBodyText);
      } catch {
        // Not JSON - will fail in model extraction
      }
    }

    // Extract model ID based on provider
    const modelId = extractModelId(provider, request, parsedRequestBody);

    if (!modelId) {
      return yield* new InternalError({
        message: `Failed to extract model ID from ${provider} request`,
      });
    }

    // Note: If modelId extraction succeeded, parsedRequestBody must be valid
    // (extractModelId requires parsedRequestBody to extract the model field)

    return {
      provider,
      user,
      apiKeyInfo,
      modelId,
      parsedRequestBody,
    };
  });
}

/**
 * Creates a pending router request in the database.
 *
 * @param validated - Validated request information
 * @returns Router request ID
 */
export function createPendingRouterRequest(
  validated: ValidatedRouterRequest,
): Effect.Effect<
  string,
  DatabaseError | NotFoundError | PermissionDeniedError,
  Database
> {
  return Effect.gen(function* () {
    const db = yield* Database;

    const routerRequest =
      yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
        {
          userId: validated.user.id,
          organizationId: validated.apiKeyInfo.organizationId,
          projectId: validated.apiKeyInfo.projectId,
          environmentId: validated.apiKeyInfo.environmentId,
          apiKeyId: validated.apiKeyInfo.apiKeyId,
          data: {
            provider: validated.provider,
            model: validated.modelId,
            status: "pending",
          },
        },
      );

    return routerRequest.id;
  });
}

/**
 * Reserves funds for a router request.
 *
 * @param validated - Validated request information
 * @param routerRequestId - Router request ID
 * @param stripeCustomerId - Stripe customer ID for the organization
 * @returns Reservation ID
 */
export function reserveRouterFunds(
  validated: ValidatedRouterRequest,
  routerRequestId: string,
  stripeCustomerId: string,
): Effect.Effect<string, Error, Payments> {
  return Effect.gen(function* () {
    const payments = yield* Payments;

    // Estimate cost
    const estimate = yield* estimateCost({
      provider: validated.provider,
      modelId: validated.modelId,
      requestBody: validated.parsedRequestBody,
    });

    // Reserve funds
    const reservationId = yield* payments.products.router.reserveFunds({
      stripeCustomerId,
      estimatedCostCenticents: estimate.cost,
      routerRequestId,
    });

    return reservationId;
  });
}

/**
 * Handles failure by updating router request and releasing funds.
 *
 * This is a common error handling pattern used throughout the router.
 *
 * @param routerRequestId - Router request ID
 * @param reservationId - Reservation ID
 * @param request - Request identifiers
 * @param errorMessage - Error message to store
 */
export function handleRouterRequestFailure(
  routerRequestId: string,
  reservationId: string,
  request: RouterRequestIdentifiers,
  errorMessage: string,
): Effect.Effect<void, never, Database | Payments> {
  return Effect.gen(function* () {
    const db = yield* Database;
    const payments = yield* Payments;

    yield* db.organizations.projects.environments.apiKeys.routerRequests
      .update({
        userId: request.userId,
        organizationId: request.organizationId,
        projectId: request.projectId,
        environmentId: request.environmentId,
        apiKeyId: request.apiKeyId,
        routerRequestId,
        data: {
          status: "failure",
          errorMessage,
          completedAt: new Date(),
        },
      })
      .pipe(
        Effect.catchAll((updateError) => {
          console.error(
            `Failed to update router request ${routerRequestId} after error:`,
            updateError,
          );
          return Effect.succeed(undefined);
        }),
      );

    yield* payments.products.router.releaseFunds(reservationId).pipe(
      Effect.catchAll((releaseError) => {
        console.error(
          `Failed to release reservation ${reservationId} after error:`,
          releaseError,
        );
        return Effect.succeed(undefined);
      }),
    );
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
      // Update router request with usage and cost
      yield* db.organizations.projects.environments.apiKeys.routerRequests.update(
        {
          userId: context.request.userId,
          organizationId: context.request.organizationId,
          projectId: context.request.projectId,
          environmentId: context.request.environmentId,
          apiKeyId: context.request.apiKeyId,
          routerRequestId: context.routerRequestId,
          data: {
            inputTokens: usage!.inputTokens ? BigInt(usage!.inputTokens) : null,
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
      yield* payments.products.router
        .settleFunds(context.reservationId, costResult.totalCost)
        .pipe(
          Effect.catchAll((error) => {
            console.error(
              `Failed to settle reservation ${context.reservationId} (cost: ${costResult.totalCost} centicents):`,
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
