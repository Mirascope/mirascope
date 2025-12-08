import { Effect, Layer } from "effect";
import { MirascopeCloudApi, ApiLive } from "@/api/router";
import {
  HttpClient,
  HttpApiClient,
  HttpClientRequest,
  HttpClientResponse,
  HttpApiBuilder,
  HttpServer,
} from "@effect/platform";
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "@/db/schema";
import { EnvironmentService } from "@/environment";
import { DatabaseService, getDatabase } from "@/db";
import { AuthenticatedUser } from "@/auth/context";
import type { PublicUser } from "@/db/schema";

// Mock authenticated user for tests
const mockUser: PublicUser = {
  id: "test-user-id",
  email: "test@example.com",
  name: "Test User",
};

// Note: For testing endpoints that don't require auth/db, we still provide
// mock services because the Layer types require them to be satisfied.
function createTestWebHandler(options: {
  environment?: string;
  databaseUrl?: string;
  authenticatedUser?: PublicUser;
}) {
  // Always provide all services to satisfy type requirements
  // Individual endpoints may not use all services
  const DependenciesLive = Layer.mergeAll(
    Layer.succeed(EnvironmentService, {
      env: options.environment || "test",
    }),
    Layer.succeed(
      DatabaseService,
      // Use a dummy database URL for tests that don't actually hit the DB
      getDatabase(
        options.databaseUrl || "postgresql://test:test@localhost/test",
      ),
    ),
    Layer.succeed(AuthenticatedUser, options.authenticatedUser || mockUser),
  );

  const ApiWithDependencies = Layer.mergeAll(
    HttpServer.layerContext,
    ApiLive.pipe(Layer.provide(DependenciesLive)),
  );

  return HttpApiBuilder.toWebHandler(ApiWithDependencies);
}

/**
 * Create a test web handler with a specific database instance and user.
 * Used for transaction-based tests.
 */
function createTestWebHandlerWithDb(
  db: ReturnType<typeof getDatabase>,
  user: PublicUser,
) {
  const DependenciesLive = Layer.mergeAll(
    Layer.succeed(EnvironmentService, { env: "test" }),
    Layer.succeed(DatabaseService, db),
    Layer.succeed(AuthenticatedUser, user),
  );

  const ApiWithDependencies = Layer.mergeAll(
    HttpServer.layerContext,
    ApiLive.pipe(Layer.provide(DependenciesLive)),
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

function createTestClient(options?: {
  authenticatedUser?: PublicUser;
  databaseUrl?: string;
}) {
  const webHandler = createTestWebHandler({
    environment: "test",
    authenticatedUser: options?.authenticatedUser ?? mockUser,
    databaseUrl: options?.databaseUrl,
  });
  const HandlerHttpClient = createHandlerHttpClient(webHandler);
  const HandlerHttpClientLayer = Layer.succeed(
    HttpClient.HttpClient,
    HandlerHttpClient,
  );

  return Effect.runSync(
    Effect.scoped(
      HttpApiClient.make(MirascopeCloudApi, {
        // NOTE: no prefix here because we're testing with the web handler directly (no prefix handling required)
        baseUrl: "http://127.0.0.1:3000/",
      }).pipe(Effect.provide(HandlerHttpClientLayer)),
    ),
  );
}

function createTestClientWithDb(
  db: ReturnType<typeof getDatabase>,
  user: PublicUser,
) {
  const webHandler = createTestWebHandlerWithDb(db, user);
  const HandlerHttpClient = createHandlerHttpClient(webHandler);
  const HandlerHttpClientLayer = Layer.succeed(
    HttpClient.HttpClient,
    HandlerHttpClient,
  );

  return Effect.runSync(
    Effect.scoped(
      HttpApiClient.make(MirascopeCloudApi, {
        baseUrl: "http://127.0.0.1:3000/",
      }).pipe(Effect.provide(HandlerHttpClientLayer)),
    ),
  );
}

export type TestClient = ReturnType<typeof createTestClient>;

/**
 * Test helper for simple tests that don't require a real database.
 * Uses mock services.
 */
export const withTestClient = (
  testFn: (client: TestClient) => void | Promise<void>,
  options?: {
    authenticatedUser?: PublicUser;
    databaseUrl?: string;
  },
) => {
  return async () => {
    const client = createTestClient(options);
    await testFn(client);
  };
};

/**
 * Test helper that wraps API tests in a database transaction that rolls back.
 * Creates the specified number of users/clients (defaults to 1).
 *
 * @param num - Number of test clients to create (each with their own user)
 * @returns A function that takes a test callback and returns an async test function
 *
 * @example
 * // Single client (default)
 * it("test name", withApiClient()(async ([client]) => {
 *   // test with single client
 * }));
 *
 * @example
 * // Multiple clients for permission testing
 * it("test name", withApiClient(2)(async ([client1, client2]) => {
 *   // test with two clients
 * }));
 */
export const withApiClient =
  (num: number = 1) =>
  (
    testFn: (clients: TestClient[]) => void | Promise<void>,
  ): (() => Promise<void>) => {
    return async (): Promise<void> => {
      const TEST_DATABASE_URL = process.env.TEST_DATABASE_URL;
      if (!TEST_DATABASE_URL) {
        throw new Error("TEST_DATABASE_URL environment variable is required.");
      }

      const sql = postgres(TEST_DATABASE_URL, { max: 5, fetch_types: false });
      const db = drizzle(sql, { schema });

      await db
        .transaction(async (tx) => {
          const txDb = getDatabase(tx);

          const clients: TestClient[] = [];
          for (let i = 0; i < num; i++) {
            const user = await Effect.runPromise(
              txDb.users.create({
                email: `user${i + 1}@example.com`,
                name: `User ${i + 1}`,
              }),
            );
            clients.push(createTestClientWithDb(txDb, user));
          }

          await testFn(clients);
          throw new Error("__ROLLBACK_TEST_DB__");
        })
        .catch((err: unknown) => {
          if (
            err &&
            typeof err === "object" &&
            "message" in err &&
            err.message !== "__ROLLBACK_TEST_DB__"
          ) {
            throw err;
          }
        });
    };
  };
