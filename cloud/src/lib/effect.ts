import { Effect, Either, Layer } from "effect";
import { getRequest } from "@tanstack/react-start/server";
import { AuthService, createAuthService } from "@/auth/service";
import { AuthenticatedUser } from "@/auth/context";
import { getAuthenticatedUser } from "@/auth/utils";
import { DatabaseService, getDatabase } from "@/db";
import { EnvironmentService, getEnvironment } from "@/environment";
import type { Result } from "./types";
export type { Result } from "./types";

export type AppServices = EnvironmentService | DatabaseService | AuthService;

/**
 * Runs an Effect that returns a Response object.
 * Use for auth flows that return HTTP responses (redirects, cookies, etc.).
 */
export async function runEffectResponse<E>(
  effect: Effect.Effect<Response, E, AppServices>,
): Promise<Response> {
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
  const environmentLayer = Layer.succeed(EnvironmentService, getEnvironment());

  const databaseUrl = process.env.DATABASE_URL;
  if (!databaseUrl) {
    return { success: false, error: "Database not configured" };
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

export async function runAuthenticatedEffect<A, E extends { message: string }>(
  effect: Effect.Effect<A, E, AppServices | AuthenticatedUser>,
): Promise<Result<A>> {
  const request = getRequest();
  if (!request) {
    return { success: false, error: "No request available" };
  }

  const environmentLayer = Layer.succeed(EnvironmentService, getEnvironment());

  const databaseUrl = process.env.DATABASE_URL;
  if (!databaseUrl) {
    return { success: false, error: "Database not configured" };
  }

  const database = getDatabase(databaseUrl);
  const databaseLayer = Layer.succeed(DatabaseService, database);
  const authLayer = Layer.succeed(AuthService, createAuthService());

  const baseServicesLayer = Layer.mergeAll(
    environmentLayer,
    databaseLayer,
    authLayer,
  );

  try {
    const user = await Effect.runPromise(
      getAuthenticatedUser(request).pipe(Effect.provide(databaseLayer)),
    );

    if (!user) {
      return { success: false, error: "Not authenticated" };
    }

    const authenticatedUserLayer = Layer.succeed(AuthenticatedUser, user);
    const appServicesLayer = Layer.mergeAll(
      baseServicesLayer,
      authenticatedUserLayer,
    );

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
