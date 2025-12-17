import * as dotenv from "dotenv";
import { Context, Effect, Layer } from "effect";
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
import { DatabaseService, getDatabase, type Database } from "@/db";
import { AuthenticatedUser } from "@/auth";
import type { App } from "@/api/handler";
import type { PublicUser } from "@/db/schema";
import { TestDatabase } from "@/tests/db";

dotenv.config({ path: ".env.local", override: true });

const mockUser: PublicUser = {
  id: "test-user-id",
  email: "test@example.com",
  name: "Test User",
  deletedAt: null,
};

const testDatabaseUrl = "postgresql://test:test@localhost/test";

function createTestWebHandler(app: App) {
  const services = Layer.mergeAll(
    Layer.succeed(SettingsService, { env: app.environment }),
    Layer.succeed(DatabaseService, app.database),
    Layer.succeed(AuthenticatedUser, app.authenticatedUser),
  );

  const ApiWithDependencies = Layer.mergeAll(
    HttpServer.layerContext,
    ApiLive.pipe(Layer.provide(services)),
  );

  return HttpApiBuilder.toWebHandler(ApiWithDependencies);
}

function createHandlerHttpClient(
  webHandler: ReturnType<typeof createTestWebHandler>,
) {
  return HttpClient.make((request: HttpClientRequest.HttpClientRequest) =>
    Effect.gen(function* () {
      const url = new URL(request.url);
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

const makeClient = HttpApiClient.make(MirascopeCloudApi, {
  baseUrl: "http://127.0.0.1:3000/",
});
type ApiClient = Effect.Effect.Success<typeof makeClient>;

function createApiClient(
  database: Database,
  authenticatedUser: PublicUser,
): Effect.Effect<
  { client: ApiClient; dispose: () => Promise<void> },
  never,
  never
> {
  return Effect.gen(function* () {
    const app: App = {
      environment: "test",
      database,
      authenticatedUser,
    };

    const webHandler = createTestWebHandler(app);
    const HandlerHttpClient = createHandlerHttpClient(webHandler);
    const HandlerHttpClientLayer = Layer.succeed(
      HttpClient.HttpClient,
      HandlerHttpClient,
    );

    const client = yield* makeClient.pipe(
      Effect.provide(HandlerHttpClientLayer),
      Effect.scoped,
    );

    return {
      client,
      dispose: () => webHandler.dispose(),
    };
  });
}

// ============================================================================
// Effect-based API testing utilities
// ============================================================================

/**
 * Context.Tag for the test API client.
 */
export class TestApiClient extends Context.Tag("TestApiClient")<
  TestApiClient,
  ApiClient
>() {}

/**
 * Test client utilities for API testing.
 *
 * For simple tests without database (health, docs, traces):
 * ```ts
 * Effect.gen(function* () {
 *   const client = yield* TestApiClient;
 *   const result = yield* client.health.check();
 * }).pipe(Effect.provide(TestClient.Default))
 * ```
 *
 * For tests with fixtures that need a specific authenticated user:
 * ```ts
 * Effect.gen(function* () {
 *   const { owner, org } = yield* TestOrganizationFixture;
 *   const client = yield* TestClient.authenticate(owner);
 *   const orgs = yield* client.organizations.list();
 * }).pipe(Effect.provide(TestDatabase))
 * ```
 *
 * For tests that just need an authenticated user (no specific fixtures):
 * ```ts
 * Effect.gen(function* () {
 *   const client = yield* TestApiClient;
 *   const org = yield* client.organizations.create({ ... });
 * }).pipe(Effect.provide(TestClient.Authenticated))
 * ```
 */
export const TestClient = {
  /**
   * Self-contained layer with mock user and mock database.
   * Use for simple tests that don't need real database interactions.
   */
  Default: Layer.scoped(
    TestApiClient,
    Effect.gen(function* () {
      const database = getDatabase(testDatabaseUrl);

      const { client, dispose } = yield* createApiClient(database, mockUser);

      yield* Effect.addFinalizer(() =>
        Effect.promise(async () => {
          await dispose();
          await database.close();
        }),
      );

      return client;
    }),
  ),

  /**
   * Creates an authenticated API client for a specific user.
   * Requires DatabaseService from context (use with TestDatabase).
   *
   * @param user - The user to authenticate as
   * @returns Effect that yields the authenticated API client
   */
  authenticate: (
    user: PublicUser,
  ): Effect.Effect<ApiClient, never, DatabaseService> =>
    Effect.gen(function* () {
      const database = yield* DatabaseService;
      const { client } = yield* createApiClient(database, user);
      return client;
    }),

  /**
   * Layer that provides an authenticated client with a newly created test user.
   * Self-contained - includes TestDatabase internally.
   */
  Authenticated: Layer.scoped(
    TestApiClient,
    Effect.gen(function* () {
      const database = yield* DatabaseService;
      const user = yield* database.users.create({
        data: { email: "api-test@example.com", name: "API Test User" },
      });
      const { client, dispose } = yield* createApiClient(database, user);
      yield* Effect.addFinalizer(() => Effect.promise(dispose));
      return client;
    }),
  ).pipe(Layer.provide(TestDatabase), Layer.orDie),
};
