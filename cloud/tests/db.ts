import { Effect, Layer, Config } from "effect";
import { describe, expect } from "@effect/vitest";
import { createCustomIt, withRollback } from "@/tests/shared";
import { DrizzleORM, type DrizzleORMClient } from "@/db/client";
import { Database } from "@/db";
import { PgClient } from "@effect/sql-pg";
import { SqlClient } from "@effect/sql";
import { CONNECTION_FILE } from "@/tests/global-setup";
import { Payments } from "@/payments";
import { MockStripe } from "@/tests/payments";
import { Analytics } from "@/analytics";
import { SpansMeteringQueueService } from "@/workers/spansMeteringQueue";
import { Settings } from "@/settings";
import { MockSettingsLayer } from "@/tests/settings";
import fs from "fs";
import assert from "node:assert";

// Re-export describe, expect, and assert for convenience
export { describe, expect, assert };

// Get the test database URL from the file written by global-setup.ts
function getTestDatabaseUrl(): string {
  try {
    return fs.readFileSync(CONNECTION_FILE, "utf-8");
  } catch {
    throw new Error(
      "TEST_DATABASE_URL not set. Ensure global-setup.ts ran successfully.",
    );
  }
}

export const TEST_DATABASE_URL = getTestDatabaseUrl();

/**
 * PgClient layer configured for test database.
 * Uses layerConfig to properly handle the connection string.
 */
const TestPgClient = PgClient.layerConfig({
  url: Config.redacted(Config.succeed(TEST_DATABASE_URL)),
});

/**
 * Layer that provides the Effect-native DrizzleORM service for tests.
 *
 * Note: This layer is automatically provided by the patched `it.effect`.
 * You only need to import this if you need to provide it manually.
 */
export const TestDrizzleORM: Layer.Layer<DrizzleORM | SqlClient.SqlClient> =
  DrizzleORM.Default.pipe(Layer.provideMerge(TestPgClient), Layer.orDie);

/**
 * Mock layer for Analytics that provides a no-op implementation for tests.
 */
export const MockAnalytics = Layer.succeed(Analytics, {
  googleAnalytics: null as never,
  postHog: null as never,
  trackEvent: () => Effect.void,
  trackPageView: () => Effect.void,
  identify: () => Effect.void,
  initialize: () => Effect.void,
});

/**
 * Mock layer for SpansMeteringQueueService that suppresses queue operations in tests.
 */
export const MockSpansMeteringQueue = Layer.succeed(
  SpansMeteringQueueService,
  SpansMeteringQueueService.of({
    send: () => Effect.succeed(undefined), // No-op in tests
  }),
);

/**
 * A Layer that provides the Effect-native `Database`, `DrizzleORM`,
 * `SqlClient`, and `Settings` services for tests.
 *
 * Note: This layer is automatically provided by `it.effect` from this module,
 * and tests are automatically wrapped in a transaction that rolls back.
 * You only need to import this if you need to provide it manually (e.g., in
 * tests that don't use `it.effect`).
 */
export const TestDatabase: Layer.Layer<
  | Database
  | DrizzleORM
  | SqlClient.SqlClient
  | Analytics
  | SpansMeteringQueueService
  | Settings
> = Effect.gen(function* () {
  // Lazy import to avoid circular dependency
  const { MockStripe } = yield* Effect.promise(
    () => import("@/tests/payments"),
  );
  return Layer.mergeAll(
    Database.Default.pipe(
      Layer.provideMerge(TestDrizzleORM),
      Layer.provide(
        Payments.Default.pipe(
          Layer.provide(MockStripe),
          Layer.provideMerge(TestDrizzleORM),
        ),
      ),
    ),
    MockAnalytics,
    MockSpansMeteringQueue,
    MockSettingsLayer(),
  );
}).pipe(Layer.unwrapEffect);

// =============================================================================
// Type-safe test utilities with automatic layer provision
// =============================================================================

/**
 * Services that are automatically provided to all `it.effect` tests.
 */
export type TestServices =
  | Database
  | DrizzleORM
  | SqlClient.SqlClient
  | Analytics
  | SpansMeteringQueueService
  | Settings;

/**
 * Wraps a test function to automatically provide TestDatabase
 * and wrap in a transaction that rolls back.
 */
const wrapEffectTest =
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (original: any) =>
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (name: any, fn: any, timeout?: any) => {
      // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-return
      return original(
        name,
        () =>
          // eslint-disable-next-line @typescript-eslint/no-unsafe-return, @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
          fn().pipe(withRollback).pipe(Effect.provide(TestDatabase)),
        timeout,
      );
    };

/**
 * Type-safe `it` with `it.effect` that automatically:
 * 1. Wraps tests in a transaction that rolls back
 * 2. Provides TestDatabase layer
 *
 * Use this instead of importing directly from @effect/vitest.
 *
 * @example
 * ```ts
 * import { it, expect } from "@/tests/db";
 * import { Effect } from "effect";
 * import { Database } from "@/db";
 *
 * it.effect("creates a user", () =>
 *   Effect.gen(function* () {
 *     const db = yield* Database;
 *     const user = yield* db.users.create({ data: { email: "test@example.com" } });
 *     expect(user.email).toBe("test@example.com");
 *   })
 * );
 * ```
 */
export const it = createCustomIt<TestServices>(wrapEffectTest);

// ============================================================================
// Mock database builder
// ============================================================================

// ============================================================================
// Mock DrizzleORM builder (Effect-native)
// ============================================================================

type MockEffectResult = unknown[] | Error;

/**
 * Builder for creating mock DrizzleORM layers with sequenced responses.
 *
 * Each call to select/insert/update/delete adds a response to a queue.
 * When the mock is used, responses are returned in order. Pass an array
 * for success, or an Error for failure.
 *
 * Unlike MockDatabase which returns a Database object, this returns a Layer
 * that can be provided to Effect-native services.
 *
 * @example
 * ```ts
 * const mockLayer = new MockDrizzleORM()
 *   .insert([{ id: "1", email: "test@example.com" }])  // insert succeeds
 *   .build();
 *
 * const result = yield* db.users
 *   .create({ data: { email: "test@example.com" } })
 *   .pipe(Effect.provide(mockLayer));
 * ```
 *
 * @example Multi-step operation testing
 * ```ts
 * // Test where select fails
 * const mockLayer = new MockDrizzleORM()
 *   .select(new Error("Connection failed"))
 *   .build();
 * ```
 */
export class MockDrizzleORM {
  private selectResults: MockEffectResult[] = [];
  private selectDistinctResults: MockEffectResult[] = [];
  private insertResults: MockEffectResult[] = [];
  private updateResults: MockEffectResult[] = [];
  private deleteResults: MockEffectResult[] = [];

  select(result: MockEffectResult): this {
    this.selectResults.push(result);
    return this;
  }

  selectDistinct(result: MockEffectResult): this {
    this.selectDistinctResults.push(result);
    return this;
  }

  insert(result: MockEffectResult): this {
    this.insertResults.push(result);
    return this;
  }

  update(result: MockEffectResult): this {
    this.updateResults.push(result);
    return this;
  }

  delete(result: MockEffectResult): this {
    this.deleteResults.push(result);
    return this;
  }

  /**
   * Builds a Layer<Database> with the mocked DrizzleORM and optional custom Payments layer.
   *
   * @param paymentsLayer - Optional custom Payments layer. If not provided, uses MockPayments.
   */
  build(paymentsLayer?: Layer.Layer<Payments>): Layer.Layer<Database> {
    let selectIndex = 0;
    let selectDistinctIndex = 0;
    let insertIndex = 0;
    let updateIndex = 0;
    let deleteIndex = 0;

    const makeEffect = (
      results: MockEffectResult[],
      index: number,
    ): Effect.Effect<unknown[], { _tag: string; cause: Error }> => {
      const result = results[index];
      if (result === undefined) {
        return Effect.fail({
          _tag: "SqlError",
          cause: new Error("No more mocked responses"),
        });
      }
      if (result instanceof Error) {
        return Effect.fail({ _tag: "SqlError", cause: result });
      }
      return Effect.succeed(result);
    };

    // Create a chainable proxy that returns itself for method calls,
    // then returns the appropriate Effect at .pipe()
    // The proxy wraps the Effect itself so it can be yielded directly
    const createChainableProxy = (
      results: MockEffectResult[],
      index: number,
    ): unknown => {
      const effect = makeEffect(results, index);

      return new Proxy(
        effect, // Proxy the Effect itself so it can be yielded
        {
          get: (target, prop) => {
            if (prop === "pipe") {
              // At .pipe(), apply the given transformations to the effect
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              return (...fns: Array<(e: any) => any>) => {
                // eslint-disable-next-line @typescript-eslint/no-unsafe-return
                return fns.reduce((acc, fn) => fn(acc), effect);
              };
            }
            // For chainable methods, return a function that returns the proxy
            if (
              typeof prop === "string" &&
              [
                "from",
                "where",
                "limit",
                "offset",
                "orderBy",
                "innerJoin",
                "leftJoin",
                "values",
                "set",
                "returning",
                "onConflictDoUpdate",
                "onConflictDoNothing",
              ].includes(prop)
            ) {
              return () => createChainableProxy(results, index);
            }
            // For all other properties, delegate to the Effect target
            // eslint-disable-next-line @typescript-eslint/no-unsafe-return
            return Reflect.get(target, prop);
          },
        },
      );
    };

    const drizzleMock = {
      select: () => {
        const idx = selectIndex++;
        return createChainableProxy(this.selectResults, idx);
      },
      selectDistinct: () => {
        const idx = selectDistinctIndex++;
        return createChainableProxy(this.selectDistinctResults, idx);
      },
      insert: () => {
        const idx = insertIndex++;
        return createChainableProxy(this.insertResults, idx);
      },
      update: () => {
        const idx = updateIndex++;
        return createChainableProxy(this.updateResults, idx);
      },
      delete: () => {
        const idx = deleteIndex++;
        return createChainableProxy(this.deleteResults, idx);
      },
      // Mock withTransaction to just run the effect directly (no actual transaction)
      withTransaction: <A, E, R>(effect: Effect.Effect<A, E, R>) => effect,
    } as unknown as DrizzleORMClient;

    const mockDrizzleORMLayer = Layer.succeed(DrizzleORM, drizzleMock);

    // If no custom payments layer provided, create one with MockStripe + our mockDrizzleORMLayer
    // This ensures DefaultMockPayments's MockDrizzleORMLayer doesn't override our custom mock
    const effectivePaymentsLayer =
      paymentsLayer ??
      Payments.Default.pipe(
        Layer.provide(MockStripe),
        Layer.provide(mockDrizzleORMLayer),
      );

    return Database.Default.pipe(
      Layer.provide(mockDrizzleORMLayer),
      Layer.provide(effectivePaymentsLayer),
    );
  }
}

// ============================================================================
// Test fixture effects
// ============================================================================

/**
 * Effect-native test fixture for organizations.
 *
 * Creates a test organization with members of all roles and a non-member user
 * using the Effect-native `Database` service.
 *
 * Each invocation generates unique email addresses to prevent conflicts
 * when tests run in shared transaction contexts.
 *
 * Returns { org, owner, admin, member, nonMember } where:
 * - owner: a user who owns the organization (OWNER role)
 * - admin: a user with ADMIN role
 * - member: a user with MEMBER role
 * - nonMember: a user who is NOT a member (useful for permission tests)
 *
 * Requires Database - call `yield* Database` in your test
 * if you need to perform additional database operations.
 */
export const TestOrganizationFixture = Effect.gen(function* () {
  const db = yield* Database;

  // Create users using Effect-native service with unique emails
  const owner = yield* db.users.create({
    data: { email: `owner@example.com`, name: "Owner" },
  });

  const admin = yield* db.users.create({
    data: { email: `admin@example.com`, name: "Admin" },
  });

  const member = yield* db.users.create({
    data: { email: `member@example.com`, name: "Member" },
  });

  const nonMember = yield* db.users.create({
    data: { email: `nonmember@example.com`, name: "Non Member" },
  });

  const org = yield* db.organizations.create({
    userId: owner.id,
    data: { name: `Test Organization`, slug: `test-organization` },
  });

  yield* db.organizations.memberships.create({
    userId: owner.id,
    organizationId: org.id,
    data: { memberId: admin.id, role: "ADMIN" },
  });

  yield* db.organizations.memberships.create({
    userId: owner.id,
    organizationId: org.id,
    data: { memberId: member.id, role: "MEMBER" },
  });

  return {
    org,
    owner,
    admin,
    member,
    nonMember,
  };
});

/**
 * Effect-native test fixture for testing FREE plan seat limits.
 *
 * Creates a minimal organization with only the owner (1 seat used).
 * Use with TestSubscriptionWithRealDatabaseFixture({ plan: "free" }, TestDatabase)
 * to test seat limit enforcement.
 *
 * Returns { org, owner, nonMember } where:
 * - org: organization with only owner as member
 * - owner: the organization owner (OWNER role)
 * - nonMember: a user not in the organization (for testing additions)
 *
 * Requires Database - call `yield* Database` in your test.
 *
 * Example usage:
 * ```ts
 * it.effect("test seat limit", () =>
 *   Effect.gen(function* () {
 *     const { org, owner, nonMember } = yield* TestFreePlanOrganizationFixture;
 *     const db = yield* Database;
 *     // Try to add nonMember - should fail with FREE plan
 *     const result = yield* db.organizations.memberships.create({
 *       userId: owner.id,
 *       organizationId: org.id,
 *       data: { memberId: nonMember.id, role: "MEMBER" },
 *     }).pipe(Effect.flip);
 *     expect(result).toBeInstanceOf(PlanLimitExceededError);
 *   }).pipe(Effect.provide(TestSubscriptionWithRealDatabaseFixture({ plan: "free" }, TestDatabase))),
 * );
 * ```
 */
export const TestFreePlanOrganizationFixture = Effect.gen(function* () {
  const db = yield* Database;

  // Create users
  const owner = yield* db.users.create({
    data: { email: `owner-free@example.com`, name: "Owner" },
  });

  const nonMember = yield* db.users.create({
    data: { email: `nonmember-free@example.com`, name: "Non Member" },
  });

  // Create organization (owner is automatically added with OWNER role)
  const org = yield* db.organizations.create({
    userId: owner.id,
    data: { name: `Free Plan Organization`, slug: `free-plan-organization` },
  });

  return {
    org,
    owner,
    nonMember,
  };
});
/**
 * Effect-native test fixture for projects.
 *
 * Creates a test project within an organization with explicit project members
 * using the Effect-native `Database` service.
 *
 * Reuses `TestOrganizationFixture` to set up the organization.
 *
 * Returns { org, project, owner, admin, member, nonMember, projectAdmin, projectDeveloper, projectViewer, projectAnnotator } where:
 * - org: the organization containing the project
 * - project: the created project
 * - owner: org owner (implicit project ADMIN access)
 * - admin: org admin (implicit project ADMIN access)
 * - member: org member without explicit project membership
 * - nonMember: not an org member
 * - projectAdmin: org member with explicit project ADMIN membership
 * - projectDeveloper: org member with explicit project DEVELOPER membership
 * - projectViewer: org member with explicit project VIEWER membership
 * - projectAnnotator: org member with explicit project ANNOTATOR membership
 *
 * Requires Database - call `yield* Database` in your test
 * if you need to perform additional database operations.
 */
export const TestProjectFixture = Effect.gen(function* () {
  const orgFixture = yield* TestOrganizationFixture;
  const db = yield* Database;

  // Create project using Projects Effect-native service (creator gets project ADMIN automatically)
  const project = yield* db.organizations.projects.create({
    userId: orgFixture.owner.id,
    organizationId: orgFixture.org.id,
    data: { name: "Test Project", slug: "test-project" },
  });

  // Create project members (must be org members first)
  const projectAdmin = yield* db.users.create({
    data: { email: "project-admin@example.com", name: "Project Admin" },
  });
  yield* db.organizations.memberships.create({
    userId: orgFixture.owner.id,
    organizationId: orgFixture.org.id,
    data: { memberId: projectAdmin.id, role: "MEMBER" },
  });
  yield* db.organizations.projects.memberships.create({
    userId: orgFixture.owner.id,
    organizationId: orgFixture.org.id,
    projectId: project.id,
    data: { memberId: projectAdmin.id, role: "ADMIN" },
  });

  const projectDeveloper = yield* db.users.create({
    data: { email: "project-developer@example.com", name: "Project Developer" },
  });
  yield* db.organizations.memberships.create({
    userId: orgFixture.owner.id,
    organizationId: orgFixture.org.id,
    data: { memberId: projectDeveloper.id, role: "MEMBER" },
  });
  yield* db.organizations.projects.memberships.create({
    userId: orgFixture.owner.id,
    organizationId: orgFixture.org.id,
    projectId: project.id,
    data: { memberId: projectDeveloper.id, role: "DEVELOPER" },
  });

  const projectViewer = yield* db.users.create({
    data: { email: "project-viewer@example.com", name: "Project Viewer" },
  });
  yield* db.organizations.memberships.create({
    userId: orgFixture.owner.id,
    organizationId: orgFixture.org.id,
    data: { memberId: projectViewer.id, role: "MEMBER" },
  });
  yield* db.organizations.projects.memberships.create({
    userId: orgFixture.owner.id,
    organizationId: orgFixture.org.id,
    projectId: project.id,
    data: { memberId: projectViewer.id, role: "VIEWER" },
  });

  const projectAnnotator = yield* db.users.create({
    data: { email: "project-annotator@example.com", name: "Project Annotator" },
  });
  yield* db.organizations.memberships.create({
    userId: orgFixture.owner.id,
    organizationId: orgFixture.org.id,
    data: { memberId: projectAnnotator.id, role: "MEMBER" },
  });
  yield* db.organizations.projects.memberships.create({
    userId: orgFixture.owner.id,
    organizationId: orgFixture.org.id,
    projectId: project.id,
    data: { memberId: projectAnnotator.id, role: "ANNOTATOR" },
  });

  return {
    ...orgFixture,
    project,
    projectAdmin,
    projectDeveloper,
    projectViewer,
    projectAnnotator,
  };
});

/**
 * Effect-native test fixture for environments.
 *
 * Creates a test environment within a project using the Effect-native
 * `Database` service.
 *
 * Reuses `TestProjectFixture` to set up the organization and project.
 *
 * Returns all properties from TestProjectFixture plus:
 * - environment: the created environment
 *
 * Requires Database - call `yield* Database` in your test
 * if you need to perform additional database operations.
 */
export const TestEnvironmentFixture = Effect.gen(function* () {
  const projectFixture = yield* TestProjectFixture;
  const db = yield* Database;

  const environment = yield* db.organizations.projects.environments.create({
    userId: projectFixture.owner.id,
    organizationId: projectFixture.org.id,
    projectId: projectFixture.project.id,
    data: { name: "development", slug: "development" },
  });

  return {
    ...projectFixture,
    environment,
  };
});

/**
 * Effect-native test fixture for API keys.
 *
 * Creates a test API key within an environment using the Effect-native
 * `Database` service.
 *
 * Reuses `TestEnvironmentFixture` to set up the organization, project, and environment.
 *
 * Returns all properties from TestEnvironmentFixture plus:
 * - apiKey: the created API key (includes the plaintext key)
 *
 * Requires Database - call `yield* Database` in your test
 * if you need to perform additional database operations.
 */
export const TestApiKeyFixture = Effect.gen(function* () {
  const envFixture = yield* TestEnvironmentFixture;
  const db = yield* Database;

  const apiKey = yield* db.organizations.projects.environments.apiKeys.create({
    userId: envFixture.owner.id,
    organizationId: envFixture.org.id,
    projectId: envFixture.project.id,
    environmentId: envFixture.environment.id,
    data: { name: "Test API Key" },
  });

  return {
    ...envFixture,
    apiKey,
  };
});

/**
 * Effect-native test fixture for spans.
 *
 * Creates a test span within an environment using the Effect-native
 * `Database` service.
 *
 * Reuses `TestEnvironmentFixture` to set up the organization, project, and environment.
 *
 * Returns all properties from TestEnvironmentFixture plus:
 * - traceId: the OTLP trace ID
 * - spanId: the OTLP span ID
 *
 * Requires Database - call `yield* Database` in your test
 * if you need to perform additional database operations.
 */
export const TestSpanFixture = Effect.gen(function* () {
  const envFixture = yield* TestEnvironmentFixture;
  const db = yield* Database;

  const traceId = "0123456789abcdef0123456789abcdef";
  const spanId = "0123456789abcdef";

  const result = yield* db.organizations.projects.environments.traces.create({
    userId: envFixture.owner.id,
    organizationId: envFixture.org.id,
    projectId: envFixture.project.id,
    environmentId: envFixture.environment.id,
    data: {
      resourceSpans: [
        {
          resource: {
            attributes: [
              { key: "service.name", value: { stringValue: "test-service" } },
            ],
          },
          scopeSpans: [
            {
              scope: { name: "test-scope" },
              spans: [
                {
                  traceId,
                  spanId,
                  name: "test-span",
                  kind: 1,
                  startTimeUnixNano: "1700000000000000000",
                  endTimeUnixNano: "1700000001000000000",
                  attributes: [],
                  status: {},
                },
              ],
            },
          ],
        },
      ],
    },
  });

  if (result.acceptedSpans !== 1) {
    throw new Error("Failed to create test span");
  }

  return {
    ...envFixture,
    traceId,
    spanId,
  };
});
