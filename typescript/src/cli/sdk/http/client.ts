/**
 * @fileoverview MirascopeHttp — Effect-native HTTP client with auth injection.
 */

import { Context, Effect, Layer, Schema } from "effect";

import { AuthService } from "../auth/service.js";
import { ApiError, AuthError } from "../errors.js";

// ---------------------------------------------------------------------------
// Service interface
// ---------------------------------------------------------------------------

export interface MirascopeHttpInterface {
  readonly get: <A, I, R>(
    path: string,
    schema: Schema.Schema<A, I, R>,
  ) => Effect.Effect<A, ApiError | AuthError, R>;

  readonly post: <A, I, R>(
    path: string,
    body: unknown,
    schema: Schema.Schema<A, I, R>,
  ) => Effect.Effect<A, ApiError | AuthError, R>;

  readonly del: (path: string) => Effect.Effect<void, ApiError | AuthError>;
}

export class MirascopeHttp extends Context.Tag("MirascopeHttp")<
  MirascopeHttp,
  MirascopeHttpInterface
>() {
  static Live = Layer.effect(
    MirascopeHttp,
    Effect.gen(function* () {
      const auth = yield* AuthService;
      const token = yield* auth.getToken();
      const baseUrl = yield* auth.getBaseUrl();

      const request = <A, I, R>(
        method: string,
        path: string,
        schema: Schema.Schema<A, I, R> | null,
        body?: unknown,
      ): Effect.Effect<A, ApiError | AuthError, R> =>
        Effect.gen(function* () {
          const url = `${baseUrl}/api${path}`;
          const headers: Record<string, string> = {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          };

          const response = yield* Effect.tryPromise({
            try: () =>
              fetch(url, {
                method,
                headers,
                ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
              }),
            catch: (e) =>
              new ApiError({
                message: `Request failed: ${e instanceof Error ? e.message : String(e)}`,
                status: 0,
              }),
          });

          if (!response.ok) {
            const text = yield* Effect.tryPromise({
              try: () => response.text(),
              catch: () =>
                new ApiError({
                  message: `HTTP ${response.status}`,
                  status: response.status,
                }),
            });

            let message: string;
            try {
              const json = JSON.parse(text) as { message?: string };
              message = json.message ?? text;
            } catch {
              message = text;
            }

            return yield* Effect.fail(
              new ApiError({ message, status: response.status }),
            );
          }

          if (!schema) {
            return undefined as unknown as A;
          }

          const json = yield* Effect.tryPromise({
            try: () => response.json() as Promise<unknown>,
            catch: () =>
              new ApiError({
                message: "Failed to parse response JSON",
                status: response.status,
              }),
          });

          return yield* Schema.decodeUnknown(schema)(json).pipe(
            Effect.mapError(
              () =>
                new ApiError({
                  message: "Response did not match expected schema",
                  status: response.status,
                }),
            ),
          );
        });

      return {
        get: <A, I, R>(path: string, schema: Schema.Schema<A, I, R>) =>
          request("GET", path, schema),
        post: <A, I, R>(
          path: string,
          body: unknown,
          schema: Schema.Schema<A, I, R>,
        ) => request("POST", path, schema, body),
        del: (path: string) =>
          request("DELETE", path, null) as Effect.Effect<
            void,
            ApiError | AuthError
          >,
      };
    }),
  );
}
