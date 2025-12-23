import { describe, it, expect } from "@/tests/db";
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
 * Creates a test environment with an API key for testing authentication
 * and authorization flows.
 *
 * Returns { testUser, testOrg, testProject, testEnvironment, otherEnvironment, testApiKey } where:
 * - testUser: the user who owns the organization
 * - testOrg: the organization
 * - testProject: the project within the organization
 * - testEnvironment: the environment associated with the API key
 * - otherEnvironment: another environment in the same project (for cross-environment validation)
 * - testApiKey: a plaintext API key for the testEnvironment
 *
 * Requires EffectDatabase - call `yield* EffectDatabase` in your test
 * if you need to perform additional database operations.
 */
export const TestEffectAuthFixture = Effect.gen(function* () {
  const db = yield* EffectDatabase;

  // Create test user
  const testUser = yield* db.users.create({
    data: { email: "test@example.com", name: "Test User" },
  });

  // Create organization
  const testOrg = yield* db.organizations.create({
    userId: testUser.id,
    data: { name: "Test Org" },
  });

  // Create project
  const testProject = yield* db.organizations.projects.create({
    userId: testUser.id,
    organizationId: testOrg.id,
    data: { name: "Test Project" },
  });

  // Create environment
  const testEnvironment = yield* db.organizations.projects.environments.create({
    userId: testUser.id,
    organizationId: testOrg.id,
    projectId: testProject.id,
    data: { name: "Test Env" },
  });

  // Create another environment to test cross-environment validation
  const otherEnvironment = yield* db.organizations.projects.environments.create(
    {
      userId: testUser.id,
      organizationId: testOrg.id,
      projectId: testProject.id,
      data: { name: "Other Env" },
    },
  );

  // Create API key
  const apiKeyResponse =
    yield* db.organizations.projects.environments.apiKeys.create({
      userId: testUser.id,
      organizationId: testOrg.id,
      projectId: testProject.id,
      environmentId: testEnvironment.id,
      data: { name: "Test API Key" },
    });

  return {
    testUser,
    testOrg,
    testProject,
    testEnvironment,
    otherEnvironment,
    testApiKey: apiKeyResponse.key,
  };
});
