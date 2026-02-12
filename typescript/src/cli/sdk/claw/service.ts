/**
 * @fileoverview ClawApi — Effect service for managing hosted OpenClaw instances.
 *
 * The Live implementation:
 * 1. Calls /api/v1/auth/me to discover the org ID from the API key
 * 2. Calls /api/v2/organizations/:orgId/claws/* for CRUD operations
 */

import { Context, Effect, Layer, Schema } from "effect";

import { ApiError, AuthError, NotFoundError } from "../errors.js";
import { MirascopeHttp } from "../http/client.js";
import * as Schemas from "./schemas.js";

// Re-export for consumers
export type Claw = Schemas.Claw;
export type ClawDetail = Schemas.ClawDetail;

// ---------------------------------------------------------------------------
// Auth/me response schema
// ---------------------------------------------------------------------------

const AuthMeResponse = Schema.Struct({
  user: Schema.Struct({
    id: Schema.String,
    email: Schema.String,
    name: Schema.NullOr(Schema.String),
  }),
  apiKey: Schema.Struct({
    id: Schema.String,
    organizationId: Schema.String,
    environmentId: Schema.NullOr(Schema.String),
    projectId: Schema.NullOr(Schema.String),
  }),
});

// ---------------------------------------------------------------------------
// Helper: map 404 to NotFoundError
// ---------------------------------------------------------------------------

const mapNotFound =
  (id: string) =>
  (e: ApiError): Effect.Effect<never, ApiError | NotFoundError> =>
    e.status === 404
      ? Effect.fail(
          new NotFoundError({
            message: "Claw not found",
            resource: "Claw",
            id,
          }),
        )
      : Effect.fail(e);

// ---------------------------------------------------------------------------
// Service
// ---------------------------------------------------------------------------

export class ClawApi extends Context.Tag("ClawApi")<
  ClawApi,
  {
    readonly list: () => Effect.Effect<
      ReadonlyArray<Schemas.Claw>,
      ApiError | AuthError
    >;
    readonly create: (
      org: string,
      name: string,
      instanceType?: string,
    ) => Effect.Effect<Schemas.Claw, ApiError | AuthError>;
    readonly get: (
      id: string,
    ) => Effect.Effect<Schemas.Claw, ApiError | AuthError | NotFoundError>;
    readonly status: (
      id: string,
    ) => Effect.Effect<
      Schemas.ClawDetail,
      ApiError | AuthError | NotFoundError
    >;
    readonly delete: (
      id: string,
    ) => Effect.Effect<void, ApiError | AuthError | NotFoundError>;
  }
>() {
  static Live = Layer.effect(
    ClawApi,
    Effect.gen(function* () {
      const http = yield* MirascopeHttp;

      // Discover org ID from API key on first use (cached)
      let cachedOrgId: string | null = null;
      const getOrgId = () =>
        Effect.gen(function* () {
          if (cachedOrgId) return cachedOrgId;
          const me = yield* http.get("/v1/auth/me", AuthMeResponse);
          cachedOrgId = me.apiKey.organizationId;
          return cachedOrgId;
        });

      const orgPath = (suffix: string) =>
        Effect.map(
          getOrgId(),
          (orgId) => `/v2/organizations/${orgId}/claws${suffix}`,
        );

      return ClawApi.of({
        list: () =>
          Effect.gen(function* () {
            const path = yield* orgPath("");
            return yield* http.get(path, Schema.Array(Schemas.Claw));
          }),

        create: (org, name, instanceType) =>
          Effect.gen(function* () {
            const path = yield* orgPath("");
            return yield* http.post(
              path,
              {
                slug: name,
                name,
                instanceType: instanceType ?? "standard-1",
              },
              Schemas.Claw,
            );
          }),

        get: (id) =>
          Effect.gen(function* () {
            const path = yield* orgPath(`/${id}`);
            return yield* http
              .get(path, Schemas.Claw)
              .pipe(Effect.catchTag("ApiError", mapNotFound(id)));
          }),

        status: (id) =>
          Effect.gen(function* () {
            const path = yield* orgPath(`/${id}`);
            return yield* http
              .get(path, Schemas.ClawDetail)
              .pipe(Effect.catchTag("ApiError", mapNotFound(id)));
          }),

        delete: (id) =>
          Effect.gen(function* () {
            const path = yield* orgPath(`/${id}`);
            return yield* http
              .del(path)
              .pipe(Effect.catchTag("ApiError", mapNotFound(id)));
          }),
      });
    }),
  );

  static Mock = (claws: Schemas.Claw[] = []) =>
    Layer.succeed(
      ClawApi,
      ClawApi.of({
        list: () => Effect.succeed(claws),
        create: (org, name, instanceType) =>
          Effect.succeed({
            id: "mock-id",
            organizationId: "mock-org-id",
            slug: name,
            displayName: name,
            status: "provisioning" as const,
            instanceType: instanceType ?? "standard",
            createdAt: "2026-02-12T00:00:00Z",
          }),
        get: (id) => {
          const found = claws.find((c) => c.id === id);
          return found
            ? Effect.succeed(found)
            : Effect.fail(
                new NotFoundError({
                  message: "Not found",
                  resource: "Claw",
                  id,
                }),
              );
        },
        status: (id) => {
          const found = claws.find((c) => c.id === id);
          return found
            ? Effect.succeed({
                ...found,
                lastError: null,
                lastDeployedAt: null,
              })
            : Effect.fail(
                new NotFoundError({
                  message: "Not found",
                  resource: "Claw",
                  id,
                }),
              );
        },
        delete: (id) => {
          const found = claws.find((c) => c.id === id);
          return found
            ? Effect.void
            : Effect.fail(
                new NotFoundError({
                  message: "Not found",
                  resource: "Claw",
                  id,
                }),
              );
        },
      }),
    );
}
