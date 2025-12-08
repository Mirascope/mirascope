import { Effect, Layer } from "effect";
import { AuthService, createAuthService } from "@/auth/service";
import { DatabaseService, getDatabase } from "@/db";
import { EnvironmentService, getEnvironment } from "@/environment";

// TODO: figure out weird type errors around `EnvironmentService` being an error typed value
export type AppServices = EnvironmentService | DatabaseService | AuthService;

export function runHandler<A, E>(
  effect: Effect.Effect<A, E, AppServices>,
): Promise<A> {
  // Create all services fresh for each request to ensure they're created
  // within the correct request context (required for Cloudflare Workers)
  const environmentLayer = Layer.succeed(EnvironmentService, getEnvironment());

  const databaseUrl = process.env.DATABASE_URL;
  if (!databaseUrl) {
    throw new Error("DATABASE_URL environment variable is not set");
  }
  const databaseLayer = Layer.succeed(
    DatabaseService,
    getDatabase(databaseUrl),
  );

  const authLayer = Layer.succeed(AuthService, createAuthService());

  const appServicesLayer = Layer.mergeAll(
    environmentLayer,
    databaseLayer,
    authLayer,
  );

  return effect.pipe(
    Effect.tapError((error) =>
      Effect.sync(() => {
        console.error("[Effect Handler] Error:", error);
      }),
    ),
    Effect.provide(appServicesLayer),
    Effect.runPromise,
  );
}
