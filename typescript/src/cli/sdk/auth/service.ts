/**
 * @fileoverview AuthService — provides the API key for authenticated requests.
 */

import { Context, Effect, Layer } from "effect";

import { AuthError } from "../errors.js";
import { readCredentials, type Credentials } from "./config.js";

// ---------------------------------------------------------------------------
// Service interface
// ---------------------------------------------------------------------------

export interface AuthServiceInterface {
  readonly getToken: () => Effect.Effect<string, AuthError>;
  readonly getBaseUrl: () => Effect.Effect<string, AuthError>;
}

export class AuthService extends Context.Tag("AuthService")<
  AuthService,
  AuthServiceInterface
>() {
  /**
   * Create a layer from an explicit token string (for programmatic / CI use).
   */
  static fromToken = (token: string, baseUrl?: string) =>
    Layer.succeed(AuthService, {
      getToken: () => Effect.succeed(token),
      getBaseUrl: () => Effect.succeed(baseUrl ?? "https://mirascope.com"),
    });

  /**
   * Create a layer that reads from config file / env vars.
   */
  static fromConfig = () =>
    Layer.effect(
      AuthService,
      Effect.gen(function* () {
        // Eagerly read once to fail fast if no credentials
        const creds: Credentials = yield* readCredentials();
        return {
          getToken: () => Effect.succeed(creds.apiKey),
          getBaseUrl: () => Effect.succeed(creds.baseUrl),
        };
      }),
    );
}
