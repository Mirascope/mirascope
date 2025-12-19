import { describe, it, expect, TestEffectEnvironmentFixture } from "@/tests/db";
import { Effect } from "effect";
import { EffectDatabase } from "@/db";

// Re-export describe, it, and expect for convenience
export { describe, it, expect };

// ============================================================================
// Test fixture effects
// ============================================================================

/**
 * Effect-native test fixture for authentication testing.
 *
 * Builds on TestEffectEnvironmentFixture and adds:
 * - An API key for the environment
 * - An additional environment for cross-environment validation
 *
 * Returns { owner, admin, org, project, environment, otherEnvironment, apiKey } where:
 * - owner: the user who owns the organization
 * - admin: an admin user in the organization
 * - org: the organization
 * - project: the project within the organization
 * - environment: the environment associated with the API key
 * - otherEnvironment: another environment in the same project (for cross-environment validation)
 * - apiKey: a plaintext API key for the environment
 *
 * Requires EffectDatabase - call `yield* EffectDatabase` in your test
 * if you need to perform additional database operations.
 */
export const TestEffectAuthFixture = Effect.gen(function* () {
  const envFixture = yield* TestEffectEnvironmentFixture;
  const db = yield* EffectDatabase;

  // Create another environment to test cross-environment validation
  const otherEnvironment = yield* db.organizations.projects.environments.create(
    {
      userId: envFixture.owner.id,
      organizationId: envFixture.org.id,
      projectId: envFixture.project.id,
      data: { name: "Other Env" },
    },
  );

  // Create API key for the main environment
  const apiKeyResponse =
    yield* db.organizations.projects.environments.apiKeys.create({
      userId: envFixture.owner.id,
      organizationId: envFixture.org.id,
      projectId: envFixture.project.id,
      environmentId: envFixture.environment.id,
      data: { name: "Test API Key" },
    });

  return {
    ...envFixture,
    otherEnvironment,
    apiKey: apiKeyResponse.key,
  };
});
