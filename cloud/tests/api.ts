import * as dotenv from "dotenv";
import { Effect, Layer } from "effect";
import { beforeAll, afterAll } from "vitest";
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
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
import * as schema from "@/db/schema";
import type { PublicUser } from "@/db/schema";

dotenv.config({ path: ".env.local", override: true });

const mockUser: PublicUser = {
  id: "test-user-id",
  email: "test@example.com",
  name: "Test User",
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

export const withTestClientDb = (
  testFn: (
    client: TestClient,
    context: { user: PublicUser },
  ) => void | Promise<void>,
) => {
  return async () => {
    const TEST_DATABASE_URL = process.env.TEST_DATABASE_URL;
    if (!TEST_DATABASE_URL) {
      throw new Error(
        "TEST_DATABASE_URL environment variable is required for database tests",
      );
    }

    const sql = postgres(TEST_DATABASE_URL, { max: 5, fetch_types: false });
    const db = drizzle(sql, { schema });

    try {
      await db
        .transaction(async (tx) => {
          const txDb = getDatabase(tx);

          const [user] = await tx
            .insert(schema.users)
            .values({ email: "api-test@example.com", name: "API Test User" })
            .returning({
              id: schema.users.id,
              email: schema.users.email,
              name: schema.users.name,
            });

          const { client, cleanup } = createTestClient({
            database: txDb,
            authenticatedUser: user,
          });

          try {
            await testFn(client, { user });
          } finally {
            await cleanup();
          }
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
    } finally {
      await sql.end();
    }
  };
};
