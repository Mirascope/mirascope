import { Effect } from "effect";
import { Database } from "@/db";
import { AuthenticatedUser } from "@/auth";
import { Payments } from "@/payments";
import type {
  CreateOrganizationRequest,
  UpdateOrganizationRequest,
  CreatePaymentIntentRequest,
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
    return yield* db.organizations.create({
      data: { name: payload.name, slug: payload.slug },
      userId: user.id,
    });
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
    yield* db.organizations.delete({ organizationId, userId: user.id });
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
        customerId: organization.stripeCustomerId,
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
