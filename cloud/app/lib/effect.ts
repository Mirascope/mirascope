import { Effect, Either, Layer } from "effect";
import { AuthService, createAuthService } from "@/auth/service";
import { Database } from "@/db";
import { SettingsService, getSettings } from "@/settings";
import type { Result } from "./types";
export type { Result } from "./types";

export type AppServices = SettingsService | Database | AuthService;

/**
 * Creates the application services layer with Database, Settings, and Auth.
 */
function createAppServicesLayer(databaseUrl: string) {
  const stripeApiKey = process.env.STRIPE_SECRET_KEY;
  if (!stripeApiKey) {
    throw new Error("STRIPE_SECRET_KEY environment variable is not set");
  }

  return Layer.mergeAll(
    Layer.succeed(SettingsService, getSettings()),
    Database.Live({
      database: { connectionString: databaseUrl },
      stripe: { apiKey: stripeApiKey },
    }).pipe(Layer.orDie),
    Layer.succeed(AuthService, createAuthService()),
  );
}

/**
 * Runs an effect with the application services layer and returns an Either result.
 */
async function runEffectWithServices<A, E>(
  effect: Effect.Effect<A, E, AppServices>,
  databaseUrl: string,
): Promise<Either.Either<A, E>> {
  const appServicesLayer = createAppServicesLayer(databaseUrl);
  return effect.pipe(
    Effect.either,
    Effect.provide(appServicesLayer),
    Effect.runPromise,
  );
}

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

  const result = await runEffectWithServices(effect, databaseUrl);

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

  const result = await runEffectWithServices(effect, databaseUrl);

  if (Either.isRight(result)) {
    return { success: true, data: result.right };
  } else {
    return { success: false, error: result.left.message };
  }
}
