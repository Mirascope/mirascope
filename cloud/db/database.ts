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
import { type Ready, dependencyProvider } from "@/utils";
import { DrizzleORM, type DrizzleORMConfig } from "@/db/client";
import { Users } from "@/db/users";
import { Sessions } from "@/db/sessions";
import { Organizations } from "@/db/organizations";
import { OrganizationMemberships } from "@/db/organization-memberships";
import { OrganizationInvitations } from "@/db/organization-invitations";
import { Projects } from "@/db/projects";
import { ProjectMemberships } from "@/db/project-memberships";
import { Environments } from "@/db/environments";
import { ApiKeys } from "@/db/api-keys";
import { Traces } from "@/db/traces";
import { Functions } from "@/db/functions";
import { Annotations } from "@/db/annotations";
import { RouterRequests } from "@/db/router-requests";
import { Payments, type StripeConfig } from "@/payments";

/**
 * Type definition for the traces service with nested annotations.
 *
 * Access pattern: `db.organizations.projects.environments.traces.annotations.create(...)`
 */
export interface TracesService extends Ready<Traces> {
  readonly annotations: Ready<Annotations>;
}

/**
 * Type definition for the API keys service with nested router requests.
 *
 * Access pattern: `db.organizations.projects.environments.apiKeys.routerRequests.create(...)`
 */
export interface ApiKeysService extends Ready<ApiKeys> {
  readonly routerRequests: Ready<RouterRequests>;
}

/**
 * Type definition for the environments service with nested API keys, traces, and functions.
 *
 * Access pattern:
 * - API Keys: `db.organizations.projects.environments.apiKeys.create(...)`
 * - Router Requests: `db.organizations.projects.environments.apiKeys.routerRequests.create(...)`
 * - Traces: `db.organizations.projects.environments.traces.create(...)`
 * - Annotations: `db.organizations.projects.environments.traces.annotations.create(...)`
 * - Functions: `db.organizations.projects.environments.functions.create(...)`
 */
export interface EnvironmentsService extends Ready<Environments> {
  readonly apiKeys: ApiKeysService;
  readonly traces: TracesService;
  readonly functions: Ready<Functions>;
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
 * Type definition for the organizations service with nested memberships, invitations, and projects.
 *
 * Access pattern: `db.organizations.create(...)` or `db.organizations.memberships.create(...)`
 * Invitations: `db.organizations.invitations.create(...)`
 * Projects: `db.organizations.projects.create(...)` or `db.organizations.projects.memberships.create(...)`
 */
export interface OrganizationsService extends Ready<Organizations> {
  readonly memberships: Ready<OrganizationMemberships>;
  readonly invitations: Ready<OrganizationInvitations>;
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
   * Requires DrizzleORM and Payments to be provided. The dependency provider
   * automatically provides these dependencies to services, removing them from
   * method signatures.
   */
  static Default = Layer.effect(
    Database,
    Effect.gen(function* () {
      const client = yield* DrizzleORM;
      const payments = yield* Payments;
      const provideDependencies = dependencyProvider([
        { tag: DrizzleORM, instance: client },
        { tag: Payments, instance: payments },
      ]);

      // Create services with shared dependencies
      const users = new Users();
      const organizationMemberships = new OrganizationMemberships();
      const organizationInvitations = new OrganizationInvitations(
        organizationMemberships,
        users,
      );
      const organizations = new Organizations(organizationMemberships);
      const projectMemberships = new ProjectMemberships(
        organizationMemberships,
      );
      const projects = new Projects(
        organizationMemberships,
        projectMemberships,
      );
      const environments = new Environments(projectMemberships);
      const apiKeys = new ApiKeys(projectMemberships);
      const traces = new Traces(projectMemberships);
      const functions = new Functions(projectMemberships);
      const annotations = new Annotations(projectMemberships);
      const routerRequests = new RouterRequests(projectMemberships);

      return {
        users: provideDependencies(users),
        sessions: provideDependencies(new Sessions()),
        organizations: {
          ...provideDependencies(organizations),
          memberships: provideDependencies(organizationMemberships),
          invitations: provideDependencies(organizationInvitations),
          projects: {
            ...provideDependencies(projects),
            memberships: provideDependencies(projectMemberships),
            environments: {
              ...provideDependencies(environments),
              apiKeys: {
                ...provideDependencies(apiKeys),
                routerRequests: provideDependencies(routerRequests),
              },
              traces: {
                ...provideDependencies(traces),
                annotations: provideDependencies(annotations),
              },
              functions: provideDependencies(functions),
            },
          },
        },
      };
    }),
  );

  /**
   * Creates a fully configured layer with database and Payments connections.
   *
   * This is the standard way to use Database. Provide database and Payments
   * configurations and get back a layer that provides both Database and Payments
   * services with no dependencies.
   *
   * @param config - Database and Payments configuration
   * @returns A Layer providing both Database and Payments with no dependencies
   *
   * @example
   * ```ts
   * const DatabaseLive = Database.Live({
   *   database: { connectionString: process.env.DATABASE_URL },
   *   payments: {
   *     apiKey: process.env.STRIPE_SECRET_KEY,
   *     routerPriceId: process.env.STRIPE_ROUTER_PRICE_ID,
   *     // ... other fields from process.env
   *   },
   * });
   *
   * program.pipe(Effect.provide(DatabaseLive));
   * ```
   */
  static Live = (config: {
    database: DrizzleORMConfig;
    payments: Partial<StripeConfig>;
  }) => {
    const drizzleLayer = DrizzleORM.layer(config.database);

    const paymentsLayer = Payments.Live(config.payments).pipe(
      Layer.provide(drizzleLayer),
    );

    const databaseLayer = Database.Default.pipe(
      Layer.provideMerge(Layer.mergeAll(drizzleLayer, paymentsLayer)),
    );

    return Layer.mergeAll(drizzleLayer, paymentsLayer, databaseLayer);
  };
}
