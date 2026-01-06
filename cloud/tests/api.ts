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
import { ClickHouseSearchService } from "@/clickhouse/search";
import type { AuthResult } from "@/auth/context";
import type { PublicUser, PublicOrganization, ApiKeyInfo } from "@/db/schema";
import { users } from "@/db/schema";
import { TEST_DATABASE_URL, DefaultMockPayments } from "@/tests/db";
import { eq } from "drizzle-orm";

// Re-export expect from vitest
export { expect };

// ============================================================================
// it.effect with automatic Database layer provision
// ============================================================================

/**
 * Creates a Database layer with MockPayments for testing.
 * Provides both Database and Payments services.
 */
function createTestDatabaseLayer(connectionString: string) {
  return Layer.mergeAll(
    Database.Default.pipe(
      Layer.provide(DrizzleORM.layer({ connectionString }).pipe(Layer.orDie)),
      Layer.provide(DefaultMockPayments),
    ).pipe(Layer.orDie),
    DefaultMockPayments,
  );
}

/**
 * Layer that provides Database for API handler tests.
 */
const TestDatabaseLayer = createTestDatabaseLayer(TEST_DATABASE_URL);

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
 * Type-safe `it` with `it.effect` that automatically provides Database.
 *
 * Works as a regular `it` for synchronous tests, and provides `it.effect`
 * for Effect-based tests with automatic Database layer provision.
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
 * });
 * ```
 */
export const it = createCustomIt<Database | Payments>(wrapEffectTest);

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
  const settings = getSettings();
  const settingsLayer = Layer.succeed(SettingsService, {
    ...settings,
    env: "test",
  });
  const clickHouseClientLayer = ClickHouse.Default.pipe(
    Layer.provide(settingsLayer),
  );
  const clickHouseSearchLayer = ClickHouseSearchService.Default.pipe(
    Layer.provide(clickHouseClientLayer),
  );

  const services = Layer.mergeAll(
    settingsLayer,
    Layer.succeed(AuthenticatedUser, user),
    Layer.succeed(Authentication, { user, apiKeyInfo }),
    createTestDatabaseLayer(databaseUrl),
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
  const clickHouseSearchLayer = ClickHouseSearchService.Default.pipe(
    Layer.provide(clickHouseClientLayer),
  );

  const services = Layer.mergeAll(
    settingsLayer,
    Layer.succeed(AuthenticatedUser, mockUser),
    Layer.succeed(Authentication, authResult),
    createTestDatabaseLayer(databaseUrl).pipe(Layer.orDie),
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
