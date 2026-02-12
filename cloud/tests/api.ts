import {
  HttpClient,
  HttpApiClient,
  HttpClientRequest,
  HttpClientResponse,
  HttpApiBuilder,
  HttpServer,
} from "@effect/platform";
import {
  describe as vitestDescribe,
  it as vitestIt,
  expect,
  assert,
  beforeAll,
  afterAll,
} from "@effect/vitest";
import { eq } from "drizzle-orm";
import { Context, Effect, Layer, Option } from "effect";

import type { ModelPricing } from "@/api/router/pricing";
import type { ProviderName } from "@/api/router/providers";
import type { StreamMeteringContext } from "@/api/router/streaming";
import type { AuthResult } from "@/auth/context";
import type { PublicUser, PublicOrganization, ApiKeyInfo } from "@/db/schema";

import { Analytics } from "@/analytics";
import { MirascopeCloudApi, ApiLive } from "@/api/router";
import { AuthenticatedUser, Authentication } from "@/auth";
import { MockDeploymentService } from "@/claws/deployment/mock";
import { ClickHouse } from "@/db/clickhouse/client";
import { ClickHouseSearch } from "@/db/clickhouse/search";
import { DrizzleORM } from "@/db/client";
import { Database } from "@/db/database";
import { claws, users } from "@/db/schema";
import { Emails } from "@/emails";
import { Payments } from "@/payments";
import { executionContextLayer } from "@/server-entry";
import { Settings, type SettingsConfig } from "@/settings";
import { TEST_DATABASE_URL } from "@/tests/db";
import { getTestClickHouseConfig } from "@/tests/global-setup";
import { MockStripe } from "@/tests/payments";
import { createMockSettings, MockSettingsLayer } from "@/tests/settings";
import { createCustomIt, withRollback } from "@/tests/shared";
import { RealtimeSpans } from "@/workers/realtimeSpans";
import {
  SpansIngestQueue,
  type SpansIngestMessage,
} from "@/workers/spanIngestQueue";

// Re-export expect from vitest
export { expect, assert };

/**
 * Mock layer for Analytics that provides a no-op implementation for tests.
 */
const MockAnalytics = Layer.succeed(Analytics, {
  googleAnalytics: null as never,
  postHog: null as never,
  trackEvent: () => Effect.void,
  trackPageView: () => Effect.void,
  identify: () => Effect.void,
  initialize: () => Effect.void,
});

/**
 * Mock layer for Emails that provides a no-op implementation for tests.
 */
const MockEmails = Layer.succeed(Emails, {
  send: () => Effect.succeed({ id: "mock-email-id" }),
  audience: {
    add: () => Effect.succeed({ id: "mock-contact-id" }),
  },
});

// ============================================================================
// it.effect with automatic Database layer provision
// ============================================================================

/**
 * Creates a Database layer with MockPayments for testing.
 * Provides Database, DrizzleORM, and Payments services.
 */
const DefaultQueueLayer = Layer.succeed(SpansIngestQueue, {
  send: () => Effect.void,
});
export const DefaultRealtimeLayer = Layer.succeed(RealtimeSpans, {
  upsert: () => Effect.void,
  search: () => Effect.succeed({ spans: [], total: 0, hasMore: false }),
  getTraceDetail: () =>
    Effect.succeed({
      traceId: "",
      spans: [],
      rootSpanId: null,
      totalDurationMs: null,
    }),
  exists: () => Effect.succeed(false),
});

function createTestDatabaseLayer(
  connectionString: string,
  queueLayer: Layer.Layer<SpansIngestQueue> = DefaultQueueLayer,
  realtimeLayer: Layer.Layer<RealtimeSpans> = DefaultRealtimeLayer,
) {
  const drizzleLayer = DrizzleORM.layer({ connectionString }).pipe(Layer.orDie);

  // Provide Payments with MockStripe + drizzleLayer to avoid MockDrizzleORMLayer overriding real DB
  const paymentsLayer = Payments.Default.pipe(
    Layer.provide(MockStripe),
    Layer.provide(drizzleLayer),
  );

  return Layer.mergeAll(
    Database.Default.pipe(
      Layer.provide(drizzleLayer),
      Layer.provide(paymentsLayer),
    ).pipe(Layer.orDie),
    drizzleLayer,
    paymentsLayer,
    queueLayer,
    realtimeLayer,
    MockSettingsLayer(),
    MockAnalytics,
    MockEmails,
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
const customIt = createCustomIt<
  Database | Payments | DrizzleORM | Settings | Emails
>(wrapEffectTest);

/**
 * Type-safe `it` with `it.effect` and `it.rollback` for API tests.
 * - `it.effect` - Effect-based tests with automatic layer provision
 * - `it.rollback` - Effect-based tests that roll back database changes
 */
export const it = Object.assign(customIt, {
  rollback: <
    A,
    E,
    R extends Database | Payments | DrizzleORM | Settings | Emails,
  >(
    name: string,
    fn: () => Effect.Effect<A, E, R>,
    timeout?: number,
  ) => customIt.effect(name, () => fn().pipe(withRollback), timeout),
});

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
  apiKeyInfo: ApiKeyInfo,
  queueSend: (message: SpansIngestMessage) => Effect.Effect<void, Error>,
  realtimeLayer: Layer.Layer<RealtimeSpans> = DefaultRealtimeLayer,
) {
  // ClickHouse services layer for test environment
  const clickhouseConfig = getTestClickHouseConfig();
  const settings: SettingsConfig = createMockSettings({
    env: "test",
    clickhouse: {
      url: clickhouseConfig.url,
      user: clickhouseConfig.user,
      password: clickhouseConfig.password,
      database: clickhouseConfig.database,
      tls: {
        enabled: false,
        ca: "",
        skipVerify: false,
        hostnameVerify: true,
        minVersion: "1.2",
      },
    },
  });
  const settingsLayer = Layer.succeed(Settings, settings);
  const clickHouseSearchLayer = ClickHouseSearch.Default.pipe(
    Layer.provide(ClickHouse.Default),
    Layer.provide(settingsLayer),
  );

  const queueLayer = Layer.succeed(SpansIngestQueue, {
    send: queueSend ?? (() => Effect.void),
  });

  const services = Layer.mergeAll(
    settingsLayer,
    Layer.succeed(AuthenticatedUser, user),
    Layer.succeed(Authentication, { user, apiKeyInfo }),
    createTestDatabaseLayer(databaseUrl, queueLayer, realtimeLayer),
    clickHouseSearchLayer,
    MockAnalytics,
    MockEmails,
    MockDeploymentService,
    executionContextLayer,
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
  apiKeyInfo: ApiKeyInfo,
  queueSend: (message: SpansIngestMessage) => Effect.Effect<void, Error>,
  realtimeLayer: Layer.Layer<RealtimeSpans> = DefaultRealtimeLayer,
): Promise<{ client: ApiClient; dispose: () => Promise<void> }> {
  const webHandler = createTestWebHandler(
    databaseUrl,
    user,
    apiKeyInfo,
    queueSend,
    realtimeLayer,
  );
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

      // Create user, organization, and default API key context
      const { owner, org, apiKeyInfo } = await Effect.runPromise(
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

          const apiKeyInfo: ApiKeyInfo = {
            apiKeyId: "00000000-0000-0000-0000-000000000001",
            organizationId: org.id,
            projectId: "00000000-0000-0000-0000-000000000002",
            environmentId: "00000000-0000-0000-0000-000000000003",
            ownerId: owner.id,
            ownerEmail: owner.email,
            ownerName: owner.name,
            ownerAccountType: owner.accountType,
            ownerDeletedAt: owner.deletedAt,
            clawId: null,
          };

          return { owner, org, apiKeyInfo };
        }).pipe(Effect.provide(dbLayer)),
      );

      ownerRef = owner;
      orgRef = org;

      // Create API client authenticated as this user
      const result = await createApiClient(
        databaseUrl,
        owner,
        apiKeyInfo,
        () => Effect.void,
      );
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

            const client = yield* DrizzleORM;
            if (orgRef?.id) {
              // Collect bot user IDs before deleting the org (which cascades claws)
              const botUsers = yield* client
                .select({ botUserId: claws.botUserId })
                .from(claws)
                .where(eq(claws.organizationId, orgRef.id));

              // Delete organization (cascades to projects, memberships, claws)
              yield* db.organizations.delete({
                organizationId: orgRef.id,
                userId: ownerRef.id,
              });

              // Hard-delete bot users that were associated with this org's claws
              for (const { botUserId } of botUsers) {
                if (botUserId) {
                  yield* client.delete(users).where(eq(users.id, botUserId));
                }
              }
            }

            // Hard-delete owner to avoid polluting other tests with soft-deleted rows
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
  accountType: "user",
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
  const settings: SettingsConfig = createMockSettings({ env: "test" });
  const settingsLayer = Layer.succeed(Settings, settings);
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
    Layer.succeed(SpansIngestQueue, {
      send: () => Effect.void,
    }),
    Layer.succeed(RealtimeSpans, {
      upsert: () => Effect.void,
      search: () => Effect.succeed({ spans: [], total: 0, hasMore: false }),
      getTraceDetail: () =>
        Effect.succeed({
          traceId: "",
          spans: [],
          rootSpanId: null,
          totalDurationMs: null,
        }),
      exists: () => Effect.succeed(false),
    }),
    clickHouseSearchLayer,
    MockAnalytics,
    MockEmails,
    MockDeploymentService,
    executionContextLayer,
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
// Default mock pricing for tests (values in centi-cents per million tokens)
// Using large values so small token counts still produce non-zero costs
const defaultMockPricing: ModelPricing = {
  input: 150_000_000n, // Very high to ensure non-zero cost with small token counts
  output: 600_000_000n, // Very high to ensure non-zero cost with small token counts
};

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
        clawId: null,
      },
      response: {
        status: 200,
        statusText: "OK",
        headers: new Headers({ "content-type": "text/event-stream" }),
      },
      modelPricing: defaultMockPricing,
      ...overrides,
    };
  },
};
