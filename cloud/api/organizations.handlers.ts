import { Effect } from "effect";
import { Database } from "@/db";
import { AuthenticatedUser } from "@/auth";
import { Payments } from "@/payments";
import { Analytics } from "@/analytics";
import type {
  CreateOrganizationRequest,
  UpdateOrganizationRequest,
  CreatePaymentIntentRequest,
  PreviewSubscriptionChangeRequest,
  UpdateSubscriptionRequest,
} from "@/api/organizations.schemas";

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
        metadata: {
          organizationId: organization.id,
        },
      });

    return {
      clientSecret: result.clientSecret,
      amount: result.amountInDollars,
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
