import { Context, Effect, Layer, Config, Option } from "effect";
import { it as vitestIt, describe, expect, assert } from "@effect/vitest";
import { DrizzleORM, type DrizzleORMClient } from "@/db/client";
import { Database } from "@/db";
import { PgClient } from "@effect/sql-pg";
import { SqlClient } from "@effect/sql";
import { CONNECTION_FILE } from "@/tests/global-setup";
import { Stripe } from "@/payments";
import fs from "fs";

// Re-export describe and expect for convenience
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
 * Builder for creating mock Stripe layers that mirrors the Stripe API structure.
 *
 * @example Mock with static values
 * ```ts
 * const mockStripe = new MockStripe()
 *   .customers.create({ id: "cus_123", email: "test@example.com", ... })
 *   .build();
 * ```
 *
 * @example Mock with function (for spying or dynamic values)
 * ```ts
 * const createSpy = vi.fn();
 * const mockStripe = new MockStripe()
 *   .customers.create((params) => {
 *     createSpy(params);
 *     return { id: "cus_123", email: params.email, ... };
 *   })
 *   .build();
 * ```
 *
 * @example Mock multiple methods
 * ```ts
 * const mockStripe = new MockStripe()
 *   .customers.create({ id: "cus_123", ... })
 *   .customers.del({ id: "cus_123", deleted: true })
 *   .build();
 * ```
 */
export class MockStripe {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private createCustomerResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private deleteCustomerResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private createSubscriptionResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private listCreditGrantsResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private configResult?: any;

  /**
   * Stripe customers resource mock.
   */
  get customers() {
    return {
      /**
       * Mock `customers.create()` - accepts either a static value or a function.
       */
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      create: (result: any) => {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        this.createCustomerResult = result;
        return this;
      },
      /**
       * Mock `customers.del()` - accepts either a static value or a function.
       */
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      del: (result: any) => {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        this.deleteCustomerResult = result;
        return this;
      },
    };
  }

  /**
   * Stripe subscriptions resource mock.
   */
  get subscriptions() {
    return {
      /**
       * Mock `subscriptions.create()` - accepts either a static value or a function.
       */
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      create: (result: any) => {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        this.createSubscriptionResult = result;
        return this;
      },
    };
  }

  /**
   * Stripe billing resource mock.
   */
  get billing() {
    return {
      creditGrants: {
        /**
         * Mock `billing.creditGrants.list()` - accepts either a static value or a function.
         */
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        list: (result: any) => {
          // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
          this.listCreditGrantsResult = result;
          return this;
        },
      },
    };
  }

  /**
   * Mock Stripe config - accepts a config object.
   */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  config(result: any) {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    this.configResult = result;
    return this;
  }

  /**
   * Builds a Layer<Stripe> with the configured mocks.
   */
  build(): Layer.Layer<Stripe> {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const createCustomerResult = this.createCustomerResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const deleteCustomerResult = this.deleteCustomerResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const createSubscriptionResult = this.createSubscriptionResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const listCreditGrantsResult = this.listCreditGrantsResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const configResult = this.configResult;

    return Layer.succeed(Stripe, {
      customers: {
        create: (params: {
          email?: string;
          name?: string;
          metadata?: Record<string, string>;
        }) => {
          if (createCustomerResult !== undefined) {
            // If it's a function, call it with params
            if (typeof createCustomerResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-call
              return Effect.succeed(createCustomerResult(params));
            }
            // Otherwise return the static value
            return Effect.succeed(createCustomerResult);
          }

          // Default implementation
          return Effect.succeed({
            id: `cus_mock_${crypto.randomUUID()}`,
            object: "customer" as const,
            created: Date.now(),
            livemode: false,
            email: params.email || null,
            name: params.name || null,
            metadata: params.metadata || {},
          });
        },
        del: (id: string) => {
          if (deleteCustomerResult !== undefined) {
            // If it's a function, call it with id
            if (typeof deleteCustomerResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-call
              return Effect.succeed(deleteCustomerResult(id));
            }
            // Otherwise return the static value
            return Effect.succeed(deleteCustomerResult);
          }

          // Default implementation
          return Effect.succeed({
            id,
            object: "customer" as const,
            deleted: true,
          });
        },
      },
      subscriptions: {
        create: (params: {
          customer: string;
          items: Array<{ price: string }>;
          metadata?: Record<string, string>;
        }) => {
          if (createSubscriptionResult !== undefined) {
            // If it's a function, call it with params
            if (typeof createSubscriptionResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-call
              return Effect.succeed(createSubscriptionResult(params));
            }
            // Otherwise return the static value
            return Effect.succeed(createSubscriptionResult);
          }

          // Default implementation
          return Effect.succeed({
            id: `sub_mock_${crypto.randomUUID()}`,
            object: "subscription" as const,
            created: Date.now(),
            customer: params.customer,
            items: {
              object: "list" as const,
              data: params.items.map((item) => ({
                id: `si_mock_${crypto.randomUUID()}`,
                object: "subscription_item" as const,
                price: { id: item.price },
              })),
            },
            status: "active" as const,
            metadata: params.metadata || {},
          });
        },
      },
      billing: {
        creditGrants: {
          list: () => {
            if (listCreditGrantsResult !== undefined) {
              // If it's a function, call it
              if (typeof listCreditGrantsResult === "function") {
                // eslint-disable-next-line @typescript-eslint/no-unsafe-call
                return Effect.succeed(listCreditGrantsResult());
              }
              // Otherwise return the static value
              return Effect.succeed(listCreditGrantsResult);
            }

            // Default implementation
            return Effect.succeed({
              object: "list" as const,
              data: [
                // Valid grant #1: USD, router price - SHOULD BE COUNTED ($7)
                {
                  amount: {
                    monetary: {
                      value: 700, // $7.00 in cents
                      currency: "usd",
                    },
                  },
                  applicability_config: {
                    scope: {
                      prices: [
                        { id: "price_test_mock_for_testing" },
                        { id: "price_other" },
                      ],
                    },
                  },
                },
                // Valid grant #2: USD, router price - SHOULD BE COUNTED ($11)
                {
                  amount: {
                    monetary: {
                      value: 1100, // $11.00 in cents
                      currency: "usd",
                    },
                  },
                  applicability_config: {
                    scope: {
                      prices: [{ id: "price_test_mock_for_testing" }],
                    },
                  },
                },
                // Invalid: EUR currency - should NOT be counted
                {
                  amount: {
                    monetary: {
                      value: 500, // €5.00 in cents
                      currency: "eur",
                    },
                  },
                  applicability_config: {
                    scope: {
                      prices: [{ id: "price_test_mock_for_testing" }],
                    },
                  },
                },
                // Invalid: No monetary amount - should NOT be counted
                {
                  amount: {},
                  applicability_config: {
                    scope: {
                      prices: [{ id: "price_test_mock_for_testing" }],
                    },
                  },
                },
                // Invalid: Different price - should NOT be counted
                {
                  amount: {
                    monetary: {
                      value: 1900, // $19.00 in cents
                      currency: "usd",
                    },
                  },
                  applicability_config: {
                    scope: {
                      prices: [{ id: "price_different" }],
                    },
                  },
                },
                // Invalid: No scope - should NOT be counted
                {
                  amount: {
                    monetary: {
                      value: 2300, // $23.00 in cents
                      currency: "usd",
                    },
                  },
                  applicability_config: {},
                },
              ],
              has_more: false,
            });
          },
        },
      },
      // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
      config: configResult ?? {
        apiKey: "sk_test_mock",
        routerPriceId: "price_test_mock_for_testing",
      },
    } as unknown as Context.Tag.Service<typeof Stripe>);
  }
}

/**
 * Default MockStripe layer for tests that don't need spies.
 */
export const DefaultMockStripe = new MockStripe().build();

/**
 * A Layer that provides the Effect-native `Database`, `DrizzleORM`, and
 * `SqlClient` services for tests.
 *
 * Note: This layer is automatically provided by `it.effect` from this module,
 * and tests are automatically wrapped in a transaction that rolls back.
 * You only need to import this if you need to provide it manually (e.g., in
 * tests that don't use `it.effect`).
 */
export const TestDatabase: Layer.Layer<
  Database | DrizzleORM | SqlClient.SqlClient
> = Database.Default.pipe(
  Layer.provideMerge(TestDrizzleORM),
  Layer.provide(DefaultMockStripe),
);

// =============================================================================
// Rollback transaction wrapper
// =============================================================================

// Sentinel error used to force transaction rollback
class TestRollbackError {
  readonly _tag = "TestRollbackError";
}

/**
 * Wraps a test effect in a transaction that always rolls back.
 *
 * If SqlClient is not available (e.g., mock tests), the effect runs
 * without transaction wrapping.
 */
const withRollback = <A, E, R>(
  effect: Effect.Effect<A, E, R>,
): Effect.Effect<A, E, R> =>
  Effect.gen(function* () {
    // Check if SqlClient is available (won't be for mock tests)
    const sqlOption = yield* Effect.serviceOption(SqlClient.SqlClient);

    if (Option.isNone(sqlOption)) {
      // No SqlClient available (mock test), run without transaction
      return yield* effect;
    }

    const sql = sqlOption.value;
    let result: A;

    yield* sql
      .withTransaction(
        Effect.gen(function* () {
          // Run the test effect and capture its result
          result = yield* effect;
          // Always fail to trigger rollback
          return yield* Effect.fail(new TestRollbackError());
        }),
      )
      .pipe(
        // Catch the rollback error - this is expected
        Effect.catchIf(
          (e): e is TestRollbackError => e instanceof TestRollbackError,
          () => Effect.void,
        ),
      );

    // @ts-expect-error - result is assigned before we get here
    return result;
  }) as Effect.Effect<A, E, R>;

// =============================================================================
// Type-safe test utilities with automatic layer provision
// =============================================================================

/**
 * Services that are automatically provided to all `it.effect` tests.
 */
export type TestServices = Database | DrizzleORM | SqlClient.SqlClient;

/**
 * Type for effect test functions that accept TestServices as dependencies.
 */
type EffectTestFn = <A, E>(
  name: string,
  fn: () => Effect.Effect<A, E, TestServices>,
  timeout?: number,
) => void;

/**
 * Wraps a test function to automatically provide TestDatabase
 * and wrap in a transaction that rolls back.
 */

const wrapEffectTest =
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (original: any): EffectTestFn =>
    (name, fn, timeout) => {
      // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-return
      return original(
        name,
        () => withRollback(fn()).pipe(Effect.provide(TestDatabase)),
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
// Create a callable `it` that works as both:
// - it("test name", () => { ... }) for regular tests
// - it.effect("test name", () => Effect.gen(...)) for Effect tests
export const it = Object.assign(
  // Base callable function for regular tests
  ((name: string, fn: () => void) => vitestIt(name, fn)) as typeof vitestIt,
  {
    // Spread all properties from vitestIt (skip, only, etc.)
    ...vitestIt,
    // Override effect with our wrapped version
    effect: Object.assign(wrapEffectTest(vitestIt.effect), {
      skip: wrapEffectTest(vitestIt.effect.skip),
      only: wrapEffectTest(vitestIt.effect.only),
      fails: wrapEffectTest(vitestIt.effect.fails),
      skipIf: (condition: unknown) =>
        wrapEffectTest(vitestIt.effect.skipIf(condition)),
      runIf: (condition: unknown) =>
        wrapEffectTest(vitestIt.effect.runIf(condition)),
    }),
  },
);

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
  private insertResults: MockEffectResult[] = [];
  private updateResults: MockEffectResult[] = [];
  private deleteResults: MockEffectResult[] = [];

  select(result: MockEffectResult): this {
    this.selectResults.push(result);
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
   * Builds a Layer<Database> with the mocked DrizzleORM and optional custom Stripe layer.
   *
   * @param stripeLayer - Optional custom Stripe layer. If not provided, uses DefaultMockStripe.
   */
  build(stripeLayer?: Layer.Layer<Stripe>): Layer.Layer<Database> {
    let selectIndex = 0;
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
    const createChainableProxy = (
      results: MockEffectResult[],
      index: number,
    ): unknown => {
      const effect = makeEffect(results, index);

      return new Proxy(
        {},
        {
          get: (_, prop) => {
            if (prop === "pipe") {
              // At .pipe(), apply the given transformations to the effect
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              return (...fns: Array<(e: any) => any>) => {
                // eslint-disable-next-line @typescript-eslint/no-unsafe-return
                return fns.reduce((acc, fn) => fn(acc), effect);
              };
            }
            // For any other method, return a function that returns the proxy (chainable)
            return () => createChainableProxy(results, index);
          },
        },
      );
    };

    const drizzleMock = {
      select: () => {
        const idx = selectIndex++;
        return createChainableProxy(this.selectResults, idx);
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
    return Database.Default.pipe(
      Layer.provide(mockDrizzleORMLayer),
      Layer.provide(stripeLayer ?? DefaultMockStripe),
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
