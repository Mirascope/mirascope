import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useServerFn } from "@tanstack/react-start";
import { createServerFn } from "@tanstack/react-start";
import { getRequest } from "@tanstack/react-start/server";
import { Effect } from "effect";

import type { Result } from "@/app/lib/types";
import type {
  PublicOrganizationWithMembership,
  PublicProject,
  PublicEnvironment,
  ApiKeyCreateResponse,
} from "@/db/schema";

import { runEffect } from "@/app/lib/effect";
import { authenticate } from "@/auth";
import { DrizzleORM } from "@/db/client";
import { Database } from "@/db/database";
import { generateSlug } from "@/db/slug";

/**
 * Response from the onboarding server function.
 * Contains all created resources including the plaintext API key.
 */
export interface OnboardingResponse {
  organization: PublicOrganizationWithMembership;
  project: PublicProject;
  environment: PublicEnvironment;
  apiKey: ApiKeyCreateResponse;
}

/**
 * Request payload for the onboarding server function.
 */
export interface OnboardingRequest {
  organizationName: string;
}

/**
 * Server function that handles the complete onboarding flow.
 *
 * Creates an organization, default project, default environment, and default API key
 * in a single atomic transaction. If any step fails, all changes are rolled back.
 */
export const completeOnboarding = createServerFn({ method: "POST" })
  .inputValidator((data: OnboardingRequest) => data)
  .handler(async ({ data }): Promise<Result<OnboardingResponse>> => {
    const request = getRequest();
    if (!request) {
      return { success: false, error: "No request available" };
    }

    return await runEffect(
      Effect.gen(function* () {
        const client = yield* DrizzleORM;
        const db = yield* Database;
        const { user } = yield* authenticate(request);

        // Check if user already has organizations
        const existingOrgs = yield* db.organizations.findAll({
          userId: user.id,
        });
        if (existingOrgs.length > 0) {
          return yield* Effect.fail({
            message:
              "User already has an organization. Onboarding not required.",
          });
        }

        // Wrap all operations in a transaction for atomicity
        // If any step fails, everything rolls back
        return yield* client.withTransaction(
          Effect.gen(function* () {
            // Create organization (includes automatic OWNER membership)
            const organization = yield* db.organizations.create({
              userId: user.id,
              data: {
                name: data.organizationName,
                slug: generateSlug(data.organizationName),
              },
            });

            // Create default project (includes automatic ADMIN membership)
            const project = yield* db.organizations.projects.create({
              userId: user.id,
              organizationId: organization.id,
              data: { name: "Default", slug: "default" },
            });

            // Create default environment
            const environment =
              yield* db.organizations.projects.environments.create({
                userId: user.id,
                organizationId: organization.id,
                projectId: project.id,
                data: { name: "Default", slug: "default" },
              });

            // Create default API key (returns plaintext key only at creation)
            const apiKey =
              yield* db.organizations.projects.environments.apiKeys.create({
                userId: user.id,
                organizationId: organization.id,
                projectId: project.id,
                environmentId: environment.id,
                data: { name: "Default API Key" },
              });

            return { organization, project, environment, apiKey };
          }),
        );
      }),
    );
  });

/**
 * React hook for completing the onboarding flow.
 *
 * Calls the server function which creates all resources in a single transaction.
 * On success, invalidates the organizations query to update the UI.
 */
export const useCompleteOnboarding = () => {
  const completeOnboardingFn = useServerFn(completeOnboarding);
  const queryClient = useQueryClient();

  return useMutation({
    mutationKey: ["onboarding", "complete"],
    mutationFn: async (requestData: OnboardingRequest) => {
      const result = await completeOnboardingFn({ data: requestData });
      if (!result.success) {
        throw new Error(result.error);
      }
      return result.data;
    },
    onSuccess: () => {
      // Invalidate organizations to refresh the sidebar
      void queryClient.invalidateQueries({ queryKey: ["organizations"] });
    },
  });
};
