/**
 * @fileoverview Router product billing service.
 *
 * Provides Router-specific billing operations including usage metering,
 * fund reservations, and credit management. This service implements the
 * two-phase reservation pattern to prevent overdraft in concurrent scenarios.
 */

import Decimal from "decimal.js";
import { eq, and, sql } from "drizzle-orm";
import { Effect, Schedule } from "effect";

import type { TokenUsage } from "@/api/router/pricing";

import {
  type CostInCenticents,
  centicentsToDollars,
} from "@/api/router/cost-utils";
import { getModelPricing } from "@/api/router/pricing";
import {
  getCostCalculator,
  isValidProvider,
  type ProviderName,
} from "@/api/router/providers";
import { DrizzleORM } from "@/db/client";
import { creditReservations } from "@/db/schema";
import {
  StripeError,
  DatabaseError,
  InsufficientFundsError,
  ReservationStateError,
  NotFoundError,
} from "@/errors";
import { Stripe } from "@/payments/client";
import { Subscriptions } from "@/payments/subscriptions";

/**
 * Gas fee percentage applied to router usage charges.
 * A value of 0.05 represents a 5% fee.
 */
const GAS_FEE_PERCENTAGE = 0.05;

/**
 * Retry policy for meter charging operations.
 * Uses exponential backoff starting at 100ms, retrying up to 3 times.
 */
const METER_RETRY_POLICY = Schedule.exponential("100 millis").pipe(
  Schedule.compose(Schedule.recurs(3)),
);

/**
 * Comprehensive balance information for router billing.
 *
 * Contains all balance components needed for fund reservation checks:
 * - creditBalance: Total credit grants from Stripe
 * - meterUsage: Accumulated usage that will be invoiced
 * - activeReservations: Sum of pending reservations
 * - availableBalance: creditBalance - meterUsage (what can be reserved)
 */
export interface RouterBalanceInfo {
  /** Total credit grants in centi-cents */
  creditBalance: CostInCenticents;
  /** Accumulated meter usage in centi-cents */
  meterUsage: CostInCenticents;
  /** Sum of active reservations in centi-cents */
  activeReservations: CostInCenticents;
  /** Available balance (creditBalance - meterUsage) in centi-cents */
  availableBalance: CostInCenticents;
}

/**
 * Router product billing service.
 *
 * Handles all Router-specific billing operations including:
 * - Usage metering and balance tracking
 * - Fund reservations (two-phase pattern for concurrency safety)
 * - Credit charging with gas fees
 *
 * @example
 * ```ts
 * const program = Effect.gen(function* () {
 *   const payments = yield* Payments;
 *   const db = yield* Database;
 *
 *   // 1. Create router request in "pending" state (MUST be done first)
 *   const routerRequest = yield* db.organizations.projects.environments.apiKeys.routerRequests.create({
 *     userId: "user-123",
 *     organizationId: "org-456",
 *     projectId: "proj-789",
 *     environmentId: "env-012",
 *     data: {
 *       provider: "openai",
 *       model: "gpt-4",
 *       status: "pending",
 *       organizationId: "org-456",
 *       projectId: "proj-789",
 *       environmentId: "env-012",
 *       apiKeyId: "key-345",
 *       userId: "user-123",
 *     },
 *   });
 *
 *   // 2. Reserve funds (links to router request)
 *   const reservationId = yield* payments.products.router.reserveFunds({
 *     stripeCustomerId: "cus_123",
 *     estimatedCostCenticents: 500n, // $0.05
 *     routerRequestId: routerRequest.id,
 *   });
 *
 *   // 3. Make the actual provider request...
 *
 *   // 4. Update router request with actual usage/cost (on success)
 *   yield* db.organizations.projects.environments.apiKeys.routerRequests.update({
 *     userId: "user-123",
 *     organizationId: "org-456",
 *     projectId: "proj-789",
 *     environmentId: "env-012",
 *     routerRequestId: routerRequest.id,
 *     data: {
 *       inputTokens: 100n,
 *       outputTokens: 50n,
 *       costCenticents: 450n,
 *       status: "success",
 *       completedAt: new Date(),
 *     },
 *   });
 *
 *   // 5. Settle funds (releases reservation, charges meter)
 *   yield* payments.products.router.settleFunds(reservationId, 450n);
 * });
 * ```
 */
export class Router {
  private readonly subscriptions: Subscriptions;

  constructor(subscriptions: Subscriptions) {
    this.subscriptions = subscriptions;
  }
  /**
   * Gets the accumulated meter usage balance for a Stripe customer.
   *
   * Fetches meter event summaries for the current billing period and returns
   * the total usage in centi-cents. This represents how much the customer has used
   * in the current billing cycle but not yet been invoiced for.
   *
   * Since 1 meter unit = 1 centi-cent, we directly sum the aggregated values.
   *
   * Uses the shared Subscriptions.getActiveSubscription() method to avoid
   * code duplication.
   *
   * @param stripeCustomerId - The Stripe customer ID
   * @returns The accumulated meter usage in centi-cents (e.g., 50000n for $5 usage)
   * @throws NotFoundError - If no active subscription found
   * @throws StripeError - If API call fails
   */
  getUsageMeterBalance(
    stripeCustomerId: string,
  ): Effect.Effect<CostInCenticents, StripeError | NotFoundError, Stripe> {
    return Effect.gen(this, function* () {
      const stripe = yield* Stripe;

      // Get the active subscription using injected Subscriptions service
      const subscription =
        yield* this.subscriptions.getActiveSubscription(stripeCustomerId);

      // Get billing period from subscription
      const currentPeriodStart = subscription.current_period_start;
      const currentPeriodEnd = subscription.current_period_end;

      // Fetch meter event summaries for current billing period
      const summaries = yield* stripe.billing.meters.listEventSummaries(
        stripe.config.routerMeterId,
        {
          customer: stripeCustomerId,
          start_time: currentPeriodStart,
          end_time: currentPeriodEnd,
        },
      );

      // Sum up aggregated values (meter units = centi-cents)
      let totalCenticents = 0;
      for (const summary of summaries.data) {
        totalCenticents += summary.aggregated_value;
      }

      return BigInt(totalCenticents);
    });
  }

  /**
   * Charges the usage meter for a Stripe customer for Router.
   *
   * Records a meter event for the customer's usage, applying a gas fee.
   * The actual amount charged to the meter is `centicents * (1 + GAS_FEE_PERCENTAGE)`.
   *
   * Since 1 meter unit = 1 centi-cent, we directly use the centi-cent value as the meter value.
   *
   * @param stripeCustomerId - The Stripe customer ID
   * @param centicents - The base usage amount in centi-cents (e.g., 10000n for $1)
   * @returns Effect that succeeds when meter is charged
   * @throws StripeError - If meter event creation fails
   */
  chargeUsageMeter(
    stripeCustomerId: string,
    centicents: CostInCenticents,
  ): Effect.Effect<void, StripeError, Stripe> {
    return Effect.gen(this, function* () {
      const stripe = yield* Stripe;

      // Apply gas fee using Decimal for precision
      const chargedCenticents = new Decimal(centicents.toString()).mul(
        new Decimal(1).plus(GAS_FEE_PERCENTAGE),
      );

      // Meter value = charged centi-cents (since 1 meter unit = 1 centi-cent)
      const meterValue = chargedCenticents.round().toNumber();
      const finalValue = Math.max(meterValue, 1);

      // Create meter event
      yield* stripe.billing.meterEvents.create({
        event_name: "use_credits",
        payload: {
          stripe_customer_id: stripeCustomerId,
          value: finalValue.toString(),
        },
        timestamp: Math.floor(Date.now() / 1000),
      });
    });
  }

  /**
   * Gets the router credit balance from Stripe credit grants.
   *
   * Fetches all credit grants for the customer and filters for those that are
   * applicable to the router price (metered usage-based billing).
   *
   * @param stripeCustomerId - The Stripe customer ID
   * @returns The total credit grants in centi-cents (e.g., 100000n for $10)
   * @throws StripeError - If API call fails
   */
  getCreditBalance(
    stripeCustomerId: string,
  ): Effect.Effect<CostInCenticents, StripeError, Stripe> {
    return Effect.gen(function* () {
      const stripe = yield* Stripe;

      const credit_grants = yield* stripe.billing.creditGrants.list({
        customer: stripeCustomerId,
      });

      // Filter grants applicable to router price and sum their values
      const totalCenticents = credit_grants.data
        .filter((grant) => {
          // Must have monetary amount
          if (!grant.amount.monetary) return false;

          // Must be applicable to router price
          const config = grant.applicability_config;
          return (
            config.scope &&
            config.scope.prices?.some(
              (price) => price.id === stripe.config.routerPriceId,
            )
          );
        })
        .reduce((sum, grant) => {
          const { value, currency } = grant.amount.monetary!;
          // Convert cents to centi-cents: 1 cent = 100 centi-cents
          return currency === "usd" ? sum + BigInt(value) * 100n : sum;
        }, 0n);

      return totalCenticents;
    });
  }

  /**
   * Gets comprehensive balance information for a Stripe customer.
   *
   * Returns all balance components:
   * - creditBalance: Total credit grants
   * - meterUsage: Accumulated usage
   * - activeReservations: Sum of pending reservations
   * - availableBalance: creditBalance - meterUsage (what can be reserved)
   *
   * This is the single source of truth for fund reservation checks.
   *
   * @param stripeCustomerId - The Stripe customer ID
   * @returns Complete balance information in centi-cents
   * @throws NotFoundError - If no active subscription found
   * @throws StripeError - If Stripe API calls fail
   * @throws DatabaseError - If database query fails
   */
  getBalanceInfo(
    stripeCustomerId: string,
  ): Effect.Effect<
    RouterBalanceInfo,
    StripeError | DatabaseError | NotFoundError,
    Stripe | DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const db = yield* DrizzleORM;

      // Fetch credit balance and meter usage from Stripe
      const creditBalance = yield* this.getCreditBalance(stripeCustomerId);
      const meterUsage = yield* this.getUsageMeterBalance(stripeCustomerId);

      // Calculate active reservations from database
      const activeReservationsResult = yield* db
        .select({
          sum: sql<string>`COALESCE(SUM(${creditReservations.estimatedCostCenticents}), 0)`,
        })
        .from(creditReservations)
        .where(
          and(
            eq(creditReservations.stripeCustomerId, stripeCustomerId),
            eq(creditReservations.status, "active"),
          ),
        )
        .pipe(
          Effect.mapError(
            (error) =>
              new DatabaseError({
                message: "Failed to calculate active reservations",
                cause: error,
              }),
          ),
        );

      const activeReservations = BigInt(
        activeReservationsResult[0]?.sum ?? "0",
      );

      // Available balance = credit - meter usage (NOT subtracting reservations here)
      const availableBalance = creditBalance - meterUsage;

      return {
        creditBalance,
        meterUsage,
        activeReservations,
        availableBalance,
      };
    });
  }

  /**
   * Reserves funds for a router request to prevent overdraft in concurrent scenarios.
   *
   * This method implements the reservation phase of the two-phase pattern:
   * 1. Check if customer has sufficient available balance (total balance - active reservations)
   * 2. If sufficient, create a reservation record atomically linked to the router request
   * 3. Return reservation ID for later release
   *
   * The reservation "locks" the estimated cost so other concurrent requests can't use it.
   * This prevents race conditions where multiple requests could overdraft the account.
   *
   * **Important**: The router request must be created FIRST in "pending" state, then passed
   * to this method. This ensures every reservation is always linked to a request.
   *
   * After the request completes, caller MUST call `releaseFunds()` or `settleFunds()` to
   * release the reservation.
   *
   * @param stripeCustomerId - Stripe customer ID
   * @param estimatedCostCenticents - Estimated cost in centi-cents (e.g., 500n for $0.05)
   * @param routerRequestId - ID of the router request (must be created in "pending" state first)
   * @returns Reservation ID to use for release/settlement
   * @throws NotFoundError - If no active subscription found
   * @throws DatabaseError - If reservation creation fails
   * @throws InsufficientFundsError - If customer has insufficient available funds
   * @throws StripeError - If Stripe API calls fail
   */
  reserveFunds({
    stripeCustomerId,
    estimatedCostCenticents,
    routerRequestId,
  }: {
    stripeCustomerId: string;
    estimatedCostCenticents: CostInCenticents;
    routerRequestId: string;
  }): Effect.Effect<
    string,
    DatabaseError | InsufficientFundsError | StripeError | NotFoundError,
    DrizzleORM | Stripe
  > {
    return Effect.gen(this, function* () {
      const db = yield* DrizzleORM;

      // Get comprehensive balance information
      const balanceInfo = yield* this.getBalanceInfo(stripeCustomerId);

      // Check if sufficient funds available (available balance - active reservations)
      const netAvailableCenticents =
        balanceInfo.availableBalance - balanceInfo.activeReservations;
      if (netAvailableCenticents < estimatedCostCenticents) {
        return yield* new InsufficientFundsError({
          message: `Insufficient available funds. Required: ${estimatedCostCenticents} centi-cents ($${centicentsToDollars(estimatedCostCenticents).toFixed(4)}), Net Available: ${netAvailableCenticents} centi-cents ($${centicentsToDollars(netAvailableCenticents).toFixed(4)}) (Credit: ${balanceInfo.creditBalance}, Meter: ${balanceInfo.meterUsage}, Reserved: ${balanceInfo.activeReservations})`,
          required: centicentsToDollars(estimatedCostCenticents),
          available: centicentsToDollars(netAvailableCenticents),
        });
      }

      const [reservation] = yield* db
        .insert(creditReservations)
        .values({
          stripeCustomerId,
          estimatedCostCenticents,
          routerRequestId,
          status: "active",
        })
        .returning({ id: creditReservations.id })
        .pipe(
          Effect.mapError(
            (error) =>
              new DatabaseError({
                message: "Failed to create credit reservation",
                cause: error,
              }),
          ),
        );

      return reservation.id;
    });
  }

  /**
   * Releases a reservation after request completion.
   *
   * This is a lower-level method for releasing reservations.
   * Marks the reservation as released, freeing up the reserved funds for other requests.
   *
   * The reservation is already linked to a router request (via routerRequestId set during
   * reserveFunds), so you don't need to pass it again.
   *
   * Use this directly when you want to release without charging the meter.
   * For the common success case (release + charge), use `settleFunds` instead.
   *
   * @param reservationId - Reservation ID from reserveFunds()
   * @returns Effect that succeeds when release is complete
   * @throws DatabaseError - If database operation fails
   * @throws ReservationStateError - If reservation not found or already released
   */
  releaseFunds(
    reservationId: string,
  ): Effect.Effect<void, DatabaseError | ReservationStateError, DrizzleORM> {
    return Effect.gen(function* () {
      const db = yield* DrizzleORM;

      // Update reservation to released status
      const result = yield* db
        .update(creditReservations)
        .set({
          status: "released",
          releasedAt: new Date(),
        })
        .where(
          and(
            eq(creditReservations.id, reservationId),
            eq(creditReservations.status, "active"),
          ),
        )
        .returning({ id: creditReservations.id })
        .pipe(
          Effect.mapError(
            (error) =>
              new DatabaseError({
                message: "Failed to release credit reservation",
                cause: error,
              }),
          ),
        );

      if (result.length === 0) {
        return yield* new ReservationStateError({
          message: `Reservation not found or already released`,
          reservationId,
        });
      }
    });
  }

  /**
   * Settles a reservation after successful request completion.
   *
   * This method atomically:
   * 1. Releases the reservation (DB update within transaction)
   * 2. Charges the meter with actual cost (Stripe API)
   *
   * Both operations are wrapped in a database transaction. If Stripe charging fails,
   * the DB update is rolled back, leaving the reservation in 'active' status for
   * retry by the billing reconciliation cron job.
   *
   * ## Idempotency
   *
   * The transaction uses `WHERE status = 'active'` which ensures that if the
   * reservation is already released, the update affects 0 rows and the method
   * returns without charging. This provides safe retry by cron jobs without
   * double-charging.
   *
   * Use this for the common case when a router request succeeds and you have actual cost.
   * For failed requests where you don't want to charge, use `releaseFunds` directly.
   *
   * @param reservationId - Reservation ID from reserveFunds()
   * @param actualCostCenticents - Actual cost in centi-cents to charge
   * @returns Effect that succeeds when settlement is complete
   * @throws DatabaseError - If database operation fails
   * @throws ReservationStateError - If reservation not found
   * @throws StripeError - If meter charging fails (transaction rolls back)
   */
  settleFunds(
    reservationId: string,
    actualCostCenticents: CostInCenticents,
  ): Effect.Effect<
    void,
    DatabaseError | StripeError | ReservationStateError,
    Stripe | DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const db = yield* DrizzleORM;

      // Get reservation details for Stripe customer ID
      const [reservation] = yield* db
        .select({
          stripeCustomerId: creditReservations.stripeCustomerId,
        })
        .from(creditReservations)
        .where(eq(creditReservations.id, reservationId))
        .pipe(
          Effect.mapError(
            (error) =>
              new DatabaseError({
                message: "Failed to fetch reservation",
                cause: error,
              }),
          ),
        );

      if (!reservation) {
        return yield* new ReservationStateError({
          message: `Reservation not found`,
          reservationId,
        });
      }

      // Transaction: Release funds (DB) + Charge meter (Stripe)
      // If Stripe fails, the DB update rolls back
      yield* db.withTransaction(
        Effect.gen(this, function* () {
          // Release funds - skip charging if already released (idempotency)
          const alreadyReleased = yield* this.releaseFunds(reservationId).pipe(
            Effect.map(() => false),
            Effect.catchTag("ReservationStateError", () =>
              Effect.succeed(true),
            ),
          );

          if (alreadyReleased) {
            return;
          }

          yield* this.chargeUsageMeter(
            reservation.stripeCustomerId,
            actualCostCenticents,
          );
        }),
      );
    });
  }

  /**
   * Calculates cost from usage data and charges the router usage meter.
   *
   * This method:
   * 1. Validates the provider
   * 2. Gets the appropriate cost calculator for the provider
   * 3. Calculates costs using real pricing data from models.dev
   * 4. Charges the Stripe meter (with 5% gas fee and retries)
   *
   * Errors during cost calculation or meter charging are logged but don't fail
   * the request to ensure request processing continues even if metering fails.
   *
   * TODO: Replace retry logic with queue-based async metering for better
   * reliability. Track failed charges in a dead letter queue for reconciliation.
   * See queue implementation in [future PR reference].
   *
   * @param provider - Provider name (e.g., "openai", "anthropic", "google")
   * @param model - Model ID for cost calculation
   * @param usageData - Parsed usage data (TokenUsage format with validated non-negative numbers)
   * @param stripeCustomerId - Stripe customer ID to charge
   * @returns Effect that succeeds when metering is complete (or skipped)
   *
   * @example
   * ```ts
   * yield* payments.products.router.chargeForUsage({
   *   provider: "anthropic",
   *   model: "claude-3-opus",
   *   usageData: { inputTokens: 1000, outputTokens: 500 },
   *   stripeCustomerId: "cus_123",
   * });
   * ```
   */
  chargeForUsage({
    provider,
    model,
    usageData,
    stripeCustomerId,
  }: {
    provider: ProviderName;
    model: string;
    usageData: TokenUsage;
    stripeCustomerId: string;
  }): Effect.Effect<void, never, Stripe> {
    return Effect.gen(this, function* () {
      // Validate provider before getting cost calculator
      if (!isValidProvider(provider)) {
        console.warn("Invalid provider for metering:", { provider });
        return;
      }

      // Fetch pricing from models.dev
      const modelPricing = yield* getModelPricing(provider, model).pipe(
        Effect.catchAll((error) => {
          console.warn("Failed to fetch pricing:", { provider, model, error });
          return Effect.succeed(null);
        }),
      );

      // If pricing unavailable, log warning and skip charging
      if (!modelPricing) {
        console.warn("Pricing unavailable for model:", { provider, model });
        return;
      }

      // Get cost calculator for the provider
      const calculator = getCostCalculator(provider);

      // Calculate cost from TokenUsage
      const costBreakdown = yield* calculator.calculate(
        model,
        usageData,
        modelPricing,
      );

      // Charge the meter with retries (5% gas fee applied by chargeUsageMeter)
      // TODO: Replace with queue-based async metering for better reliability
      yield* this.chargeUsageMeter(
        stripeCustomerId,
        costBreakdown.totalCost,
      ).pipe(
        Effect.retry(METER_RETRY_POLICY),
        /* v8 ignore start */
        Effect.catchAll(() => Effect.succeed(undefined)),
        /* v8 ignore stop */
      );
    });
  }

  /**
   * Creates a paid credit grant for a Stripe customer.
   *
   * Credit grants allow customers to prepay for usage-based services. The
   * credits will be automatically applied to future invoices for the router
   * price. Grants are marked with category "paid" to distinguish them from
   * promotional credits.
   *
   * @param params.stripeCustomerId - The Stripe customer ID
   * @param params.amountInDollars - The credit amount in dollars (e.g., 50 for $50)
   * @param params.expiresAt - Optional expiration date for the credits
   * @param params.metadata - Optional metadata to attach to the credit grant
   * @returns The created credit grant ID
   * @throws StripeError - If credit grant creation fails
   *
   * @example
   * ```ts
   * const creditGrantId = yield* payments.products.router.createCreditGrant({
   *   stripeCustomerId: "cus_123",
   *   amountInDollars: 50,
   *   metadata: { source: "payment_intent" }
   * });
   * ```
   */
  createCreditGrant({
    stripeCustomerId,
    amountInDollars,
    expiresAt,
    metadata,
  }: {
    stripeCustomerId: string;
    amountInDollars: number;
    expiresAt?: Date;
    metadata?: Record<string, string>;
  }): Effect.Effect<string, StripeError, Stripe> {
    return Effect.gen(function* () {
      const stripe = yield* Stripe;

      // Convert dollars to cents
      const amountInCents = Math.round(amountInDollars * 100);

      // Create the credit grant scoped to the router price
      const creditGrant = yield* stripe.billing.creditGrants.create({
        customer: stripeCustomerId,
        amount: {
          type: "monetary",
          monetary: {
            currency: "usd",
            value: amountInCents,
          },
        },
        category: "paid",
        name: "Prepurchased Router Credits",
        applicability_config: {
          scope: {
            prices: [{ id: stripe.config.routerPriceId }],
          },
        },
        ...(expiresAt && {
          expires_at: Math.floor(expiresAt.getTime() / 1000),
        }),
        ...(metadata && { metadata }),
      });

      return creditGrant.id;
    });
  }
}
