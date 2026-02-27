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
        const subscription = yield* payments.customers.subscriptions.get(
          org.stripeCustomerId,
        );
        /* v8 ignore start -- requires Stripe to return free plan for existing org; tested via integration tests */
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
        /* v8 ignore stop */
      }
    }

    const organization = yield* db.organizations.create({
      data: { name: payload.name, slug: payload.slug },
      userId: user.id,
    });

    // If a paid plan was requested with a verified payment method,
    // attach the payment method and upgrade the subscription.
    if (requestedPlan !== "free" && payload.paymentMethodId) {
      yield* Effect.gen(function* () {
        // Attach the verified payment method to the new Stripe customer
        yield* payments.paymentMethods.attachAndSetDefault(
          organization.stripeCustomerId,
          payload.paymentMethodId!,
        );

        // Upgrade subscription to the paid plan (charges via invoice)
        yield* payments.customers.subscriptions.update({
          stripeCustomerId: organization.stripeCustomerId,
          targetPlan: requestedPlan,
          organizationId: organization.id,
        });
      }).pipe(
        /* v8 ignore start -- requires Stripe upgrade failure; tested via integration tests */
        Effect.catchAll((upgradeError) =>
          Effect.gen(function* () {
            // Payment method was pre-verified, so failure here is rare.
            // Clean up the org — user can retry.
            yield* db.organizations
              .delete({
                userId: user.id,
                organizationId: organization.id,
              })
              .pipe(Effect.catchAll(() => Effect.void));
            return yield* Effect.fail(upgradeError);
          }),
        ),
        /* v8 ignore stop */
      );
    }

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

export const createOrgSetupIntentHandler = Effect.gen(function* () {
  const payments = yield* Payments;
  return yield* payments.paymentMethods.createSetupIntentWithoutCustomer();
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
  });

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
    /* v8 ignore start -- identity pass-throughs: catch and re-throw */
    Effect.catchAllDefect((defect) => {
      return Effect.die(defect);
    }),
    Effect.catchAll((error) => {
      return Effect.fail(error);
    }),
    /* v8 ignore stop */
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
