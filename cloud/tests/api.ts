import {
  describe as vitestDescribe,
  it as vitestIt,
  expect,
  beforeAll,
  afterAll,
} from "@effect/vitest";
import { createCustomIt } from "@/tests/shared";
import { Context, Effect, Layer, Option } from "effect";
import { MirascopeCloudApi, ApiLive } from "@/api/router";
import {
  HttpClient,
  HttpApiClient,
  HttpClientRequest,
  HttpClientResponse,
  HttpApiBuilder,
  HttpServer,
} from "@effect/platform";
import { SettingsService, getSettings } from "@/settings";
import { Database } from "@/db";
import { DrizzleORM } from "@/db/client";
import { Payments } from "@/payments";
import { AuthenticatedUser, Authentication } from "@/auth";
import { ClickHouse } from "@/clickhouse/client";
import { ClickHouseSearch } from "@/clickhouse/search";
import type { AuthResult } from "@/auth/context";
import type { PublicUser, PublicOrganization, ApiKeyInfo } from "@/db/schema";
import { users } from "@/db/schema";
import { TEST_DATABASE_URL } from "@/tests/db";
import { DefaultMockPayments } from "@/tests/payments";
import type { StreamMeteringContext } from "@/api/router/streaming";
import type { ProviderName } from "@/api/router/providers";
import { eq } from "drizzle-orm";
import { CLICKHOUSE_CONNECTION_FILE } from "@/tests/global-setup";
import { SpansMeteringQueueService } from "@/workers/spansMeteringQueue";
import { SqlClient } from "@effect/sql";
import fs from "fs";

// Re-export expect from vitest
export { expect };

// ============================================================================
// it.effect with automatic Database layer provision
// ============================================================================

/**
 * Mock layer for SpansMeteringQueueService that suppresses queue operations in tests.
 */
const MockSpansMeteringQueue = Layer.succeed(
  SpansMeteringQueueService,
  SpansMeteringQueueService.of({
    send: () => Effect.succeed(undefined), // No-op in tests
  }),
);

// =============================================================================
// Rollback transaction wrapper (from @/tests/db)
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

/**
 * Creates a Database layer with MockPayments for testing.
 * Provides Database, Payments, DrizzleORM, SqlClient, and SpansMeteringQueueService.
 */
function createTestDatabaseLayer(connectionString: string) {
  const drizzleLayer = DrizzleORM.layer({ connectionString }).pipe(Layer.orDie);
  return Layer.mergeAll(
    Database.Default.pipe(
      Layer.provide(drizzleLayer),
      Layer.provide(DefaultMockPayments),
    ).pipe(Layer.orDie),
    drizzleLayer,
    DefaultMockPayments,
    MockSpansMeteringQueue,
  );
}

/**
 * Layer that provides Database for API handler tests.
 */
const TestDatabaseLayer = createTestDatabaseLayer(TEST_DATABASE_URL);

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
 * Wraps a test function to automatically provide Database and Payments layers.
 *
 * Takes a test function that requires Database | Payments, automatically provides
 * those dependencies via TestDatabaseLayer, resulting in an effect compatible with
 * @effect/vitest's expectations.
 */
const wrapEffectTest =
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (original: any) =>
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (name: any, fn: any, timeout?: any) => {
      // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-return
      return original(
        name,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-return, @typescript-eslint/no-unnecessary-type-assertion
        () => (fn() as any).pipe(Effect.provide(TestDatabaseLayer)),
        timeout,
      );
    };

/**
 * Wraps a test function to automatically provide Database layers AND wrap in rollback transaction.
 *
 * Like wrapEffectTest but also wraps the test in a transaction that rolls back,
 * ensuring test isolation and cleanup.
 */
const wrapEffectTestWithRollback =
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (original: any) =>
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (name: any, fn: any, timeout?: any) => {
      // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-return
      return original(
        name,
        () =>
          // eslint-disable-next-line @typescript-eslint/no-unsafe-return, @typescript-eslint/no-unsafe-call
          fn()
            // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
            .pipe(withRollback)
            // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
            .pipe(Effect.provide(TestDatabaseLayer)),
        timeout,
      );
    };

/**
 * Type-safe `it` with `it.effect` and `it.rollback` for API tests.
 *
 * Works as a regular `it` for synchronous tests, and provides:
 * - `it.effect` for Effect-based tests with automatic Database layer provision
 * - `it.rollback` for Effect-based tests that also wrap in a transaction rollback
 *
 * @example
 * ```ts
 * import { describe, it, expect } from "@/tests/api";
 * import { Effect } from "effect";
 *
 * describe("MyComponent", () => {
 *   // Regular synchronous test
 *   it("does something", () => {
 *     expect(true).toBe(true);
 *   });
 *
 *   // Effect-based test with auto-provided Database
 *   it.effect("handles requests", () =>
 *     Effect.gen(function* () {
 *       const db = yield* Database;
 *       // ... test code
 *     })
 *   );
 *
 *   // Effect-based test with rollback (for test isolation)
 *   it.rollback("creates user without polluting DB", () =>
 *     Effect.gen(function* () {
 *       const db = yield* Database;
 *       const user = yield* db.users.create({ ... });
 *       // User will be rolled back after test
 *     })
 *   );
 * });
 * ```
 */
export const it = Object.assign(
  createCustomIt<
    | Database
    | Payments
    | SpansMeteringQueueService
    | DrizzleORM
    | SqlClient.SqlClient
  >(wrapEffectTest),
  {
    rollback: Object.assign(wrapEffectTestWithRollback(vitestIt.effect), {
      skip: wrapEffectTestWithRollback(vitestIt.effect.skip),
      only: wrapEffectTestWithRollback(vitestIt.effect.only),
      fails: wrapEffectTestWithRollback(vitestIt.effect.fails),
      skipIf: (condition: unknown) =>
        wrapEffectTestWithRollback(vitestIt.effect.skipIf(condition)),
      runIf: (condition: unknown) =>
        wrapEffectTestWithRollback(vitestIt.effect.runIf(condition)),
    }),
  },
);

// ============================================================================
// API Client Creation
// ============================================================================

const makeClient = HttpApiClient.make(MirascopeCloudApi, {
  baseUrl: "http://127.0.0.1:3000/",
});
type ApiClient = Effect.Effect.Success<typeof makeClient>;

function createTestWebHandler(
  databaseUrl: string,
  user: PublicUser,
  apiKeyInfo?: ApiKeyInfo,
) {
  // ClickHouse services layer for test environment
  const clickhouseConfig = getTestClickHouseConfig();
  const settings = getSettings();
  const settingsLayer = Layer.succeed(SettingsService, {
    ...settings,
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

  const services = Layer.mergeAll(
    settingsLayer,
    Layer.succeed(AuthenticatedUser, user),
    Layer.succeed(Authentication, { user, apiKeyInfo }),
    createTestDatabaseLayer(databaseUrl),
    DrizzleORM.layer({ connectionString: databaseUrl }).pipe(Layer.orDie),
    clickHouseSearchLayer,
  );

  const ApiWithDependencies = Layer.merge(
    HttpServer.layerContext,
    ApiLive,
  ).pipe(Layer.provide(services));

  return HttpApiBuilder.toWebHandler(ApiWithDependencies);
}

function createHandlerHttpClient(
  webHandler: ReturnType<typeof createTestWebHandler>,
) {
  return HttpClient.make((request: HttpClientRequest.HttpClientRequest) =>
    Effect.gen(function* () {
      const url = Option.getOrElse(
        HttpClientRequest.toUrl(request),
        () => new URL(request.url),
      );
      const method = request.method.toUpperCase();
      const options: RequestInit = {
        method: request.method,
        headers: request.headers,
      };

      if (method !== "GET" && method !== "HEAD" && request.body !== undefined) {
        options.body = (request.body.toJSON() as { body: BodyInit }).body;
      }

      const webResponse = yield* Effect.promise(() =>
        webHandler.handler(new Request(url.toString(), options)),
      );

      return HttpClientResponse.fromWeb(request, webResponse);
    }),
  );
}

export async function createApiClient(
  databaseUrl: string,
  user: PublicUser,
  apiKeyInfo?: ApiKeyInfo,
): Promise<{ client: ApiClient; dispose: () => Promise<void> }> {
  const webHandler = createTestWebHandler(databaseUrl, user, apiKeyInfo);
  const HandlerHttpClient = createHandlerHttpClient(webHandler);
  const HandlerHttpClientLayer = Layer.succeed(
    HttpClient.HttpClient,
    HandlerHttpClient,
  );

  const client = await Effect.runPromise(
    makeClient.pipe(Effect.provide(HandlerHttpClientLayer), Effect.scoped),
  );

  return {
    client,
    dispose: () => webHandler.dispose(),
  };
}

// ============================================================================
// Sequential Test Utilities
// ============================================================================

/**
 * Context provided to sequential API tests via Effect dependency injection.
 *
 * Use `yield* TestApiContext` inside `it.effect` tests to access the client,
 * owner, and organization fixtures.
 */
export class TestApiContext extends Context.Tag("TestApiContext")<
  TestApiContext,
  {
    /** API client authenticated as owner */
    client: ApiClient;
    /** The user the client is authenticated as */
    owner: PublicUser;
    /** An organization owned by owner */
    org: PublicOrganization;
  }
>() {}

/**
 * Custom it interface for sequential tests with TestApiContext auto-provided.
 */
interface SequentialIt {
  effect: <E>(
    name: string,
    testFn: () => Effect.Effect<void, E, TestApiContext>,
  ) => void;
}

/**
 * Sequential test wrapper for API tests.
 *
 * Creates a user, organization, and authenticated API client before tests run.
 * Cleans up by deleting the organization and user after all tests complete.
 *
 * The callback receives a scoped `it` with `it.effect` that auto-provides
 * the `TestApiContext` layer. Use `yield* TestApiContext` to access fixtures.
 *
 * @example
 * ```ts
 * import { describe, expect, TestApiContext } from "@/tests/api";
 *
 * describe.sequential("Organizations API", (it) => {
 *   let org: PublicOrganizationWithMembership;
 *
 *   it.effect("POST /organizations - create", () =>
 *     Effect.gen(function* () {
 *       const { client } = yield* TestApiContext;
 *       org = yield* client.organizations.create({
 *         payload: { name: "New Org" },
 *       });
 *       expect(org.name).toBe("New Org");
 *     }),
 *   );
 * });
 * ```
 */
function createSequentialDescribe(
  name: string,
  fn: (it: SequentialIt) => void,
) {
  vitestDescribe.sequential(name, () => {
    let testLayer: Layer.Layer<TestApiContext>;
    let dispose: (() => Promise<void>) | null = null;
    let databaseUrl: string;
    let ownerRef: PublicUser;
    let orgRef: PublicOrganization;

    beforeAll(async () => {
      databaseUrl = TEST_DATABASE_URL;

      // Create database layer for setup operations
      const dbLayer = createTestDatabaseLayer(databaseUrl);

      // Create user and organization
      const { owner, org } = await Effect.runPromise(
        Effect.gen(function* () {
          const db = yield* Database;

          // Create test user
          const owner = yield* db.users.create({
            data: {
              email: `api-test-${Date.now()}@example.com`,
              name: "API Test User",
            },
          });

          // Create test organization
          const org = yield* db.organizations.create({
            userId: owner.id,
            data: {
              name: "API Test Organization",
              slug: "api-test-organization",
            },
          });

          return { owner, org };
        }).pipe(Effect.provide(dbLayer)),
      );

      ownerRef = owner;
      orgRef = org;

      // Create API client authenticated as this user
      const result = await createApiClient(databaseUrl, owner);
      dispose = result.dispose;

      // Create the layer that tests will use
      testLayer = Layer.succeed(TestApiContext, {
        client: result.client,
        owner,
        org,
      });
    });

    afterAll(async () => {
      // Dispose API client
      if (dispose) {
        await dispose();
      }

      // Clean up database - delete org first (cascades), then user
      if (ownerRef?.id) {
        const dbLayer = Layer.merge(
          createTestDatabaseLayer(databaseUrl),
          DrizzleORM.layer({ connectionString: databaseUrl }).pipe(Layer.orDie),
        );

        await Effect.runPromise(
          Effect.gen(function* () {
            const db = yield* Database;

            // Delete organization (cascades to projects, memberships)
            if (orgRef?.id) {
              yield* db.organizations.delete({
                organizationId: orgRef.id,
                userId: ownerRef.id,
              });
            }

            // Hard-delete user to avoid polluting other tests with soft-deleted rows
            const client = yield* DrizzleORM;
            yield* client.delete(users).where(eq(users.id, ownerRef.id));
          }).pipe(Effect.provide(dbLayer)),
        );
      }
    });

    // Create custom it.effect that auto-provides the TestApiContext layer
    const scopedIt: SequentialIt = {
      effect: (testName, testFn) =>
        vitestIt.effect(testName, () =>
          testFn().pipe(Effect.provide(testLayer)),
        ),
    };

    fn(scopedIt);
  });
}

// Custom describe object with our sequential method
interface CustomDescribe {
  (name: string, fn: () => void): void;
  sequential: typeof createSequentialDescribe;
  skip: typeof vitestDescribe.skip;
  only: typeof vitestDescribe.only;
}

export const describe: CustomDescribe = Object.assign(
  (name: string, fn: () => void) => vitestDescribe(name, fn),
  {
    sequential: createSequentialDescribe,
    skip: vitestDescribe.skip,
    only: vitestDescribe.only,
  },
);

// ============================================================================
// Simple Test Client (for tests that don't need database fixtures)
// ============================================================================

const mockUser: PublicUser = {
  id: "test-user-id",
  email: "test@example.com",
  name: "Test User",
  deletedAt: null,
};

/**
 * Context.Tag for the test API client.
 */
export class TestApiClient extends Context.Tag("TestApiClient")<
  TestApiClient,
  ApiClient
>() {}

/**
 * Creates a simple web handler with mock user and database for simple API tests.
 */
function createSimpleTestWebHandler() {
  const databaseUrl = TEST_DATABASE_URL;
  const authResult: AuthResult = { user: mockUser };

  // ClickHouse services layer for test environment
  const settings = getSettings();
  const settingsLayer = Layer.succeed(SettingsService, {
    ...settings,
    env: "test",
  });
  const clickHouseClientLayer = ClickHouse.Default.pipe(
    Layer.provide(settingsLayer),
  );
  const clickHouseSearchLayer = ClickHouseSearch.Default.pipe(
    Layer.provide(clickHouseClientLayer),
  );

  const services = Layer.mergeAll(
    settingsLayer,
    Layer.succeed(AuthenticatedUser, mockUser),
    Layer.succeed(Authentication, authResult),
    createTestDatabaseLayer(databaseUrl).pipe(Layer.orDie),
    DrizzleORM.layer({ connectionString: databaseUrl }).pipe(Layer.orDie),
    clickHouseSearchLayer,
  );

  const ApiWithDependencies = Layer.mergeAll(
    HttpServer.layerContext,
    ApiLive.pipe(Layer.provide(services)),
  );

  return HttpApiBuilder.toWebHandler(ApiWithDependencies);
}

/**
 * Test client utilities for simple API testing (health, docs, traces, etc.)
 *
 * For tests that don't need database fixtures:
 * ```ts
 * Effect.gen(function* () {
 *   const client = yield* TestApiClient;
 *   const result = yield* client.health.check();
 * }).pipe(Effect.provide(TestClient.Default))
 * ```
 */
export const TestClient = {
  /**
   * Self-contained layer with mock user and test database.
   * Use for simple tests that don't need specific database fixtures.
   */
  Default: Layer.scoped(
    TestApiClient,
    Effect.gen(function* () {
      const webHandler = createSimpleTestWebHandler();
      const HandlerHttpClient = createHandlerHttpClient(webHandler);
      const HandlerHttpClientLayer = Layer.succeed(
        HttpClient.HttpClient,
        HandlerHttpClient,
      );

      const client = yield* makeClient.pipe(
        Effect.provide(HandlerHttpClientLayer),
        Effect.scoped,
      );

      yield* Effect.addFinalizer(() =>
        Effect.promise(() => webHandler.dispose()),
      );

      return client;
    }),
  ),
};

// ============================================================================
// Mock Metering Context for Router Tests
// ============================================================================

/**
 * Factory for creating mock StreamMeteringContext objects in router tests.
 *
 * Provides a consistent way to create metering contexts without manually spreading
 * or overriding properties.
 *
 * @example
 * ```ts
 * const context = MockMeteringContext.fromProvider("openai", "gpt-4");
 * const customContext = MockMeteringContext.fromProvider("anthropic", "claude-3-opus", {
 *   reservationId: "custom_res_123",
 * });
 * ```
 */
export const MockMeteringContext = {
  fromProvider(
    provider: ProviderName,
    model: string,
    overrides?: Partial<StreamMeteringContext>,
  ): StreamMeteringContext {
    return {
      provider,
      modelId: model,
      reservationId: "res_test123",
      request: {
        userId: "user_test123",
        organizationId: "org_test123",
        projectId: "proj_test123",
        environmentId: "env_test123",
        apiKeyId: "key_test123",
        routerRequestId: "req_test123",
      },
      response: {
        status: 200,
        statusText: "OK",
        headers: new Headers({ "content-type": "text/event-stream" }),
      },
      ...overrides,
    };
  },
};
