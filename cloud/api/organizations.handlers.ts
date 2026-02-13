import { Effect } from "effect";

import type {
  CreateOrganizationRequest,
  UpdateOrganizationRequest,
  CreatePaymentIntentRequest,
  PreviewSubscriptionChangeRequest,
  UpdateSubscriptionRequest,
  UpdateAutoReloadSettingsRequest,
} from "@/api/organizations.schemas";

import { Analytics } from "@/analytics";
import { AuthenticatedUser } from "@/auth";
import { Database } from "@/db/database";
import { Payments } from "@/payments";

export * from "@/api/organizations.schemas";

export const listOrganizationsHandler = Effect.gen(function* () {
  const db = yield* Database;
  const user = yield* AuthenticatedUser;
  return yield* db.organizations.findAll({ userId: user.id });
});

export const createOrganizationHandler = (payload: CreateOrganizationRequest) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const analytics = yield* Analytics;

    const organization = yield* db.organizations.create({
      data: { name: payload.name, slug: payload.slug },
      userId: user.id,
    });

    yield* analytics.trackEvent({
      name: "organization_created",
      properties: {
        organizationId: organization.id,
        organizationName: organization.name,
        userId: user.id,
      },
      distinctId: user.id,
    });

    return organization;
  });

export const getOrganizationHandler = (organizationId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.findById({
      organizationId,
      userId: user.id,
    });
  });

export const updateOrganizationHandler = (
  organizationId: string,
  payload: UpdateOrganizationRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.update({
      organizationId,
      data: payload,
      userId: user.id,
    });
  });

export const deleteOrganizationHandler = (organizationId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const analytics = yield* Analytics;

    yield* db.organizations.delete({ organizationId, userId: user.id });

    yield* analytics.trackEvent({
      name: "organization_deleted",
      properties: {
        organizationId,
        userId: user.id,
      },
      distinctId: user.id,
    });
  });

export const getOrganizationRouterBalanceHandler = (organizationId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const payments = yield* Payments;

    // First verify user has access to this organization
    const organization = yield* db.organizations.findById({
      organizationId,
      userId: user.id,
    });

    // Get the router balance info from Stripe
    const balanceInfo = yield* payments.products.router.getBalanceInfo(
      organization.stripeCustomerId,
    );

    // Return available balance in centi-cents (client will convert to dollars for display)
    return { balance: balanceInfo.availableBalance };
  });

export const createPaymentIntentHandler = (
  organizationId: string,
  payload: CreatePaymentIntentRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const payments = yield* Payments;

    // First verify user has access to this organization
    const organization = yield* db.organizations.findById({
      organizationId,
      userId: user.id,
    });

    // Create PaymentIntent for credit purchase
    const result =
      yield* payments.paymentIntents.createRouterCreditsPurchaseIntent({
        stripeCustomerId: organization.stripeCustomerId,
        amountInDollars: payload.amount,
        paymentMethodId: payload.paymentMethodId,
        metadata: {
          organizationId: organization.id,
        },
      });

    return {
      clientSecret: result.clientSecret,
      amount: result.amountInDollars,
      status: result.status,
    };
  });

export const getSubscriptionHandler = (organizationId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const payments = yield* Payments;

    // Verify user has access to this organization
    const organization = yield* db.organizations.findById({
      organizationId,
      userId: user.id,
    });

    // Get subscription details from Stripe
    return yield* payments.customers.subscriptions.get(
      organization.stripeCustomerId,
    );
  }).pipe(
    // In local dev, return a default free plan if Stripe is not configured
    Effect.catchAll((error) => {
      if (process.env.ENVIRONMENT === "development") {
        console.warn(
          "[dev] Stripe subscription lookup failed, returning free plan default:",
          error instanceof Error ? error.message : String(error),
        );
        return Effect.succeed({
          subscriptionId: "sub_dev_free",
          currentPlan: "free" as const,
          status: "active",
          currentPeriodEnd: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
          hasPaymentMethod: false,
        });
      }
      return Effect.fail(error);
    }),
  );

export const previewSubscriptionChangeHandler = (
  organizationId: string,
  payload: PreviewSubscriptionChangeRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const payments = yield* Payments;

    // Verify user has access to this organization
    const organization = yield* db.organizations.findById({
      organizationId,
      userId: user.id,
    });

    // Preview the subscription change
    return yield* payments.customers.subscriptions.previewChange({
      stripeCustomerId: organization.stripeCustomerId,
      targetPlan: payload.targetPlan,
      organizationId,
    });
  });

export const updateSubscriptionHandler = (
  organizationId: string,
  payload: UpdateSubscriptionRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const payments = yield* Payments;
    const analytics = yield* Analytics;

    // Verify user has access to this organization
    const organization = yield* db.organizations.findById({
      organizationId,
      userId: user.id,
    });

    // Update the subscription
    const result = yield* payments.customers.subscriptions.update({
      stripeCustomerId: organization.stripeCustomerId,
      targetPlan: payload.targetPlan,
      organizationId,
    });

    yield* analytics.trackEvent({
      name: "subscription_updated",
      properties: {
        organizationId,
        userId: user.id,
        targetPlan: payload.targetPlan,
      },
      distinctId: user.id,
    });

    return result;
  });

export const cancelScheduledDowngradeHandler = (organizationId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const payments = yield* Payments;

    // Verify user has access to this organization
    const organization = yield* db.organizations.findById({
      organizationId,
      userId: user.id,
    });

    // Cancel the scheduled downgrade
    yield* payments.customers.subscriptions.cancelScheduledDowngrade(
      organization.stripeCustomerId,
    );
  });

export const createSetupIntentHandler = (organizationId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const payments = yield* Payments;

    const organization = yield* db.organizations.findById({
      organizationId,
      userId: user.id,
    });

    return yield* payments.paymentMethods.createSetupIntent(
      organization.stripeCustomerId,
    );
  });

export const getPaymentMethodHandler = (organizationId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const payments = yield* Payments;

    const organization = yield* db.organizations.findById({
      organizationId,
      userId: user.id,
    });

    return yield* payments.paymentMethods.getDefault(
      organization.stripeCustomerId,
    );
  });

export const removePaymentMethodHandler = (organizationId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const payments = yield* Payments;

    const organization = yield* db.organizations.findById({
      organizationId,
      userId: user.id,
    });

    const paymentMethod = yield* payments.paymentMethods.getDefault(
      organization.stripeCustomerId,
    );

    /* v8 ignore start */
    if (!paymentMethod) {
      return;
    }
    /* v8 ignore end */

    yield* payments.paymentMethods.remove(
      organization.stripeCustomerId,
      paymentMethod.id,
    );
  });

export const getAutoReloadSettingsHandler = (organizationId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.getAutoReloadSettings({
      organizationId,
      userId: user.id,
    });
  });

export const updateAutoReloadSettingsHandler = (
  organizationId: string,
  payload: UpdateAutoReloadSettingsRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.updateAutoReloadSettings({
      organizationId,
      userId: user.id,
      data: payload,
    });
  });
