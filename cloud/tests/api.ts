import { Effect, Layer } from "effect";
import { beforeAll, afterAll } from "vitest";
import { MirascopeCloudApi, ApiLive } from "@/api/router";
import {
  HttpClient,
  HttpApiClient,
  HttpClientRequest,
  HttpClientResponse,
  HttpApiBuilder,
  HttpServer,
} from "@effect/platform";
import { EnvironmentService } from "@/environment";
import { DatabaseService, getDatabase, type Database } from "@/db";
import { AuthenticatedUser } from "@/auth";
import type { App } from "@/api/handler";
import type { PublicUser } from "@/db/schema";

const mockUser: PublicUser = {
  id: "test-user-id",
  email: "test@example.com",
  name: "Test User",
};

const testDatabaseUrl = "postgresql://test:test@localhost/test";

function createTestWebHandler(app: App) {
  const services = Layer.mergeAll(
    Layer.succeed(EnvironmentService, { env: app.environment }),
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

function createTestClient(options?: {
  authenticatedUser?: PublicUser;
  database?: Database;
}) {
  const database = options?.database ?? getDatabase(testDatabaseUrl);
  const app: App = {
    environment: "test",
    database,
    authenticatedUser: options?.authenticatedUser ?? mockUser,
  };

  const webHandler = createTestWebHandler(app);
  const HandlerHttpClient = createHandlerHttpClient(webHandler);
  const HandlerHttpClientLayer = Layer.succeed(
    HttpClient.HttpClient,
    HandlerHttpClient,
  );

  const client = Effect.runSync(
    Effect.scoped(
      HttpApiClient.make(MirascopeCloudApi, {
        baseUrl: "http://127.0.0.1:3000/",
      }).pipe(Effect.provide(HandlerHttpClientLayer)),
    ),
  );

  const cleanup = async () => {
    await webHandler.dispose();
    // Only close if we created the database connection
    if (!options?.database) {
      await database.close();
    }
  };

  return { client, cleanup };
}

export type TestClient = ReturnType<typeof createTestClient>["client"];

/**
 * Wraps a describe block callback with a shared test client.
 * Uses vitest's beforeAll/afterAll hooks for proper resource lifecycle.
 *
 * @example
 * describe("Health API", withTestClient((client) => {
 *   it("GET /health", async () => {
 *     const result = await Effect.runPromise(client.health.check());
 *     expect(result.status).toBe("ok");
 *   });
 * }));
 */
export const withTestClient = (
  testFn: (client: TestClient) => void,
  options?: {
    authenticatedUser?: PublicUser;
    database?: Database;
  },
) => {
  return () => {
    let client: TestClient;
    let cleanup: () => Promise<void>;

    beforeAll(() => {
      const result = createTestClient(options);
      client = result.client;
      cleanup = result.cleanup;
    });

    afterAll(async () => {
      await cleanup();
    });

    // Use a getter to access the client lazily (after beforeAll runs)
    testFn(
      new Proxy({} as TestClient, {
        get: (_, prop) => {
          return (client as Record<string | symbol, unknown>)[prop];
        },
      }),
    );
  };
};
