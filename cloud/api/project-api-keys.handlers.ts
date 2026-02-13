import { Effect } from "effect";

import type { SetProjectApiKeyRequest } from "@/api/project-api-keys.schemas";
import type { ProviderName } from "@/api/router/providers";

import { AuthenticatedUser } from "@/auth";
import { OrganizationMemberships } from "@/db/organization-memberships";
import { ProjectApiKeys } from "@/db/project-api-keys";
import { ProjectMemberships } from "@/db/project-memberships";
import { PlanLimitExceededError } from "@/errors";
import { Payments } from "@/payments";

export * from "@/api/project-api-keys.schemas";

/**
 * Verify the organization is on a Pro or Team plan.
 * Free tier users cannot manage BYOK keys.
 */
const requirePaidPlan = (organizationId: string) =>
  Effect.gen(function* () {
    const payments = yield* Payments;
    const planTier =
      yield* payments.customers.subscriptions.getPlan(organizationId);
    if (planTier === "free") {
      return yield* Effect.fail(
        new PlanLimitExceededError({
          message:
            "BYOK (Bring Your Own Key) requires a Pro or Team plan. Upgrade to use your own API keys.",
          resource: "project_api_keys",
          limitType: "byok",
          currentUsage: 0,
          limit: 0,
          planTier,
        }),
      );
    }
    return planTier;
  });

/**
 * Create the ProjectApiKeys service instance.
 * Instantiated per-request since it depends on membership services.
 */
const createService = () => {
  const orgMemberships = new OrganizationMemberships();
  const projectMemberships = new ProjectMemberships(orgMemberships);
  return new ProjectApiKeys(projectMemberships);
};

export const listProjectApiKeysHandler = (
  organizationId: string,
  projectId: string,
) =>
  Effect.gen(function* () {
    yield* requirePaidPlan(organizationId);
    const user = yield* AuthenticatedUser;
    const service = createService();
    const keys = yield* service.list({
      userId: user.id,
      organizationId,
      projectId,
    });
    return keys.map((k) => ({
      ...k,
      updatedAt: k.updatedAt?.toISOString() ?? new Date().toISOString(),
    }));
  });

export const setProjectApiKeyHandler = (
  organizationId: string,
  projectId: string,
  provider: string,
  payload: SetProjectApiKeyRequest,
) =>
  Effect.gen(function* () {
    yield* requirePaidPlan(organizationId);
    const user = yield* AuthenticatedUser;
    const service = createService();
    const result = yield* service.set({
      userId: user.id,
      organizationId,
      projectId,
      provider: provider as ProviderName,
      key: payload.key,
    });
    return {
      ...result,
      updatedAt: result.updatedAt?.toISOString() ?? new Date().toISOString(),
    };
  });

export const deleteProjectApiKeyHandler = (
  organizationId: string,
  projectId: string,
  provider: string,
) =>
  Effect.gen(function* () {
    yield* requirePaidPlan(organizationId);
    const user = yield* AuthenticatedUser;
    const service = createService();
    yield* service.delete({
      userId: user.id,
      organizationId,
      projectId,
      provider: provider as ProviderName,
    });
  });
