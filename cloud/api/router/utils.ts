/**
 * @fileoverview Shared utilities for router request handling.
 *
 * Provides reusable utilities for processing router requests including
 * authentication, validation, fund reservation, and failure handling.
 */

import { Effect } from "effect";

import type { TokenUsage, ModelPricing } from "@/api/router/pricing";
import type { PublicUser, EnvironmentApiKeyAuth } from "@/db/schema";

import { estimateCost } from "@/api/router/cost-estimator";
import {
  isValidProvider,
  extractModelId,
  type ProviderName,
} from "@/api/router/providers";
import { authenticate } from "@/auth";
import { Database } from "@/db/database";
import {
  InternalError,
  UnauthorizedError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/errors";
import { Payments } from "@/payments";
import {
  RouterMeteringQueueService,
  type RouterMeteringMessage,
} from "@/workers/routerMeteringQueue";

// =============================================================================
// Types
// =============================================================================

/**
 * Router request identifiers for database operations.
 */
export interface RouterRequestIdentifiers {
  userId: string;
  organizationId: string;
  projectId: string;
  environmentId: string;
  apiKeyId: string;
  routerRequestId: string;
  /** Populated when the request is made via a claw's bot-user API key. */
  clawId: string | null;
}

/**
 * Result of router request validation.
 */
export interface ValidatedRouterRequest {
  user: PublicUser;
  apiKeyInfo: EnvironmentApiKeyAuth;
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
  /** Cached pricing from estimation phase for use in cost calculation */
  modelPricing: ModelPricing;
}

// =============================================================================
// Validation Functions
// =============================================================================

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

// =============================================================================
// Database Functions
// =============================================================================

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

// =============================================================================
// Payment Functions
// =============================================================================

/**
 * Result of fund reservation.
 */
export interface ReserveRouterFundsResult {
  /** Reservation ID for fund settlement */
  reservationId: string;
  /** Cached pricing data for cost calculation */
  modelPricing: ModelPricing;
}

/**
 * Reserves funds for a router request.
 *
 * @param validated - Validated request information
 * @param routerRequestId - Router request ID
 * @param stripeCustomerId - Stripe customer ID for the organization
 * @returns Reservation ID and cached pricing data
 */
export function reserveRouterFunds(
  validated: ValidatedRouterRequest,
  routerRequestId: string,
  stripeCustomerId: string,
): Effect.Effect<ReserveRouterFundsResult, Error, Payments> {
  return Effect.gen(function* () {
    const payments = yield* Payments;

    // Estimate cost (also validates pricing availability)
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

    return {
      reservationId,
      modelPricing: estimate.modelPricing,
    };
  });
}

// =============================================================================
// Error Handling Functions
// =============================================================================

/**
 * Handles failure by updating router request and releasing funds.
 *
 * @param routerRequestId - Router request ID
 * @param reservationId - Reservation ID to release
 * @param request - Router request identifiers
 * @param errorMessage - Error message to record
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

// =============================================================================
// Metering Functions
// =============================================================================

/**
 * Enqueues metering data to the router metering queue.
 *
 * This is the single source of truth for all metering operations.
 * Both streaming and non-streaming handlers use this function to
 * asynchronously process usage data via the DLQ-backed queue.
 *
 * @param routerRequestId - Router request ID
 * @param reservationId - Reservation ID for fund settlement
 * @param request - Router request identifiers
 * @param usage - Token usage data
 * @param tokenCostCenticents - Token cost in centicents
 * @param toolCostCenticents - Tool cost in centicents (optional)
 * @returns Effect that completes when message is enqueued
 */
export function enqueueRouterMetering(
  routerRequestId: string,
  reservationId: string,
  request: RouterRequestIdentifiers,
  usage: TokenUsage,
  tokenCostCenticents: number,
  toolCostCenticents?: number,
): Effect.Effect<void, Error, RouterMeteringQueueService> {
  return Effect.gen(function* () {
    const queue = yield* RouterMeteringQueueService;

    // Compute total cost (sum of token and tool costs)
    const costCenticents = tokenCostCenticents + (toolCostCenticents ?? 0);

    const message: RouterMeteringMessage = {
      routerRequestId,
      reservationId,
      request,
      usage,
      costCenticents,
      tokenCostCenticents,
      toolCostCenticents,
      timestamp: Date.now(),
    };

    yield* queue.send(message);
  });
}
