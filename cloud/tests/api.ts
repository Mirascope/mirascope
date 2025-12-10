import {
  describe as vitestDescribe,
  expect,
  beforeAll,
  afterAll,
} from "vitest";
import { it as vitestIt } from "@effect/vitest";
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
import { SettingsService } from "@/settings";
import { Database } from "@/db";
import { AuthenticatedUser, AuthenticatedApiKey } from "@/auth";
import type { PublicUser, PublicOrganization, ApiKeyInfo } from "@/db/schema";
import { TEST_DATABASE_URL } from "@/tests/db";

// Re-export expect from vitest
export { expect };

// ============================================================================
// it.effect with automatic Database layer provision
// ============================================================================

/**
 * Layer that provides Database for API handler tests.
 */
const TestDatabaseLayer = Database.Live({
  connectionString: TEST_DATABASE_URL,
}).pipe(Layer.orDie);

/**
 * Type for effect test functions that accept Database as dependency.
 */
type EffectTestFn = <A, E>(
  name: string,
  fn: () => Effect.Effect<A, E, Database>,
  timeout?: number,
) => void;

/**
 * Wraps a test function to automatically provide Database layer.
 */
const wrapEffectTest =
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (original: any): EffectTestFn =>
    (name, fn, timeout) => {
      // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-return
      return original(
        name,
        () => fn().pipe(Effect.provide(TestDatabaseLayer)),
        timeout,
      );
    };

/**
 * Type-safe `it` with `it.effect` that automatically provides Database.
 *
 * Use this for API handler tests that need database access.
 *
 * @example
 * ```ts
 * import { describe, it, expect } from "@/tests/api";
 * import { Effect } from "effect";
 * import { handleRequest } from "@/api/handler";
 *
 * describe("handleRequest", () => {
 *   it.effect("handles requests", () =>
 *     Effect.gen(function* () {
 *       const result = yield* handleRequest(req, options);
 *       expect(result.matched).toBe(true);
 *     })
 *   );
 * });
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
// API Client Creation
// ============================================================================

const makeClient = HttpApiClient.make(MirascopeCloudApi, {
  baseUrl: "http://127.0.0.1:3000/",
});
type ApiClient = Effect.Effect.Success<typeof makeClient>;

function createTestWebHandler(
  databaseUrl: string,
  authenticatedUser: PublicUser,
  authenticatedApiKey?: ApiKeyInfo,
) {
  const baseServices = Layer.mergeAll(
    Layer.succeed(SettingsService, { env: "test" }),
    Layer.succeed(AuthenticatedUser, authenticatedUser),
    Database.Live({ connectionString: databaseUrl }).pipe(Layer.orDie),
  );
  const apiKeyLayer = authenticatedApiKey
    ? Layer.succeed(AuthenticatedApiKey, authenticatedApiKey)
    : Layer.empty;
  const services = Layer.merge(baseServices, apiKeyLayer);

  const ApiWithDependencies = Layer.merge(
    HttpServer.layerContext,
    ApiLive,
  ).pipe(Layer.provide(services));

  // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-argument
  return HttpApiBuilder.toWebHandler(ApiWithDependencies as any);
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
  authenticatedUser: PublicUser,
  authenticatedApiKey?: ApiKeyInfo,
): Promise<{ client: ApiClient; dispose: () => Promise<void> }> {
  const webHandler = createTestWebHandler(
    databaseUrl,
    authenticatedUser,
    authenticatedApiKey,
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
      const dbLayer = Database.Live({ connectionString: databaseUrl });

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
        const dbLayer = Database.Live({ connectionString: databaseUrl });

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

            // Delete user
            yield* db.users.delete({ userId: ownerRef.id });
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

  // Simple services
  const simpleServices = Layer.mergeAll(
    Layer.succeed(SettingsService, { env: "test" }),
    Layer.succeed(AuthenticatedUser, mockUser),
  );

  // Database layer
  const dbLayer = Database.Live({ connectionString: databaseUrl }).pipe(
    Layer.orDie,
  );

  const allServices = Layer.merge(simpleServices, dbLayer);

  const ApiWithDependencies = Layer.mergeAll(
    HttpServer.layerContext,
    ApiLive.pipe(Layer.provide(allServices)),
  );

  // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-argument
  return HttpApiBuilder.toWebHandler(ApiWithDependencies as any);
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
