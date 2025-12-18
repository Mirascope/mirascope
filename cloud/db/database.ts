/**
 * @fileoverview Effect-native database service layer.
 *
 * This module provides the `EffectDatabase` service which aggregates all
 * individual database services (`Users`, `Sessions`, etc.) and provides them
 * through Effect's dependency injection system.
 *
 * ## Usage
 *
 * ```ts
 * import { EffectDatabase } from "@/db/database";
 *
 * const createUser = Effect.gen(function* () {
 *   const db = yield* EffectDatabase;
 *
 *   const user = yield* db.users.create({
 *     data: { email: "user@example.com", name: "User" },
 *   });
 *
 *   return user;
 * });
 *
 * // Provide the EffectDatabase layer
 * createUser.pipe(Effect.provide(EffectDatabase.Live({ connectionString: "..." })));
 * ```
 *
 * ## Architecture
 *
 * ```
 * EffectDatabase (service layer)
 *   ├── users: Ready<Users>
 *   └── sessions: Ready<Sessions>
 *
 * Each service uses `yield* DrizzleORM` internally. The `makeReady` wrapper
 * provides the DrizzleORM client, so consumers see methods returning
 * Effect<T, E> with no additional dependencies.
 * ```
 *
 * NOTE: This is a transitional service that will eventually be renamed to `Database`
 * once the migration is complete.
 */

import { Context, Layer, Effect } from "effect";
import { type Ready, makeReady } from "@/db/base";
import { DrizzleORM, type DrizzleORMConfig } from "@/db/client";
import { Users } from "@/db/users";
import { Sessions } from "@/db/sessions";
import { Organizations } from "@/db/organizations";
import { OrganizationMemberships } from "@/db/organization-memberships";
import { ProjectMemberships } from "@/db/project-memberships";

/**
 * Type definition for the organizations service with nested memberships.
 *
 * Access pattern: `db.organizations.create(...)` or `db.organizations.memberships.create(...)`
 */
export interface EffectOrganizations extends Ready<Organizations> {
  readonly memberships: Ready<OrganizationMemberships>;
}

/**
 * Type definition for the projects service with nested memberships.
 *
 * Access pattern: `db.projects.memberships.create(...)`
 */
export interface EffectProjects {
  readonly memberships: Ready<ProjectMemberships>;
}

/**
 * Type definition for the EffectDatabase service.
 *
 * Each service is wrapped with `Ready` which removes the DrizzleORM
 * requirement from all methods. This means consumers only need to provide
 * EffectDatabase, not DrizzleORM.
 *
 * Adding a new method to a service class automatically adds it here via
 * the `Ready` type transformation. If the interface doesn't match
 * what's returned from `Default`, TypeScript will error.
 */
// TODO: remove "Effect" prefix after refactor is complete
export interface EffectDatabaseSchema {
  readonly users: Ready<Users>;
  readonly sessions: Ready<Sessions>;
  readonly organizations: EffectOrganizations;
  readonly projects: EffectProjects;
}

/**
 * Effect-native database service layer.
 *
 * Provides aggregated access to all database services through Effect's
 * dependency injection system. The DrizzleORM dependency is provided
 * internally, so consumers don't need to manage it.
 *
 * @example
 * ```ts
 * const program = Effect.gen(function* () {
 *   const db = yield* EffectDatabase;
 *
 *   // Create a user - no DrizzleORM requirement leaked!
 *   const user = yield* db.users.create({
 *     data: { email: "user@example.com" },
 *   });
 *
 *   return user;
 * });
 *
 * // Provide the EffectDatabase layer (includes DrizzleORM)
 * program.pipe(Effect.provide(EffectDatabase.Live({ connectionString: "..." })));
 * ```
 */
// TODO: remove "Effect" prefix after refactor is complete
export class EffectDatabase extends Context.Tag("EffectDatabase")<
  EffectDatabase,
  EffectDatabaseSchema
>() {
  /**
   * Default layer that creates the EffectDatabase service.
   *
   * Requires DrizzleORM to be provided. The `makeReady` wrapper provides
   * the DrizzleORM client to each service, removing it from method signatures.
   */
  static Default = Layer.effect(
    EffectDatabase,
    Effect.gen(function* () {
      const client = yield* DrizzleORM;

      // Create memberships services first, then pass to parent services
      const organizationMemberships = new OrganizationMemberships();
      const organizations = new Organizations(organizationMemberships);
      const projectMemberships = new ProjectMemberships(
        organizationMemberships,
      );

      return {
        users: makeReady(client, new Users()),
        sessions: makeReady(client, new Sessions()),
        organizations: {
          ...makeReady(client, organizations),
          memberships: makeReady(client, organizationMemberships),
        },
        projects: {
          memberships: makeReady(client, projectMemberships),
        },
      };
    }),
  );

  /**
   * Creates a fully configured layer with database connection.
   *
   * This is the standard way to use EffectDatabase. Provide a connection
   * configuration and get back a layer that provides both EffectDatabase
   * and its DrizzleORM dependency.
   *
   * @param config - Database connection configuration
   * @returns A Layer providing EffectDatabase with no dependencies
   *
   * @example
   * ```ts
   * const DbLive = EffectDatabase.Live({
   *   connectionString: process.env.DATABASE_URL,
   * });
   *
   * program.pipe(Effect.provide(DbLive));
   * ```
   */
  static Live = (config: DrizzleORMConfig) =>
    EffectDatabase.Default.pipe(Layer.provide(DrizzleORM.layer(config)));
}
