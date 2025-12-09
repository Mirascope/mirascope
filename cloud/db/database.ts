/**
 * @fileoverview Database service layer.
 *
 * This module provides the `Database` service which aggregates all
 * individual database services (`Users`, `Sessions`, etc.) and provides them
 * through Effect's dependency injection system.
 *
 * ## Usage
 *
 * ```ts
 * import { Database } from "@/db/database";
 *
 * const createUser = Effect.gen(function* () {
 *   const db = yield* Database;
 *
 *   const user = yield* db.users.create({
 *     data: { email: "user@example.com", name: "User" },
 *   });
 *
 *   return user;
 * });
 *
 * // Provide the Database layer
 * createUser.pipe(Effect.provide(Database.Live({ connectionString: "..." })));
 * ```
 *
 * ## Architecture
 *
 * ```
 * Database (service layer)
 *   ├── users: Ready<Users>
 *   └── sessions: Ready<Sessions>
 *
 * Each service uses `yield* DrizzleORM` internally. The `makeReady` wrapper
 * provides the DrizzleORM client, so consumers see methods returning
 * Effect<T, E> with no additional dependencies.
 * ```
 */

import { Context, Layer, Effect } from "effect";
import { type Ready, makeReady } from "@/db/base";
import { DrizzleORM, type DrizzleORMConfig } from "@/db/client";
import { Users } from "@/db/users";
import { Sessions } from "@/db/sessions";
import { Organizations } from "@/db/organizations";
import { OrganizationMemberships } from "@/db/organization-memberships";
import { Projects } from "@/db/projects";
import { ProjectMemberships } from "@/db/project-memberships";
import { Environments } from "@/db/environments";
import { ApiKeys } from "@/db/api-keys";
import { Traces } from "@/db/traces";

/**
 * Type definition for the environments service with nested API keys and traces.
 *
 * Access pattern: `db.organizations.projects.environments.apiKeys.create(...)`
 * Traces: `db.organizations.projects.environments.traces.create(...)`
 */
export interface EnvironmentsService extends Ready<Environments> {
  readonly apiKeys: Ready<ApiKeys>;
  readonly traces: Ready<Traces>;
}

/**
 * Type definition for the projects service with nested memberships and environments.
 *
 * Access pattern: `db.organizations.projects.create(...)` or `db.organizations.projects.memberships.create(...)`
 * Environments: `db.organizations.projects.environments.create(...)`
 * API Keys: `db.organizations.projects.environments.apiKeys.create(...)`
 */
export interface ProjectsService extends Ready<Projects> {
  readonly memberships: Ready<ProjectMemberships>;
  readonly environments: EnvironmentsService;
}

/**
 * Type definition for the organizations service with nested memberships and projects.
 *
 * Access pattern: `db.organizations.create(...)` or `db.organizations.memberships.create(...)`
 * Projects: `db.organizations.projects.create(...)` or `db.organizations.projects.memberships.create(...)`
 */
export interface OrganizationsService extends Ready<Organizations> {
  readonly memberships: Ready<OrganizationMemberships>;
  readonly projects: ProjectsService;
}

/**
 * Database service layer.
 *
 * Provides aggregated access to all database services through Effect's
 * dependency injection system. The DrizzleORM dependency is provided
 * internally, so consumers don't need to manage it.
 *
 * @example
 * ```ts
 * const program = Effect.gen(function* () {
 *   const db = yield* Database;
 *
 *   // Create a user - no DrizzleORM requirement leaked!
 *   const user = yield* db.users.create({
 *     data: { email: "user@example.com" },
 *   });
 *
 *   return user;
 * });
 *
 * // Provide the Database layer (includes DrizzleORM)
 * program.pipe(Effect.provide(Database.Live({ connectionString: "..." })));
 * ```
 */
export class Database extends Context.Tag("Database")<
  Database,
  {
    readonly users: Ready<Users>;
    readonly sessions: Ready<Sessions>;
    readonly organizations: OrganizationsService;
  }
>() {
  /**
   * Default layer that creates the Database service.
   *
   * Requires DrizzleORM to be provided. The `makeReady` wrapper provides
   * the DrizzleORM client to each service, removing it from method signatures.
   */
  static Default = Layer.effect(
    Database,
    Effect.gen(function* () {
      const client = yield* DrizzleORM;

      // Create services with shared dependencies
      const organizationMemberships = new OrganizationMemberships();
      const organizations = new Organizations(organizationMemberships);
      const projectMemberships = new ProjectMemberships(
        organizationMemberships,
      );
      const projectsService = new Projects(
        organizationMemberships,
        projectMemberships,
      );
      const environmentsService = new Environments(projectMemberships);
      const apiKeysService = new ApiKeys(projectMemberships);

      const tracesService = new Traces(projectMemberships);

      const readyTraces = makeReady(client, tracesService);

      return {
        users: makeReady(client, new Users()),
        sessions: makeReady(client, new Sessions()),
        organizations: {
          ...makeReady(client, organizations),
          memberships: makeReady(client, organizationMemberships),
          projects: {
            ...makeReady(client, projectsService),
            memberships: makeReady(client, projectMemberships),
            environments: {
              ...makeReady(client, environmentsService),
              apiKeys: makeReady(client, apiKeysService),
              traces: readyTraces,
            },
          },
        },
      };
    }),
  );

  /**
   * Creates a fully configured layer with database connection.
   *
   * This is the standard way to use Database. Provide a connection
   * configuration and get back a layer that provides both Database
   * and its DrizzleORM dependency.
   *
   * @param config - Database connection configuration
   * @returns A Layer providing Database with no dependencies
   *
   * @example
   * ```ts
   * const DbLive = Database.Live({
   *   connectionString: process.env.DATABASE_URL,
   * });
   *
   * program.pipe(Effect.provide(DbLive));
   * ```
   */
  static Live = (config: DrizzleORMConfig) =>
    Database.Default.pipe(Layer.provide(DrizzleORM.layer(config)));
}
