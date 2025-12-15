import { Effect, Either, Layer } from "effect";
import { AuthService, createAuthService } from "@/auth/service";
import { DatabaseService, getDatabase } from "@/db";
import { SettingsService, getSettings } from "@/settings";
import type { Result } from "./types";
export type { Result } from "./types";

export type AppServices = SettingsService | DatabaseService | AuthService;

/**
 * Runs an Effect that returns a Response object.
 * Use for auth flows that return HTTP responses (redirects, cookies, etc.).
 */
export async function runEffectResponse<E>(
  effect: Effect.Effect<Response, E, AppServices>,
): Promise<Response> {
  const settingsLayer = Layer.succeed(SettingsService, getSettings());

  const databaseUrl = process.env.DATABASE_URL;
  if (!databaseUrl) {
    throw new Error("DATABASE_URL environment variable is not set");
  }

  const database = getDatabase(databaseUrl);
  const databaseLayer = Layer.succeed(DatabaseService, database);
  const authLayer = Layer.succeed(AuthService, createAuthService());

  const appServicesLayer = Layer.mergeAll(
    settingsLayer,
    databaseLayer,
    authLayer,
  );

  try {
    return await effect.pipe(
      Effect.provide(appServicesLayer),
      Effect.runPromise,
    );
  } finally {
    await database.close();
  }
}

export async function runEffect<A, E extends { message: string }>(
  effect: Effect.Effect<A, E, AppServices>,
): Promise<Result<A>> {
  const settingsLayer = Layer.succeed(SettingsService, getSettings());

  const databaseUrl = process.env.DATABASE_URL;
  if (!databaseUrl) {
    return { success: false, error: "Database not configured" };
  }

  const database = getDatabase(databaseUrl);
  const databaseLayer = Layer.succeed(DatabaseService, database);
  const authLayer = Layer.succeed(AuthService, createAuthService());

  const appServicesLayer = Layer.mergeAll(
    settingsLayer,
    databaseLayer,
    authLayer,
  );

  try {
    const result = await effect.pipe(
      Effect.either,
      Effect.provide(appServicesLayer),
      Effect.runPromise,
    );

    if (Either.isRight(result)) {
      return { success: true, data: result.right };
    } else {
      return { success: false, error: result.left.message };
    }
  } finally {
    await database.close();
  }
}
