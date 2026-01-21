import { Effect, Either, Layer } from "effect";
import { AuthService, createAuthService } from "@/auth/service";
import { Database } from "@/db";
import { DrizzleORM } from "@/db/client";
import { Settings, type SettingsConfig } from "@/settings";
import { Emails } from "@/emails";
import {
  ExecutionContext,
  executionContextLayer,
  settingsLayer,
} from "@/server-entry";
import type { Result } from "./types";
export type { Result } from "./types";

export type AppServices =
  | Settings
  | Database
  | DrizzleORM
  | AuthService
  | Emails
  | ExecutionContext;

/**
 * Creates the application services layer with Database, Settings, Auth, Emails, and ExecutionContext.
 */
function createAppServicesLayer(settings: SettingsConfig) {
  return Layer.mergeAll(
    Layer.succeed(Settings, settings),
    Database.Live({
      database: { connectionString: settings.databaseUrl },
      payments: settings.stripe,
    }).pipe(Layer.orDie),
    Layer.succeed(AuthService, createAuthService()),
    Emails.Live(settings.resend),
    executionContextLayer,
  );
}

/**
 * Runs an effect with the application services layer and returns an Either result.
 */
async function runEffectWithServices<A, E>(
  effect: Effect.Effect<A, E, AppServices>,
  settings: SettingsConfig,
): Promise<Either.Either<A, E>> {
  const appServicesLayer = createAppServicesLayer(settings);
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
  // Get settings from the global layer (set by server-entry fetch handler)
  const settingsResult = await Effect.runPromise(
    Effect.gen(function* () {
      return yield* Settings;
    }).pipe(Effect.provide(settingsLayer), Effect.either),
  );

  if (Either.isLeft(settingsResult)) {
    // Settings validation failed - return error response
    const error = settingsResult.left;
    return Response.redirect(
      `http://localhost:3000/cloud/login?error=${encodeURIComponent(String(error))}`,
      302,
    );
  }

  const settings = settingsResult.right;
  const result = await runEffectWithServices(effect, settings);

  if (Either.isRight(result)) {
    return result.right;
  } else {
    // Return a proper error response instead of throwing
    const siteUrl = settings.siteUrl;
    return Response.redirect(
      `${siteUrl}/cloud/login?error=${encodeURIComponent(result.left.message)}`,
      302,
    );
  }
}

export async function runEffect<A, E extends { message: string }>(
  effect: Effect.Effect<A, E, AppServices>,
): Promise<Result<A>> {
  // Get settings from the global layer (set by server-entry fetch handler)
  const settingsResult = await Effect.runPromise(
    Effect.gen(function* () {
      return yield* Settings;
    }).pipe(Effect.provide(settingsLayer), Effect.either),
  );

  if (Either.isLeft(settingsResult)) {
    return { success: false, error: String(settingsResult.left) };
  }

  const settings = settingsResult.right;
  const result = await runEffectWithServices(effect, settings);

  if (Either.isRight(result)) {
    return { success: true, data: result.right };
  } else {
    return { success: false, error: result.left.message };
  }
}
