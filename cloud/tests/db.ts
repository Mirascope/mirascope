import * as dotenv from "dotenv";
import { Effect, Layer, Config, Option } from "effect";
import { it as vitestIt, describe, expect } from "@effect/vitest";
import { getDatabase, DatabaseService, type Database } from "@/db/services";
import { DrizzleORM, type DrizzleORMClient } from "@/db/client";
import { EffectDatabase } from "@/db/database";
import { PgClient } from "@effect/sql-pg";
import { SqlClient } from "@effect/sql";
import type { PostgresJsDatabase } from "drizzle-orm/postgres-js";
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "@/db/schema";
import {
  organizations,
  organizationMemberships,
  organizationMembershipAudit,
} from "@/db/schema";

// Re-export describe and expect for convenience
export { describe, expect };

dotenv.config({ path: ".env.local", override: true });

if (!process.env.TEST_DATABASE_URL) {
  throw new Error(
    "TEST_DATABASE_URL environment variable is required. Please set it in your .env file.",
  );
}

const TEST_DATABASE_URL: string = process.env.TEST_DATABASE_URL;

/**
 * A scoped Layer that provides a DatabaseService backed by a transaction that
 * automatically rolls back when the test completes. This ensures test isolation
 * without polluting the database.
 *
 * Usage with @effect/vitest:
 * ```ts
 * import { it } from "@effect/vitest";
 * import { Effect } from "effect";
 * import { DatabaseService } from "@/db/services";
 * import { TestDatabase } from "@/tests/db";
 *
 * it.effect("should do something", () =>
 *   Effect.gen(function* () {
 *     const db = yield* DatabaseService;
 *     // ... test code
 *   }).pipe(Effect.provide(TestDatabase))
 * );
 * ```
 */
export const TestDatabase: Layer.Layer<DatabaseService> = Layer.scoped(
  DatabaseService,
  Effect.gen(function* () {
    const sql = postgres(TEST_DATABASE_URL, {
      max: 5,
      fetch_types: false,
    });
    const db = drizzle(sql, { schema });

    // Create promise-based coordination for the transaction lifecycle
    let resolveReady!: (database: Database) => void;
    let resolveComplete!: () => void;

    const readyPromise = new Promise<Database>((resolve) => {
      resolveReady = resolve;
    });
    const completePromise = new Promise<void>((resolve) => {
      resolveComplete = resolve;
    });

    // Start the transaction - it will wait for completePromise before rolling back
    const transactionPromise = db
      .transaction(async (tx) => {
        const txDb = getDatabase(tx);
        resolveReady(txDb);
        // Wait for the test to complete
        await completePromise;
        // Always throw to trigger rollback
        throw new Error("__ROLLBACK_TEST_DB__");
      })
      .catch((err: unknown) => {
        // Only suppress the rollback error; propagate all other errors
        if (
          err &&
          typeof err === "object" &&
          "message" in err &&
          err.message !== "__ROLLBACK_TEST_DB__"
        ) {
          throw err;
        }
      })
      .finally(() => {
        void sql.end();
      });

    // Wait for the transaction to be ready and the database to be available
    const database = yield* Effect.promise(() => readyPromise);

    // Add finalizer to signal completion and wait for rollback
    yield* Effect.addFinalizer(() =>
      Effect.promise(() => {
        resolveComplete();
        return transactionPromise;
      }),
    );

    return database;
  }),
);

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
 * A Layer that provides the Effect-native `EffectDatabase`, `DrizzleORM`, and
 * `SqlClient` services for tests.
 *
 * Note: This layer is automatically provided by `it.effect` from this module,
 * and tests are automatically wrapped in a transaction that rolls back.
 * You only need to import this if you need to provide it manually (e.g., in
 * tests that don't use `it.effect`).
 */
export const TestEffectDatabase: Layer.Layer<
  EffectDatabase | DrizzleORM | SqlClient.SqlClient
> = EffectDatabase.Default.pipe(Layer.provideMerge(TestDrizzleORM));

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
export type TestServices = EffectDatabase | DrizzleORM | SqlClient.SqlClient;

/**
 * Type for effect test functions that accept TestServices as dependencies.
 */
type EffectTestFn = <A, E>(
  name: string,
  fn: () => Effect.Effect<A, E, TestServices>,
  timeout?: number,
) => void;

/**
 * Wraps a test function to automatically provide TestEffectDatabase
 * and wrap in a transaction that rolls back.
 */
 
const wrapEffectTest =
  (original: any): EffectTestFn =>
  (name, fn, timeout) => {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-return
    return original(
      name,
      () => withRollback(fn()).pipe(Effect.provide(TestEffectDatabase)),
      timeout,
    );
  };

/**
 * Type-safe `it` with `it.effect` that automatically:
 * 1. Wraps tests in a transaction that rolls back
 * 2. Provides TestEffectDatabase layer
 *
 * Use this instead of importing directly from @effect/vitest.
 *
 * @example
 * ```ts
 * import { it, expect } from "@/tests/db";
 * import { Effect } from "effect";
 * import { EffectDatabase } from "@/db/database";
 *
 * it.effect("creates a user", () =>
 *   Effect.gen(function* () {
 *     const db = yield* EffectDatabase;
 *     const user = yield* db.users.create({ data: { email: "test@example.com" } });
 *     expect(user.email).toBe("test@example.com");
 *   })
 * );
 * ```
 */
export const it = {
  ...vitestIt,
  effect: Object.assign(wrapEffectTest(vitestIt.effect), {
    skip: wrapEffectTest(vitestIt.effect.skip),
    only: wrapEffectTest(vitestIt.effect.only),
    fails: wrapEffectTest(vitestIt.effect.fails),
    skipIf: (condition: unknown) =>
      wrapEffectTest(vitestIt.effect.skipIf(condition)),
    runIf: (condition: unknown) =>
      wrapEffectTest(vitestIt.effect.runIf(condition)),
  }),
};

// ============================================================================
// Mock database builder
// ============================================================================

type MockResult = unknown[] | Error;

/**
 * Builder for creating mock databases with sequenced responses.
 *
 * Each call to select/insert/update/delete adds a response to a queue.
 * When the mock is used, responses are returned in order. Pass an array
 * for success, or an Error for failure.
 *
 * Example:
 * ```ts
 * const db = new MockDatabase()
 *   .select([{ role: "OWNER" }])           // 1st select succeeds
 *   .select(new Error("Connection lost"))  // 2nd select fails
 *   .build();
 *
 * const result = yield* db.projects.findById(...);
 * ```
 */
export class MockDatabase {
  private selectResults: MockResult[] = [];
  private insertResults: MockResult[] = [];
  private updateResults: MockResult[] = [];
  private deleteResults: MockResult[] = [];

  select(result: MockResult): this {
    this.selectResults.push(result);
    return this;
  }

  insert(result: MockResult): this {
    this.insertResults.push(result);
    return this;
  }

  update(result: MockResult): this {
    this.updateResults.push(result);
    return this;
  }

  delete(result: MockResult): this {
    this.deleteResults.push(result);
    return this;
  }

  build(): Database {
    let selectIndex = 0;
    let insertIndex = 0;
    let updateIndex = 0;
    let deleteIndex = 0;

    const makePromise = (
      results: MockResult[],
      index: number,
    ): Promise<unknown[]> => {
      const result = results[index];
      if (result === undefined) {
        return Promise.reject(new Error("No more mocked responses"));
      }
      if (result instanceof Error) {
        return Promise.reject(result);
      }
      return Promise.resolve(result);
    };

    // Create a terminal promise handler that works for all chain patterns
    const createTerminal = (results: MockResult[], getIndex: () => number) => {
      const promise = makePromise(results, getIndex());
      return {
        limit: () => promise,
        then: promise.then.bind(promise),
        catch: promise.catch.bind(promise),
      };
    };

    const drizzleMock = {
      select: () => {
        const idx = selectIndex++;
        return {
          from: () => {
            const terminal = createTerminal(this.selectResults, () => idx);
            return {
              where: () => terminal,
              innerJoin: () => ({
                where: () => terminal,
              }),
              limit: terminal.limit,
              then: terminal.then,
              catch: terminal.catch,
            };
          },
        };
      },
      insert: () => {
        const idx = insertIndex++;
        const promise = makePromise(this.insertResults, idx);
        return {
          values: () => ({
            onConflictDoUpdate: () => promise,
            returning: () => promise,
          }),
        };
      },
      update: () => {
        const idx = updateIndex++;
        const promise = makePromise(this.updateResults, idx);
        return {
          set: () => ({
            where: () => ({
              returning: () => promise,
            }),
          }),
        };
      },
      delete: () => {
        const idx = deleteIndex++;
        const promise = makePromise(this.deleteResults, idx);
        return {
          where: () => ({
            returning: () => promise,
            then: promise.then.bind(promise),
            catch: promise.catch.bind(promise),
          }),
        };
      },
    } as unknown as PostgresJsDatabase<typeof schema>;

    return getDatabase(drizzleMock);
  }
}

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
   * Builds a Layer<EffectDatabase> with the mocked DrizzleORM.
   */
  build(): Layer.Layer<EffectDatabase> {
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
    return EffectDatabase.Default.pipe(Layer.provide(mockDrizzleORMLayer));
  }
}

// ============================================================================
// Test fixture effects
// ============================================================================

/**
 * Creates a test organization with members of all roles and a non-member user.
 *
 * Returns { org, owner, admin, member, nonMember } where:
 * - owner: a user who owns the organization (OWNER role)
 * - admin: a user with ADMIN role
 * - member: a user with MEMBER role
 * - nonMember: a user who is NOT a member (useful for permission tests)
 *
 * Requires DatabaseService - call `yield* DatabaseService` in your test
 * if you need to perform additional database operations.
 */
export const TestOrganizationFixture = Effect.gen(function* () {
  const db = yield* DatabaseService;

  // Create users
  const owner = yield* db.users.create({
    data: { email: "owner@example.com", name: "Owner" },
  });

  const admin = yield* db.users.create({
    data: { email: "admin@example.com", name: "Admin" },
  });

  const member = yield* db.users.create({
    data: { email: "member@example.com", name: "Member" },
  });

  const nonMember = yield* db.users.create({
    data: { email: "nonmember@example.com", name: "Non Member" },
  });

  // Create organization (owner becomes OWNER automatically)
  const org = yield* db.organizations.create({
    data: { name: "Test Organization" },
    userId: owner.id,
  });

  // Add members with different roles using the memberships service
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
 * Effect-native test fixture for organizations.
 *
 * Creates a test organization with members of all roles and a non-member user
 * using the Effect-native `EffectDatabase` service.
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
 * Requires EffectDatabase - call `yield* EffectDatabase` in your test
 * if you need to perform additional database operations.
 */
export const TestEffectOrganizationFixture = Effect.gen(function* () {
  const db = yield* EffectDatabase;
  const client = yield* DrizzleORM;

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

  // Create organization directly (OrganizationService not yet migrated)
  const [org] = yield* client
    .insert(organizations)
    .values({ name: `Test Organization` })
    .returning({ id: organizations.id, name: organizations.name })
    .pipe(
      Effect.mapError(
        (e) => new Error(`Failed to create organization: ${String(e)}`),
      ),
    );

  // Create OWNER membership for the owner
  yield* client
    .insert(organizationMemberships)
    .values({
      memberId: owner.id,
      organizationId: org.id,
      role: "OWNER",
    })
    .pipe(
      Effect.mapError(
        (e) => new Error(`Failed to create owner membership: ${String(e)}`),
      ),
    );

  // Log audit for OWNER membership
  yield* client
    .insert(organizationMembershipAudit)
    .values({
      organizationId: org.id,
      actorId: owner.id,
      targetId: owner.id,
      action: "GRANT",
      newRole: "OWNER",
    })
    .pipe(
      Effect.mapError(
        (e) => new Error(`Failed to create audit log: ${String(e)}`),
      ),
    );

  // Add members with different roles using Effect-native memberships service
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
 * Creates a test project within an organization with explicit project members.
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
 * Note: Project members must already be org members (TODO: external collaborators).
 *
 * TODO: Refactor to use db.projects.create() and db.projects.memberships once ProjectService is implemented.
 */
export const TestProjectFixture = Effect.gen(function* () {
  const orgFixture = yield* TestOrganizationFixture;
  const db = yield* DatabaseService;

  // Create project through the ProjectService (creator gets project ADMIN automatically).
  const project = yield* db.organizations.projects.create({
    userId: orgFixture.owner.id,
    organizationId: orgFixture.org.id,
    data: { name: "Test Project" },
  });

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
