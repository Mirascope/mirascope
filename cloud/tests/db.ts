import { Config, Context, Effect, Layer, Option } from "effect";
import { describe, expect } from "@effect/vitest";
import { createCustomIt } from "@/tests/shared";
import { DrizzleORM, type DrizzleORMClient } from "@/db/client";
import { Database } from "@/db";
import { PgClient } from "@effect/sql-pg";
import { SqlClient } from "@effect/sql";
import {
  CONNECTION_FILE,
  CLICKHOUSE_CONNECTION_FILE,
} from "@/tests/global-setup";
import { Payments } from "@/payments";
import { DefaultMockPayments } from "@/tests/payments";
import {
  SpansIngestQueue,
  ingestSpansMessage,
  type SpansIngestMessage,
} from "@/workers/spanIngestQueue";
import { RealtimeSpans } from "@/workers/realtimeSpans";
import {
  MockRealtimeSpansLayer,
  createRealtimeSpansLayer,
} from "@/tests/workers/realtimeSpans";
import { ClickHouse } from "@/db/clickhouse/client";
import { ClickHouseSearch } from "@/db/clickhouse/search";
import { SettingsService, getSettings } from "@/settings";
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

type ClickHouseConnectionFile = {
  url: string;
  user: string;
  password: string;
  database: string;
  nativePort: number;
};

function getTestClickHouseConfig(): ClickHouseConnectionFile {
  try {
    const raw = fs.readFileSync(CLICKHOUSE_CONNECTION_FILE, "utf-8");
    return JSON.parse(raw) as ClickHouseConnectionFile;
  } catch {
    throw new Error(
      "TEST_CLICKHOUSE_URL not set. Ensure global-setup.ts ran successfully.",
    );
  }
}

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
 * A Layer that provides the Effect-native `Database`, `DrizzleORM`, and
 * `SqlClient` services for tests.
 *
 * Note: This layer is automatically provided by `it.effect` from this module,
 * and tests are automatically wrapped in a transaction that rolls back.
 * You only need to import this if you need to provide it manually (e.g., in
 * tests that don't use `it.effect`).
 */
/**
 * Test ClickHouse layer using the real test container.
 */
const TestClickHouse = Effect.sync(() => {
  const config = getTestClickHouseConfig();
  const settings = getSettings();
  const settingsLayer = Layer.succeed(SettingsService, {
    ...settings,
    env: "test",
    CLICKHOUSE_URL: config.url,
    CLICKHOUSE_USER: config.user,
    CLICKHOUSE_PASSWORD: config.password,
    CLICKHOUSE_DATABASE: config.database,
  });
  return ClickHouse.Default.pipe(Layer.provide(settingsLayer));
}).pipe(Layer.unwrapEffect);

export { createRealtimeSpansLayer, MockRealtimeSpansLayer };

type ClickHouseSearchService = Context.Tag.Service<ClickHouseSearch>;

const defaultClickHouseSearchService: ClickHouseSearchService = {
  search: () => Effect.succeed({ spans: [], total: 0, hasMore: false }),
  getTraceDetail: () =>
    Effect.succeed({
      traceId: "",
      spans: [],
      rootSpanId: null,
      totalDurationMs: null,
    }),
  getAnalyticsSummary: () =>
    Effect.succeed({
      totalSpans: 0,
      avgDurationMs: null,
      p50DurationMs: null,
      p95DurationMs: null,
      p99DurationMs: null,
      errorRate: 0,
      totalTokens: 0,
      totalCostUsd: 0,
      topModels: [],
      topFunctions: [],
    }),
};

/**
 * Creates a mock ClickHouseSearch layer with optional overrides.
 */
export const createClickHouseSearchLayer = (
  overrides: Partial<ClickHouseSearchService> = {},
): Layer.Layer<ClickHouseSearch> =>
  Layer.succeed(ClickHouseSearch, {
    ...defaultClickHouseSearchService,
    ...overrides,
  });

/**
 * Default mock ClickHouseSearch layer for tests.
 */
export const MockClickHouseSearchLayer = createClickHouseSearchLayer();

/**
 * SpansIngestQueue layer that synchronously executes ingestSpansMessage.
 * Uses real TestClickHouse and MockRealtimeSpans (Durable Object is external).
 */
const TestSpansIngestQueue = Layer.succeed(SpansIngestQueue, {
  send: (message: SpansIngestMessage) =>
    ingestSpansMessage(message).pipe(
      Effect.provide(Layer.merge(TestClickHouse, MockRealtimeSpansLayer)),
      Effect.catchAll(() => Effect.void),
    ),
});

export const TestDatabase: Layer.Layer<
  | Database
  | DrizzleORM
  | SqlClient.SqlClient
  | ClickHouseSearch
  | SpansIngestQueue
  | RealtimeSpans
> = Effect.gen(function* () {
  // Lazy import to avoid circular dependency
  const { DefaultMockPayments } = yield* Effect.promise(
    () => import("@/tests/payments"),
  );

  // ClickHouse layer from Docker container config
  const clickhouseConfig = getTestClickHouseConfig();
  const settingsLayer = Layer.succeed(SettingsService, {
    env: "test",
    CLICKHOUSE_URL: clickhouseConfig.url,
    CLICKHOUSE_USER: clickhouseConfig.user,
    CLICKHOUSE_PASSWORD: clickhouseConfig.password,
    CLICKHOUSE_DATABASE: clickhouseConfig.database,
  });
  const clickHouseSearchLayer = ClickHouseSearch.Default.pipe(
    Layer.provide(ClickHouse.Default),
    Layer.provide(settingsLayer),
  );

  return Layer.mergeAll(
    Database.Default.pipe(
      Layer.provideMerge(TestDrizzleORM),
      Layer.provide(DefaultMockPayments),
    ),
    TestSpansIngestQueue,
    MockRealtimeSpansLayer,
    clickHouseSearchLayer,
  );
}).pipe(Layer.unwrapEffect);

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
export const withRollback = <A, E, R>(
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
export type TestServices =
  | Database
  | DrizzleORM
  | SqlClient.SqlClient
  | ClickHouseSearch
  | SpansIngestQueue;

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
const baseIt = createCustomIt<TestServices>(wrapEffectTest);

/**
 * Type-safe `it` with `it.effect` that automatically:
 * 1. Wraps tests in a transaction that rolls back
 * 2. Provides TestDatabase layer
 */
export const it = baseIt;

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
    return Database.Default.pipe(
      Layer.provide(mockDrizzleORMLayer),
      Layer.provide(paymentsLayer ?? DefaultMockPayments),
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
 * Returns a test span identifier within an environment for ClickHouse/DurableObjects
 * integration paths.
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

  const traceId = "0123456789abcdef0123456789abcdef";
  const spanId = "0123456789abcdef";

  return {
    ...envFixture,
    traceId,
    spanId,
  };
});
