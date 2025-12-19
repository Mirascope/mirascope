import * as dotenv from "dotenv";
import { Effect, Layer } from "effect";
import { getDatabase, DatabaseService, type Database } from "@/db/services";
import type { PostgresJsDatabase } from "drizzle-orm/postgres-js";
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "@/db/schema";

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
