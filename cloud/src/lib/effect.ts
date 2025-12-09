import { Effect, Layer } from "effect";
import { AuthService, createAuthService } from "@/auth/service";
import { DatabaseService, getDatabase } from "@/db";
import { EnvironmentService, getEnvironment } from "@/environment";

// TODO: figure out weird type errors around `EnvironmentService` being an error typed value
export type AppServices = EnvironmentService | DatabaseService | AuthService;

export async function runHandler<A, E>(
  effect: Effect.Effect<A, E, AppServices>,
): Promise<A> {
  const environmentLayer = Layer.succeed(EnvironmentService, getEnvironment());

  const databaseUrl = process.env.DATABASE_URL;
  if (!databaseUrl) {
    throw new Error("DATABASE_URL environment variable is not set");
  }

  const database = getDatabase(databaseUrl);
  const databaseLayer = Layer.succeed(DatabaseService, database);
  const authLayer = Layer.succeed(AuthService, createAuthService());

  const appServicesLayer = Layer.mergeAll(
    environmentLayer,
    databaseLayer,
    authLayer,
  );

  try {
    return await effect.pipe(
      Effect.tapError((error) =>
        Effect.sync(() => {
          console.error("[Effect Handler] Error:", error);
        }),
      ),
      Effect.provide(appServicesLayer),
      Effect.runPromise,
    );
  } finally {
    await database.close();
  }
}
