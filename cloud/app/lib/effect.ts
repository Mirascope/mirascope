import { Effect, Either, Layer } from "effect";
import { AuthService, createAuthService } from "@/auth/service";
import { Database } from "@/db";
import { SettingsService, getSettings } from "@/settings";
import type { Result } from "./types";
export type { Result } from "./types";

export type AppServices = SettingsService | Database | AuthService;

/**
 * Runs an Effect that returns a Response object.
 * Use for auth flows that return HTTP responses (redirects, cookies, etc.).
 */
export async function runEffectResponse<E extends { message: string }>(
  effect: Effect.Effect<Response, E, AppServices>,
): Promise<Response> {
  const databaseUrl = process.env.DATABASE_URL;
  if (!databaseUrl) {
    throw new Error("DATABASE_URL environment variable is not set");
  }

  const appServicesLayer = Layer.mergeAll(
    Layer.succeed(SettingsService, getSettings()),
    Database.Live({ connectionString: databaseUrl }).pipe(Layer.orDie),
    Layer.succeed(AuthService, createAuthService()),
  );

  const result = await effect.pipe(
    Effect.either,
    Effect.provide(appServicesLayer),
    Effect.runPromise,
  );

  if (Either.isRight(result)) {
    return result.right;
  } else {
    // Return a proper error response instead of throwing
    const settings = getSettings();
    const siteUrl = settings.SITE_URL || "http://localhost:3000";
    return Response.redirect(
      `${siteUrl}/login?error=${encodeURIComponent(result.left.message)}`,
      302,
    );
  }
}

export async function runEffect<A, E extends { message: string }>(
  effect: Effect.Effect<A, E, AppServices>,
): Promise<Result<A>> {
  const databaseUrl = process.env.DATABASE_URL;
  if (!databaseUrl) {
    return { success: false, error: "Database not configured" };
  }

  const appServicesLayer = Layer.mergeAll(
    Layer.succeed(SettingsService, getSettings()),
    Database.Live({ connectionString: databaseUrl }).pipe(Layer.orDie),
    Layer.succeed(AuthService, createAuthService()),
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
}
