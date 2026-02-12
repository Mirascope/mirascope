/**
 * @fileoverview ClawApi — Effect service for managing hosted OpenClaw instances.
 */

import { Context, Effect, Layer, Schema } from "effect";

import { ApiError, AuthError, NotFoundError } from "../errors.js";
import { MirascopeHttp } from "../http/client.js";
import * as Schemas from "./schemas.js";

// Re-export for consumers
export type Claw = Schemas.Claw;
export type ClawDetail = Schemas.ClawDetail;

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

      return ClawApi.of({
        list: () => http.get("/claws", Schema.Array(Schemas.Claw)),

        create: (org, name, instanceType) =>
          http.post(
            "/claws",
            {
              organizationSlug: org,
              name,
              instanceType: instanceType ?? "standard",
            },
            Schemas.Claw,
          ),

        get: (id) =>
          http
            .get(`/claws/${id}`, Schemas.Claw)
            .pipe(Effect.catchTag("ApiError", mapNotFound(id))),

        status: (id) =>
          http
            .get(`/claws/${id}/status`, Schemas.ClawDetail)
            .pipe(Effect.catchTag("ApiError", mapNotFound(id))),

        delete: (id) =>
          http
            .del(`/claws/${id}`)
            .pipe(Effect.catchTag("ApiError", mapNotFound(id))),
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
            organizationSlug: org,
            slug: name,
            status: "provisioning" as const,
            instanceType: instanceType ?? "standard",
            createdAt: new Date().toISOString(),
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
                containerStatus: "running",
                uptime: 3600,
                lastSync: null,
                errorMessage: null,
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
