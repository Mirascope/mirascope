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
import { PlanLimitExceededError } from "@/errors";
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
    const payments = yield* Payments;

    const requestedPlan = payload.planTier ?? "free";

    // Block creation of a second free org (each user may own at most one).
    // Paid org creation is always allowed.
    if (requestedPlan === "free") {
      const userOrgs = yield* db.organizations.findAll({ userId: user.id });
      const ownedOrgs = userOrgs.filter((org) => org.role === "OWNER");

      for (const org of ownedOrgs) {
        const subscription = yield* payments.customers.subscriptions
          .get(org.stripeCustomerId)
          .pipe(
            Effect.catchAll(() =>
              Effect.succeed({ currentPlan: "free" as const }),
            ),
          );
        if (subscription.currentPlan === "free") {
          return yield* Effect.fail(
            new PlanLimitExceededError({
              message:
                "You already own a free organization. Please upgrade your existing organization or create a paid organization.",
              resource: "organizations",
              limitType: "free_organizations",
              currentUsage: 1,
              limit: 1,
              planTier: "free",
            }),
          );
        }
      }
    }

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
        planTier: requestedPlan,
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
  }).pipe(
    // In local dev, return zero balance if Stripe is not configured
    Effect.catchAllDefect((defect) => {
      if (process.env.ENVIRONMENT === "development") {
        console.warn("[dev] Stripe router balance unavailable, returning 0");
        return Effect.succeed({ balance: 0n });
      }
      return Effect.die(defect);
    }),
    Effect.catchAll((error) => {
      if (process.env.ENVIRONMENT === "development") {
        console.warn("[dev] Stripe router balance failed, returning 0");
        return Effect.succeed({ balance: 0n });
      }
      return Effect.fail(error);
    }),
  );

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
    Effect.catchAllDefect((defect) => {
      if (process.env.ENVIRONMENT === "development") {
        console.warn(
          "[dev] Stripe subscription unavailable, returning free plan default",
        );
        return Effect.succeed({
          subscriptionId: "sub_dev_free",
          currentPlan: "free" as const,
          status: "active",
          currentPeriodEnd: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
          hasPaymentMethod: false,
        });
      }
      return Effect.die(defect);
    }),
    Effect.catchAll((error) => {
      if (process.env.ENVIRONMENT === "development") {
        console.warn(
          "[dev] Stripe subscription failed, returning free plan default",
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
  }).pipe(
    Effect.catchAllDefect((defect) => {
      if (process.env.ENVIRONMENT === "development") {
        console.warn("[dev] Stripe payment method unavailable, returning null");
        return Effect.succeed(null);
      }
      return Effect.die(defect);
    }),
    Effect.catchAll((error) => {
      if (process.env.ENVIRONMENT === "development") {
        console.warn("[dev] Stripe payment method failed, returning null");
        return Effect.succeed(null);
      }
      return Effect.fail(error);
    }),
  );

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
